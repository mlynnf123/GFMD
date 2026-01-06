import { NextResponse } from 'next/server';
import { MongoClient, ObjectId } from 'mongodb';

// MongoDB connection - using same credentials as Railway deployment
const MONGODB_URI = process.env.MONGODB_CONNECTION_STRING || 
  'mongodb+srv://solutions-account:GFMDgfmd2280%40%40@cluster0.hdejtab.mongodb.net/?appName=Cluster0';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const email = searchParams.get('email');
    const contactId = searchParams.get('contactId');
    
    if (!email) {
      return NextResponse.json({ error: 'Email parameter required' }, { status: 400 });
    }
    
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    
    const db = client.db('gfmd_narc_gone');
    const sequencesCollection = db.collection('email_sequences');
    const contactsCollection = db.collection('contacts');
    
    // Get contact details
    let contact = null;
    if (contactId) {
      try {
        contact = await contactsCollection.findOne({ _id: new ObjectId(contactId) });
      } catch (error) {
        console.log('Error finding contact by ID, trying by email:', error);
      }
    }
    
    // Fallback to find by email
    if (!contact) {
      contact = await contactsCollection.findOne({ email: email.toLowerCase() });
    }
    
    // Get sequence for this contact
    const sequence = await sequencesCollection.findOne({ 
      contact_email: email.toLowerCase() 
    });
    
    await client.close();
    
    return NextResponse.json({
      contact: contact ? {
        firstName: contact.firstName,
        lastName: contact.lastName,
        organization: contact.organization,
        title: contact.title,
        email: contact.email
      } : { email },
      sequence: sequence ? {
        current_step: sequence.current_step,
        status: sequence.status,
        emails_sent: sequence.emails_sent || [],
        created_at: sequence.created_at,
        updated_at: sequence.updated_at,
        next_email_due: sequence.next_email_due
      } : null
    });
    
  } catch (error) {
    console.error('Contact History API Error:', error);
    return NextResponse.json({ 
      contact: null, 
      sequence: null,
      error: 'Failed to fetch contact history' 
    });
  }
}