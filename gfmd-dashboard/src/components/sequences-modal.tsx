'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

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
  next_email_due?: string;
}

interface ContactData {
  firstName?: string;
  lastName?: string;
  organization?: string;
  title?: string;
}

interface SequencesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onContactClick: (contactEmail: string, contactId: string) => void;
}

export function SequencesModal({ isOpen, onClose, onContactClick }: SequencesModalProps) {
  const [sequences, setSequences] = useState<SequenceData[]>([]);
  const [contacts, setContacts] = useState<{[key: string]: ContactData}>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchSequences();
    }
  }, [isOpen]);

  const fetchSequences = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/sequences');
      const data = await response.json();
      setSequences(data.sequences || []);
      setContacts(data.contacts || {});
    } catch (error) {
      console.error('Error fetching sequences:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-6" style={{borderBottom: '1px solid #efebe2'}}>
          <h2 className="text-2xl font-normal" style={{color: '#272030'}}>Active Email Sequences</h2>
          <button
            onClick={onClose}
            className="text-2xl font-light hover:opacity-70"
            style={{color: '#272030'}}
          >
            ×
          </button>
        </div>
        
        <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{borderColor: '#4e2780'}}></div>
              <span className="ml-3 font-light" style={{color: '#272030'}}>Loading sequences...</span>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow style={{borderColor: '#efebe2'}}>
                  <TableHead className="font-light" style={{color: '#272030'}}>Contact</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Organization</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Current Step</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Emails Sent</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Status</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Next Email Due</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Last Updated</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sequences.map((sequence) => {
                  const contact = contacts[sequence.contact_id] || {};
                  const name = `${contact.firstName || ''} ${contact.lastName || ''}`.trim() || 
                              sequence.contact_email.split('@')[0];
                  
                  return (
                    <TableRow 
                      key={sequence._id}
                      style={{borderColor: '#efebe2'}}
                      className="hover:bg-white cursor-pointer"
                      onClick={() => onContactClick(sequence.contact_email, sequence.contact_id)}
                    >
                      <TableCell className="font-normal" style={{color: '#272030'}}>
                        <div>
                          <div className="font-normal">{name}</div>
                          <div className="text-sm font-light" style={{color: '#272030', opacity: 0.7}}>
                            {sequence.contact_email}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="font-light" style={{color: '#272030'}}>
                        {contact.organization || 'Unknown'}
                      </TableCell>
                      <TableCell className="font-light" style={{color: '#272030'}}>
                        Step {sequence.current_step}
                      </TableCell>
                      <TableCell className="font-light" style={{color: '#272030'}}>
                        {sequence.emails_sent.length}
                      </TableCell>
                      <TableCell>
                        <span 
                          className="px-2 py-1 rounded text-xs font-light"
                          style={{
                            backgroundColor: sequence.status === 'active' ? '#4e2780' : '#efebe2',
                            color: sequence.status === 'active' ? 'white' : '#272030'
                          }}
                        >
                          {sequence.status}
                        </span>
                      </TableCell>
                      <TableCell className="font-light" style={{color: '#272030'}}>
                        {sequence.next_email_due ? 
                          new Date(sequence.next_email_due).toLocaleDateString() : 
                          'N/A'
                        }
                      </TableCell>
                      <TableCell className="font-light" style={{color: '#272030'}}>
                        {new Date(sequence.updated_at).toLocaleDateString()}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
          
          {!loading && sequences.length === 0 && (
            <div className="text-center py-12">
              <p className="font-light" style={{color: '#272030'}}>No active sequences found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}