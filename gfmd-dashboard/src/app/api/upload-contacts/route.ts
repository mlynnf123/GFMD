import { NextResponse } from 'next/server';
import { MongoClient } from 'mongodb';

// Increase timeout for large file uploads
export const maxDuration = 60; // 60 seconds max

const MONGODB_URI = process.env.MONGODB_CONNECTION_STRING ||
  'mongodb+srv://solutions-account:GFMDgfmd2280%40%40@cluster0.hdejtab.mongodb.net/?appName=Cluster0';

interface ContactRow {
  name?: string;
  email?: string;
  organization?: string;
  title?: string;
  location?: string;
  phone?: string;
  [key: string]: string | undefined;
}

function parseCSV(csvText: string): ContactRow[] {
  const lines = csvText.split('\n').filter(line => line.trim());
  if (lines.length < 2) return [];

  // Parse header row
  const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]/g, ''));

  // Map common column names to standard fields
  const fieldMappings: Record<string, string[]> = {
    name: ['name', 'contact_name', 'full_name', 'contact', 'person', 'fullname'],
    email: ['email', 'email_address', 'contact_email', 'e_mail', 'emailaddress'],
    organization: ['organization', 'company', 'department', 'agency', 'org', 'organisation'],
    title: ['title', 'position', 'role', 'job_title', 'jobtitle'],
    location: ['location', 'city', 'address', 'state', 'city_state', 'citystate'],
    phone: ['phone', 'phone_number', 'telephone', 'contact_phone', 'phonenumber']
  };

  function findHeaderIndex(possibleNames: string[]): number {
    for (const name of possibleNames) {
      const idx = headers.indexOf(name);
      if (idx !== -1) return idx;
    }
    return -1;
  }

  const columnIndexes: Record<string, number> = {};
  for (const [field, possibleNames] of Object.entries(fieldMappings)) {
    columnIndexes[field] = findHeaderIndex(possibleNames);
  }

  // Parse data rows
  const contacts: ContactRow[] = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // Handle CSV with quoted values
    const values: string[] = [];
    let current = '';
    let inQuotes = false;

    for (const char of line) {
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    values.push(current.trim());

    const contact: ContactRow = {};
    for (const [field, idx] of Object.entries(columnIndexes)) {
      if (idx !== -1 && values[idx]) {
        contact[field] = values[idx].replace(/^["']|["']$/g, '').trim();
      }
    }

    // Only add if email exists
    if (contact.email) {
      contact.email = contact.email.toLowerCase();

      // Generate name from email if missing
      if (!contact.name && contact.email) {
        const emailParts = contact.email.split('@')[0];
        contact.name = emailParts.replace(/[._]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      }

      contacts.push(contact);
    }
  }

  return contacts;
}

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const startSequences = formData.get('startSequences') === 'true';

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Read file content
    const csvText = await file.text();
    const contacts = parseCSV(csvText);

    if (contacts.length === 0) {
      return NextResponse.json({
        error: 'No valid contacts found in CSV. Ensure file has email column.'
      }, { status: 400 });
    }

    // Connect to MongoDB
    const client = new MongoClient(MONGODB_URI);
    await client.connect();

    const db = client.db('gfmd_narc_gone');
    const contactsCollection = db.collection('contacts');
    const sequencesCollection = db.collection('email_sequences');

    let imported = 0;
    let duplicates = 0;
    let sequencesStarted = 0;
    const errors: string[] = [];

    for (const contact of contacts) {
      try {
        // Check if contact already exists
        const existing = await contactsCollection.findOne({
          email: contact.email?.toLowerCase()
        });

        if (existing) {
          duplicates++;
          continue;
        }

        // Insert contact
        const contactDoc = {
          name: contact.name || '',
          email: contact.email?.toLowerCase() || '',
          organization: contact.organization || '',
          title: contact.title || '',
          location: contact.location || '',
          phone: contact.phone || '',
          status: 'new',
          createdAt: new Date(),
          updatedAt: new Date(),
          source: 'csv_upload'
        };

        const result = await contactsCollection.insertOne(contactDoc);
        imported++;

        // Start sequence if requested
        if (startSequences && result.insertedId) {
          const sequenceDoc = {
            contact_id: result.insertedId.toString(),
            contact_email: contact.email?.toLowerCase(),
            sequence_name: 'narc_gone_law_enforcement',
            current_step: 0,
            status: 'active',
            emails_sent: [],
            last_email_sent: null,
            next_email_due: new Date().toISOString(),
            reply_received: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };

          await sequencesCollection.insertOne(sequenceDoc);
          sequencesStarted++;
        }

      } catch (err) {
        errors.push(`${contact.email}: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }
    }

    await client.close();

    return NextResponse.json({
      success: true,
      imported,
      duplicates,
      sequencesStarted,
      totalProcessed: contacts.length,
      errors: errors.length,
      errorDetails: errors.slice(0, 10)
    });

  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json({
      error: 'Failed to process CSV file',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function GET() {
  // Return sample CSV format
  const sampleCSV = `name,email,organization,title,location,phone
John Smith,john.smith@police.gov,City Police Department,Chief of Police,Austin TX,555-0101
Jane Doe,jane.doe@sheriff.gov,County Sheriff Office,Sheriff,Houston TX,555-0102`;

  return new NextResponse(sampleCSV, {
    headers: {
      'Content-Type': 'text/csv',
      'Content-Disposition': 'attachment; filename="sample_contacts.csv"'
    }
  });
}
