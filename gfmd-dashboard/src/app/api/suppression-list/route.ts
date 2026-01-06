import { NextResponse } from 'next/server';
import { MongoClient, ObjectId } from 'mongodb';

// MongoDB connection - using same credentials as Railway deployment
const MONGODB_URI = process.env.MONGODB_CONNECTION_STRING || 
  'mongodb+srv://solutions-account:GFMDgfmd2280%40%40@cluster0.hdejtab.mongodb.net/?appName=Cluster0';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');
    const search = searchParams.get('search') || '';
    
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db('gfmd_narc_gone');
    const suppressionCollection = db.collection('suppression_list');
    
    // Build query for search
    let query: any = { status: 'active' };
    
    if (search) {
      query.email = { $regex: search, $options: 'i' };
    }
    
    // Get total count for pagination
    const totalCount = await suppressionCollection.countDocuments(query);
    
    // Get suppressed contacts with pagination
    const suppressedContacts = await suppressionCollection
      .find(query)
      .sort({ suppressed_at: -1 })
      .skip((page - 1) * limit)
      .limit(limit)
      .toArray();
    
    // Get summary stats
    const statsResult = await suppressionCollection.aggregate([
      { $match: { status: 'active' } },
      { $group: { _id: '$reason', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]).toArray();
    
    const totalSuppressed = await suppressionCollection.countDocuments({ status: 'active' });
    const recentSuppressed = await suppressionCollection.countDocuments({
      status: 'active',
      suppressed_at: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) }
    });
    
    await client.close();
    
    return NextResponse.json({
      suppressed_contacts: suppressedContacts.map(contact => ({
        ...contact,
        _id: contact._id.toString()
      })),
      pagination: {
        current_page: page,
        total_pages: Math.ceil(totalCount / limit),
        total_count: totalCount,
        limit: limit
      },
      stats: {
        total_suppressed: totalSuppressed,
        recent_suppressed: recentSuppressed,
        by_reason: statsResult
      }
    });
    
  } catch (error) {
    console.error('Suppression List API Error:', error);
    return NextResponse.json({ 
      error: 'Failed to fetch suppression list',
      suppressed_contacts: [],
      pagination: { current_page: 1, total_pages: 0, total_count: 0, limit: 50 },
      stats: { total_suppressed: 0, recent_suppressed: 0, by_reason: [] }
    });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, reason, admin_user } = body;
    
    if (!email || !reason) {
      return NextResponse.json({ error: 'Email and reason are required' }, { status: 400 });
    }
    
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db('gfmd_narc_gone');
    const suppressionCollection = db.collection('suppression_list');
    const contactsCollection = db.collection('contacts');
    const sequencesCollection = db.collection('email_sequences');
    
    // Check if already suppressed
    const existing = await suppressionCollection.findOne({
      email: email.toLowerCase(),
      status: 'active'
    });
    
    if (existing) {
      await client.close();
      return NextResponse.json({ error: 'Email already suppressed' }, { status: 400 });
    }
    
    // Add to suppression list
    const suppressionRecord = {
      email: email.toLowerCase(),
      suppressed_at: new Date(),
      reason: reason,
      source: {
        type: 'manual_admin',
        admin_user: admin_user || 'dashboard_user'
      },
      status: 'active'
    };
    
    await suppressionCollection.insertOne(suppressionRecord);
    
    // Update contact status
    await contactsCollection.updateOne(
      { email: email.toLowerCase() },
      {
        $set: {
          status: 'suppressed',
          suppressed_at: new Date(),
          suppression_reason: reason
        }
      }
    );
    
    // Stop active sequences
    await sequencesCollection.updateMany(
      { contact_email: email.toLowerCase(), status: 'active' },
      {
        $set: {
          status: 'suppressed',
          stopped_at: new Date(),
          stop_reason: reason
        }
      }
    );
    
    await client.close();
    
    return NextResponse.json({ 
      success: true, 
      message: 'Contact successfully suppressed' 
    });
    
  } catch (error) {
    console.error('Suppression Add API Error:', error);
    return NextResponse.json({ 
      error: 'Failed to add suppression' 
    }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const email = searchParams.get('email');
    const admin_user = searchParams.get('admin_user') || 'dashboard_user';
    
    if (!email) {
      return NextResponse.json({ error: 'Email parameter required' }, { status: 400 });
    }
    
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db('gfmd_narc_gone');
    const suppressionCollection = db.collection('suppression_list');
    const contactsCollection = db.collection('contacts');
    
    // Mark suppression as inactive (don't actually delete for audit trail)
    const result = await suppressionCollection.updateOne(
      { email: email.toLowerCase(), status: 'active' },
      {
        $set: {
          status: 'inactive',
          unsuppressed_at: new Date(),
          unsuppressed_by: admin_user
        }
      }
    );
    
    if (result.modifiedCount > 0) {
      // Update contact status back to active
      await contactsCollection.updateOne(
        { email: email.toLowerCase() },
        {
          $set: {
            status: 'active',
            suppressed_at: null,
            suppression_reason: null,
            unsuppressed_at: new Date(),
            unsuppressed_by: admin_user
          }
        }
      );
      
      await client.close();
      return NextResponse.json({ 
        success: true, 
        message: 'Contact successfully unsuppressed' 
      });
    } else {
      await client.close();
      return NextResponse.json({ 
        error: 'No active suppression found for this email' 
      }, { status: 404 });
    }
    
  } catch (error) {
    console.error('Suppression Delete API Error:', error);
    return NextResponse.json({ 
      error: 'Failed to remove suppression' 
    }, { status: 500 });
  }
}