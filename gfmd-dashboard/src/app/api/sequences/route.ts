import { NextResponse } from 'next/server';
import { MongoClient, ObjectId } from 'mongodb';

// MongoDB connection - using same credentials as Railway deployment
const MONGODB_URI = process.env.MONGODB_CONNECTION_STRING || process.env.MONGODB_URI || '';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const campaign = searchParams.get('campaign');

    const client = new MongoClient(MONGODB_URI);
    await client.connect();

    const db = client.db('gfmd_narc_gone');
    const sequencesCollection = db.collection('email_sequences');
    const contactsCollection = db.collection('contacts');

    // Get all active sequences, optionally filtered by campaign
    const filter: Record<string, unknown> = { status: 'active' };
    if (campaign) {
      filter.campaign = campaign;
    }
    const sequences = await sequencesCollection
      .find(filter)
      .sort({ updated_at: -1 })
      .toArray();
    
    // Get all contact IDs
    const contactIds = sequences.map(seq => seq.contact_id);
    const objectIds = contactIds.map(id => {
      try {
        return new ObjectId(id);
      } catch {
        return null;
      }
    }).filter(id => id !== null) as ObjectId[];
    
    // Get contact details
    const contacts = await contactsCollection
      .find({ _id: { $in: objectIds } })
      .toArray();
    
    // Create contact lookup map
    const contactMap: Record<string, (typeof contacts)[number]> = {};
    contacts.forEach(contact => {
      contactMap[contact._id.toString()] = contact;
    });
    
    await client.close();
    
    return NextResponse.json({
      sequences: sequences.map(seq => ({
        ...seq,
        _id: seq._id.toString()
      })),
      contacts: contactMap
    });
    
  } catch (error) {
    console.error('Sequences API Error:', error);
    return NextResponse.json({ 
      sequences: [], 
      contacts: {},
      error: 'Failed to fetch sequences' 
    });
  }
}
