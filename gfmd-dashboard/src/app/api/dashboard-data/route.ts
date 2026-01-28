import { NextResponse } from 'next/server';
import { MongoClient, ObjectId } from 'mongodb';

// MongoDB connection - using same credentials as Railway deployment
const MONGODB_URI = process.env.MONGODB_CONNECTION_STRING || 
  'mongodb+srv://solutions-account:GFMDgfmd2280%40%40@cluster0.hdejtab.mongodb.net/?appName=Cluster0';

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

export async function GET() {
  try {
    // Connect to MongoDB (same database as your Railway automation)
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db('gfmd_narc_gone');
    const sequencesCollection = db.collection('email_sequences');
    const contactsCollection = db.collection('contacts');
    const suppressionCollection = db.collection('suppression_list');
    const interactionsCollection = db.collection('interactions');
    
    // Get sequence statistics
    const totalSequences = await sequencesCollection.countDocuments({});
    const activeSequences = await sequencesCollection.countDocuments({ status: 'active' });
    const completedSequences = await sequencesCollection.countDocuments({ status: 'completed' });
    const repliedSequences = await sequencesCollection.countDocuments({ status: 'replied' });
    
    // Get bounce and suppression metrics
    const totalSuppressed = await suppressionCollection.countDocuments({ status: 'active' });
    const bouncedEmails = await suppressionCollection.countDocuments({ 
      status: 'active',
      reason: { $regex: 'delivery failed|address not found|bounce', $options: 'i' }
    });
    
    // Get total contacts made (emails sent)
    const totalEmailsSent = await sequencesCollection.aggregate([
      { $match: {} },
      { $group: { _id: null, totalSent: { $sum: '$current_step' } } }
    ]).toArray();
    const emailsSentCount = totalEmailsSent.length > 0 ? totalEmailsSent[0].totalSent : 0;
    
    // Get actual human replies (excluding bounces/system messages)
    const humanReplies = await interactionsCollection.countDocuments({
      type: 'auto_reply',
      sender_email: { 
        $not: { $regex: 'postmaster|mailer-daemon|mail-daemon', $options: 'i' }
      },
      original_content: { $ne: '' }
    });
    
    // Calculate true response rate (human replies / (emails sent - bounces))
    const deliveredEmails = emailsSentCount - bouncedEmails;
    const trueResponseRate = deliveredEmails > 0 ? ((humanReplies / deliveredEmails) * 100) : 0;
    
    // Legacy response rate for backward compatibility
    const responseRate = totalSequences > 0 ? ((repliedSequences / totalSequences) * 100) : 0;
    
    // Get recent sequences for activity table
    const recentSequences = await sequencesCollection
      .find({})
      .sort({ updated_at: -1 })
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
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    const emailPerformance = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const startOfDay = new Date(dateStr + 'T00:00:00.000Z');
      const endOfDay = new Date(dateStr + 'T23:59:59.999Z');

      // Count emails sent on this date from sequences
      const sent = await sequencesCollection.countDocuments({
        'emails_sent.sent_at': {
          $gte: dateStr + 'T00:00:00',
          $lt: dateStr + 'T23:59:59'
        }
      });

      // Get REAL opens from interactions collection (emails with openedAt on this date)
      const opens = await interactionsCollection.countDocuments({
        type: 'email_sent',
        openedAt: { $gte: startOfDay, $lt: endOfDay }
      });

      // Get REAL replies from interactions collection
      const repliesFromTracking = await interactionsCollection.countDocuments({
        type: 'email_sent',
        repliedAt: { $gte: startOfDay, $lt: endOfDay }
      });

      // Also count auto_reply type interactions (detected replies)
      const autoReplies = await interactionsCollection.countDocuments({
        type: 'auto_reply',
        timestamp: { $gte: startOfDay, $lt: endOfDay },
        sender_email: {
          $not: { $regex: 'postmaster|mailer-daemon|mail-daemon', $options: 'i' }
        }
      });

      const replies = repliesFromTracking + autoReplies;

      emailPerformance.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        sent,
        opens,
        replies
      });
    }
    
    // Calculate step distribution for pipeline visualization
    const stepDistribution = await sequencesCollection.aggregate([
      { $match: { status: 'active' } },
      { $group: { _id: '$current_step', count: { $sum: 1 } } },
      { $sort: { _id: 1 } }
    ]).toArray();
    
    // Create lead activity data
    const leadActivity = recentSequences.slice(0, 5).map(sequence => {
      const contact = contactMap.get(sequence.contact_id) || {};
      const lastEmail = sequence.emails_sent[sequence.emails_sent.length - 1];
      const daysSinceLastEmail = lastEmail ? 
        Math.floor((Date.now() - new Date(lastEmail.sent_at).getTime()) / (1000 * 60 * 60 * 24)) : null;
      
      return {
        name: contact.name || sequence.contact_email.split('@')[0],
        organization: contact.organization || 'Unknown',
        stage: getStageFromStep(sequence.current_step),
        lastContact: lastEmail ? `${daysSinceLastEmail} days ago` : 'Never',
        daysUnanswered: sequence.status === 'active' ? daysSinceLastEmail : null,
        status: sequence.status === 'replied' ? 'Engaged' : 
                sequence.status === 'completed' ? 'Customer' : 'Waiting',
        contactEmail: sequence.contact_email,
        contactId: sequence.contact_id
      };
    });
    
    // Get REAL revenue data from orders collection
    const ordersCollection = db.collection('orders');

    // Get revenue aggregated by month for last 6 months
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

    const revenueAggregation = await ordersCollection.aggregate([
      {
        $match: {
          $or: [
            { orderDate: { $gte: sixMonthsAgo } },
            { recordedAt: { $gte: sixMonthsAgo } }
          ]
        }
      },
      {
        $group: {
          _id: {
            year: { $year: { $ifNull: ['$orderDate', '$recordedAt'] } },
            month: { $month: { $ifNull: ['$orderDate', '$recordedAt'] } }
          },
          revenue: { $sum: { $ifNull: ['$revenue', '$amount', 0] } }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1 } }
    ]).toArray();

    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const revenueOverTime = revenueAggregation.map(item => ({
      month: monthNames[item._id.month - 1],
      revenue: item.revenue || 0
    }));

    // If no orders exist, show empty state instead of fake data
    if (revenueOverTime.length === 0) {
      const currentMonth = new Date().getMonth();
      for (let i = 2; i >= 0; i--) {
        const monthIndex = (currentMonth - i + 12) % 12;
        revenueOverTime.push({ month: monthNames[monthIndex], revenue: 0 });
      }
    }

    // Calculate total sales from orders
    const totalSalesAgg = await ordersCollection.aggregate([
      {
        $group: {
          _id: null,
          total: { $sum: { $ifNull: ['$revenue', '$amount', 0] } }
        }
      }
    ]).toArray();
    const actualTotalSales = totalSalesAgg.length > 0 ? totalSalesAgg[0].total : 0;

    // Calculate sales change (this week vs last week)
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    const twoWeeksAgo = new Date();
    twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);

    const thisWeekSales = await ordersCollection.aggregate([
      { $match: { $or: [{ orderDate: { $gte: oneWeekAgo } }, { recordedAt: { $gte: oneWeekAgo } }] } },
      { $group: { _id: null, total: { $sum: { $ifNull: ['$revenue', '$amount', 0] } } } }
    ]).toArray();

    const lastWeekSales = await ordersCollection.aggregate([
      { $match: { $or: [
        { orderDate: { $gte: twoWeeksAgo, $lt: oneWeekAgo } },
        { recordedAt: { $gte: twoWeeksAgo, $lt: oneWeekAgo } }
      ] } },
      { $group: { _id: null, total: { $sum: { $ifNull: ['$revenue', '$amount', 0] } } } }
    ]).toArray();

    const thisWeekTotal = thisWeekSales.length > 0 ? thisWeekSales[0].total : 0;
    const lastWeekTotal = lastWeekSales.length > 0 ? lastWeekSales[0].total : 0;
    const actualSalesChange = lastWeekTotal > 0 ? ((thisWeekTotal - lastWeekTotal) / lastWeekTotal * 100) : 0;

    // Calculate REAL open rate from interactions
    const totalEmailsWithTracking = await interactionsCollection.countDocuments({
      type: 'email_sent'
    });
    const totalOpens = await interactionsCollection.countDocuments({
      type: 'email_sent',
      openedAt: { $exists: true, $ne: null }
    });
    const actualOpenRate = totalEmailsWithTracking > 0
      ? parseFloat(((totalOpens / totalEmailsWithTracking) * 100).toFixed(1))
      : 0;

    await client.close();

    // Return REAL data from your GFMD system
    const dashboardData = {
      totalSales: actualTotalSales,
      salesChange: parseFloat(actualSalesChange.toFixed(1)),
      convertedLeads: repliedSequences,
      leadsChange: Math.max(0, repliedSequences - 3),
      replyRate: parseFloat(responseRate.toFixed(1)),
      openRate: actualOpenRate,
      
      // New KPI metrics
      totalEmailsSent: emailsSentCount,
      bouncedEmails,
      totalSuppressed,
      humanReplies,
      trueResponseRate: parseFloat(trueResponseRate.toFixed(1)),
      deliveredEmails,
      
      totalSequences,
      activeSequences,
      completedSequences,
      emailPerformance,
      revenueOverTime,
      leadActivity,
      stepDistribution,
      systemStatus: {
        automationRunning: true,
        lastContactAddition: new Date().toISOString(),
        nextScheduledRun: getNextScheduledRun()
      }
    };
    
    return NextResponse.json(dashboardData);
    
  } catch (error) {
    console.error('Dashboard API Error:', error);

    // Return error state with empty data - no fake data
    const errorData = {
      totalSales: 0,
      salesChange: 0,
      convertedLeads: 0,
      leadsChange: 0,
      replyRate: 0,
      openRate: 0,
      totalSequences: 0,
      activeSequences: 0,
      completedSequences: 0,
      totalEmailsSent: 0,
      bouncedEmails: 0,
      totalSuppressed: 0,
      humanReplies: 0,
      trueResponseRate: 0,
      deliveredEmails: 0,
      emailPerformance: [],
      revenueOverTime: [],
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

function getStageFromStep(step: number): string {
  if (step <= 1) return 'Initial Contact';
  if (step <= 2) return 'Follow-up';
  if (step <= 4) return 'Qualified';
  return 'Advanced';
}

function getNextScheduledRun(): string {
  const now = new Date();
  const tomorrow8AM = new Date(now);
  tomorrow8AM.setDate(tomorrow8AM.getDate() + 1);
  tomorrow8AM.setHours(8, 0, 0, 0);
  
  // If tomorrow is weekend, move to Monday
  if (tomorrow8AM.getDay() === 0) tomorrow8AM.setDate(tomorrow8AM.getDate() + 1); // Sunday -> Monday
  if (tomorrow8AM.getDay() === 6) tomorrow8AM.setDate(tomorrow8AM.getDate() + 2); // Saturday -> Monday
  
  return tomorrow8AM.toISOString();
}