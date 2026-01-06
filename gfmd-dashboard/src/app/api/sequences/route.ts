import { NextResponse } from 'next/server';
import { MongoClient, ObjectId } from 'mongodb';

// MongoDB connection - using same credentials as Railway deployment
const MONGODB_URI = process.env.MONGODB_CONNECTION_STRING || 
  'mongodb+srv://solutions-account:GFMDgfmd2280%40%40@cluster0.hdejtab.mongodb.net/?appName=Cluster0';

export async function GET() {
  try {
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db('gfmd_narc_gone');
    const sequencesCollection = db.collection('email_sequences');
    const contactsCollection = db.collection('contacts');
    
    // Get all active sequences
    const sequences = await sequencesCollection
      .find({ status: 'active' })
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
    const contactMap: {[key: string]: any} = {};
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