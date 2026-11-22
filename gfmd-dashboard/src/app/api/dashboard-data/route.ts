import { NextResponse } from 'next/server';
import { MongoClient, ObjectId } from 'mongodb';

// MongoDB connection - using same credentials as Railway deployment
const MONGODB_URI = process.env.MONGODB_CONNECTION_STRING || process.env.MONGODB_URI || '';

interface SequenceData {
  _id: string;
  contact_email: string;
  contact_id: string;
  current_step: number;
  status: string;
  emails_sent: Array<{
    step: number;
    sent_at: string;
    subject: string;
    actually_sent: boolean;
  }>;
  created_at: string;
  updated_at: string;
}

interface ContactData {
  _id: string;
  name: string;
  email: string;
  organization: string;
  title: string;
  location?: string;
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const campaign = searchParams.get('campaign');

    // Build campaign filter (empty = all campaigns).
    // narc_gone is the legacy default: those docs predate the multi-campaign
    // migration and have NO `campaign` field, so filtering on {campaign:'narc_gone'}
    // would match zero docs and blank the dashboard. Treat a missing field as narc_gone.
    let campaignFilter: Record<string, unknown> = {};
    if (campaign === 'narc_gone') {
      campaignFilter = { $or: [{ campaign: 'narc_gone' }, { campaign: { $exists: false } }, { campaign: null }] };
    } else if (campaign) {
      campaignFilter = { campaign };
    }

    // Connect to MongoDB (same database as your Railway automation)
    const client = new MongoClient(MONGODB_URI);
    await client.connect();

    const db = client.db('gfmd_narc_gone');
    const sequencesCollection = db.collection('email_sequences');
    const contactsCollection = db.collection('contacts');
    const suppressionCollection = db.collection('suppression_list');
    const interactionsCollection = db.collection('interactions');

    // Get sequence statistics filtered by campaign
    const totalSequences = await sequencesCollection.countDocuments(campaignFilter);
    const activeSequences = await sequencesCollection.countDocuments({ status: 'active', ...campaignFilter });
    const completedSequences = await sequencesCollection.countDocuments({ status: 'completed', ...campaignFilter });

    // Get bounce and suppression metrics, scoped to the campaign.
    // suppression_list has no campaign field, so when a campaign is selected we
    // intersect with that campaign's own contact emails. Without this, every
    // campaign page showed the GLOBAL suppression/bounce totals (e.g. spectrum
    // displaying narc_gone's ~768 bounces).
    let suppressionEmailFilter: Record<string, unknown> = {};
    if (campaign) {
      const campaignEmails = (await sequencesCollection.distinct('contact_email', campaignFilter))
        .filter(Boolean)
        .map((e: string) => e.toLowerCase());
      suppressionEmailFilter = { email: { $in: campaignEmails } };
    }
    const totalSuppressed = await suppressionCollection.countDocuments({
      status: 'active',
      ...suppressionEmailFilter,
    });
    const bouncedEmails = await suppressionCollection.countDocuments({
      status: 'active',
      reason: { $regex: 'delivery failed|address not found|bounce', $options: 'i' },
      ...suppressionEmailFilter,
    });

    // Get total contacts made (emails sent)
    const totalEmailsSent = await sequencesCollection.aggregate([
      { $match: campaignFilter },
      { $unwind: '$emails_sent' },
      { $match: { 'emails_sent.actually_sent': true } },
      { $group: { _id: null, totalSent: { $sum: 1 }, latestSentAt: { $max: '$emails_sent.sent_at' } } }
    ]).toArray();
    const emailsSentCount = totalEmailsSent.length > 0 ? totalEmailsSent[0].totalSent : 0;

    // Get unique contacts who have replied (excluding bounces/system messages).
    // interactions docs carry no `campaign` field, so we can't filter them by
    // campaign directly (doing so matched 0 and zeroed the reply metrics). And
    // sender_email is stored mixed-case while contact_email is lowercase, so we
    // can't $in-match either. Pull all real repliers, then intersect by
    // lowercased email against the campaign's sequence contacts in JS.
    const replyFilter: Record<string, unknown> = {
      type: { $in: ['auto_reply', 'ai_reply_review', 'spectrum_reply_review'] },
      sender_email: {
        $not: { $regex: 'postmaster|mailer-daemon|mail-daemon|noreply|no-reply|donotreply', $options: 'i' }
      }
    };
    // Human replies live under two interaction types: 'auto_reply' (historical,
    // before the escalation feature) and 'escalation' (current -- genuine human
    // replies now forwarded to Lisa instead of AI-answered). Count unique real
    // people across BOTH so the reply metric keeps growing after the switch.
    const escalationFilter: Record<string, unknown> = {
      type: 'escalation',
      sender_email: {
        $not: { $regex: 'postmaster|mailer-daemon|mail-daemon|noreply|no-reply|donotreply', $options: 'i' }
      }
    };
    const escalationSenders = (await interactionsCollection.distinct('sender_email', escalationFilter))
      .filter((e): e is string => typeof e === 'string');

    let allRepliers = (await interactionsCollection.distinct('sender_email', replyFilter))
      .filter((e): e is string => typeof e === 'string')
      .concat(escalationSenders);
    let uniqueEscalated = escalationSenders;

    if (campaign) {
      const campaignEmails = new Set(
        (await sequencesCollection.distinct('contact_email', campaignFilter))
          .filter((e): e is string => typeof e === 'string')
          .map(e => e.toLowerCase().trim())
      );
      allRepliers = allRepliers.filter(e => campaignEmails.has(e.toLowerCase().trim()));
      uniqueEscalated = escalationSenders.filter(e => campaignEmails.has(e.toLowerCase().trim()));
    }
    allRepliers = allRepliers.concat(
      (await sequencesCollection.distinct('contact_email', { ...campaignFilter, status: 'replied' }))
        .filter((email): email is string => typeof email === 'string')
    );
    // Dedupe (a contact may appear in several reply records)
    const replyCount = new Set(allRepliers.map(e => e.toLowerCase().trim())).size;
    const escalatedToLisa = new Set(uniqueEscalated.map(e => e.toLowerCase().trim())).size;

    // Reply rate: unique repliers / total sequences contacted
    const replyRate = totalSequences > 0 ? ((replyCount / totalSequences) * 100) : 0;
    
    // Get recent sequences for activity table
    const recentSequences = await sequencesCollection
      .find(campaignFilter)
      .sort({ last_email_sent: -1, updated_at: -1 })
      .limit(10)
      .toArray() as unknown as SequenceData[];
    
    // Get contact details for recent sequences
    const contactIds = recentSequences.map(seq => seq.contact_id);
    const objectIds = contactIds.map(id => {
      try {
        return new ObjectId(id);
      } catch {
        return null;
      }
    }).filter(id => id !== null) as ObjectId[];
    
    const contacts = await contactsCollection
      .find({ _id: { $in: objectIds } })
      .toArray() as unknown as ContactData[];
    
    // Create contact lookup map
    const contactMap = new Map();
    contacts.forEach(contact => {
      contactMap.set(contact._id.toString(), contact);
    });
    
    // Get email performance data (last 7 days) - REAL DATA from interactions
    const emailPerformance = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const startOfDay = new Date(dateStr + 'T00:00:00.000Z');
      const endOfDay = new Date(dateStr + 'T23:59:59.999Z');

      // Count emails sent on this date from sequences
      const sentResult = await sequencesCollection.aggregate([
        { $match: campaignFilter }, { $unwind: '$emails_sent' },
        { $match: { 'emails_sent.actually_sent': true, 'emails_sent.sent_at': {
          $gte: dateStr + 'T00:00:00', $lt: dateStr + 'T23:59:59'
        } } }, { $count: 'count' }
      ]).toArray();
      const sent = sentResult[0]?.count || 0;

      // Human replies detected on this date: auto_reply (historical) +
      // escalation (current). Open tracking was removed -- the pixel never
      // recorded opens, so it always read 0.
      const replies = await interactionsCollection.countDocuments({
        type: { $in: ['auto_reply', 'escalation', 'ai_reply_review', 'spectrum_reply_review'] },
        ...(campaign ? { sender_email: { $in: allRepliers } } : {}),
        timestamp: { $gte: startOfDay.toISOString(), $lt: endOfDay.toISOString() },
        ...(!campaign ? { sender_email: {
          $not: { $regex: 'postmaster|mailer-daemon|mail-daemon', $options: 'i' }
        } } : {})
      });

      emailPerformance.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        sent,
        replies
      });
    }
    
    // Calculate step distribution for pipeline visualization
    const stepDistribution = await sequencesCollection.aggregate([
      { $match: { status: 'active', ...campaignFilter } },
      { $group: { _id: '$current_step', count: { $sum: 1 } } },
      { $sort: { _id: 1 } }
    ]).toArray();
    
    // Create lead activity data
    const leadActivity = recentSequences.slice(0, 5).map(sequence => {
      const contact = contactMap.get(sequence.contact_id) || {};
      const lastEmail = sequence.emails_sent.filter(email => email.actually_sent === true).at(-1);

      // Calculate time since last email in hours
      let lastContact = 'Never';
      if (lastEmail) {
        const hoursSinceLastEmail = Math.floor(
          (Date.now() - new Date(lastEmail.sent_at).getTime()) / (1000 * 60 * 60)
        );
        if (hoursSinceLastEmail < 24) {
          lastContact = `${hoursSinceLastEmail} ${hoursSinceLastEmail === 1 ? 'hour' : 'hours'} ago`;
        } else {
          const days = Math.floor(hoursSinceLastEmail / 24);
          lastContact = `${days} ${days === 1 ? 'day' : 'days'} ago`;
        }
      }

      // Get step info - total steps depends on campaign: centrifuge is a
      // 5-step sequence, narc_gone (legacy/default) is 6 steps. Hardcoding 5
      // produced "Step 6 of 5" on the narc_gone page.
      const totalSteps = campaign === 'spectrum' ? 8 : campaign === 'centrifuge' ? 5 : 6;
      const currentStep = sequence.current_step;
      const stage = `Step ${currentStep} of ${totalSteps}`;

      return {
        name: contact.name || sequence.contact_email.split('@')[0],
        organization: contact.organization || 'Unknown',
        stage,
        lastContact,
        status: sequence.status === 'replied' ? 'Engaged' :
                sequence.status === 'completed' ? 'Completed' : sequence.status === 'suppressed' ? 'Suppressed' : 'Waiting',
        contactEmail: sequence.contact_email,
        contactId: sequence.contact_id
      };
    });
    
    await client.close();

    let automationRunning = false;
    let statusLabel = 'Worker status unavailable';
    try {
      const response = await fetch('https://gfmd-email-automation-production.up.railway.app/health', {
        cache: 'no-store', signal: AbortSignal.timeout(5000)
      });
      const worker = await response.json();
      if (worker.integrations) {
        automationRunning = response.ok && worker.automation?.status === 'running' && worker.integrations.ready === true;
        statusLabel = !worker.integrations.ready ? 'Integration checks failed' :
          worker.automation?.status === 'running' ? (worker.sending_enabled ? 'Running' : 'Monitoring; sending disabled') :
          worker.automation?.status === 'disabled' ? 'Automation disabled' : 'Automation needs attention';
      }
    } catch { /* Unverified worker status must not appear active. */ }

    // Return REAL data from your GFMD system.
    // Open rate and revenue were removed: the tracking pixel never recorded
    // opens (always 0) and there is no orders/revenue data source.
    const dashboardData = {
      convertedLeads: replyCount,
      replyRate: parseFloat(replyRate.toFixed(1)),
      replyCount: replyCount,
      escalatedToLisa,

      // Email metrics
      totalEmailsSent: emailsSentCount,
      latestSuccessfulSend: totalEmailsSent[0]?.latestSentAt || null,
      bouncedEmails,
      totalSuppressed,

      totalSequences,
      activeSequences,
      completedSequences,
      emailPerformance,
      leadActivity,
      stepDistribution,
      systemStatus: {
        automationRunning,
        statusLabel,
        lastContactAddition: null,
        nextScheduledRun: null
      }
    };
    
    return NextResponse.json(dashboardData);
    
  } catch (error) {
    console.error('Dashboard API Error:', error);

    // Return error state with empty data - no fake data
    const errorData = {
      convertedLeads: 0,
      replyRate: 0,
      replyCount: 0,
      escalatedToLisa: 0,
      totalSequences: 0,
      activeSequences: 0,
      completedSequences: 0,
      totalEmailsSent: 0,
      bouncedEmails: 0,
      totalSuppressed: 0,
      emailPerformance: [],
      leadActivity: [],
      stepDistribution: [],
      systemStatus: {
        automationRunning: false,
        lastContactAddition: null,
        nextScheduledRun: null
      },
      connectionError: true,
      errorMessage: 'Database connection failed - please check configuration'
    };

    return NextResponse.json(errorData, { status: 500 });
  }
}
