'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface EmailData {
  step: number;
  sent_at: string;
  subject: string;
  actually_sent: boolean;
  content?: string;
}

interface ContactDetails {
  firstName?: string;
  lastName?: string;
  organization?: string;
  title?: string;
  email: string;
}

interface SequenceDetails {
  current_step: number;
  status: string;
  emails_sent: EmailData[];
  created_at: string;
  updated_at: string;
  next_email_due?: string;
}

interface EmailHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  contactEmail: string;
  contactId: string;
}

export function EmailHistoryModal({ isOpen, onClose, contactEmail, contactId }: EmailHistoryModalProps) {
  const [contact, setContact] = useState<ContactDetails | null>(null);
  const [sequence, setSequence] = useState<SequenceDetails | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen && contactEmail) {
      fetchEmailHistory();
    }
  }, [isOpen, contactEmail, contactId]);

  const fetchEmailHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/contact-history?email=${encodeURIComponent(contactEmail)}&contactId=${contactId}`);
      const data = await response.json();
      setContact(data.contact || { email: contactEmail });
      setSequence(data.sequence || null);
    } catch (error) {
      console.error('Error fetching email history:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const displayName = contact ? 
    `${contact.firstName || ''} ${contact.lastName || ''}`.trim() || 
    contactEmail.split('@')[0] : 
    contactEmail.split('@')[0];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-6" style={{borderBottom: '1px solid #efebe2'}}>
          <div>
            <h2 className="text-2xl font-normal" style={{color: '#272030'}}>Email History</h2>
            <p className="text-sm font-light mt-1" style={{color: '#272030'}}>
              {displayName} • {contactEmail}
            </p>
          </div>
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
              <span className="ml-3 font-light" style={{color: '#272030'}}>Loading email history...</span>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Contact Details */}
              {contact && (
                <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
                  <CardHeader>
                    <CardTitle className="text-lg font-normal" style={{color: '#272030'}}>
                      Contact Details
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-light" style={{color: '#272030'}}>Name</p>
                      <p className="font-normal" style={{color: '#272030'}}>{displayName}</p>
                    </div>
                    <div>
                      <p className="text-sm font-light" style={{color: '#272030'}}>Organization</p>
                      <p className="font-normal" style={{color: '#272030'}}>
                        {contact.organization || 'Unknown'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-light" style={{color: '#272030'}}>Title</p>
                      <p className="font-normal" style={{color: '#272030'}}>
                        {contact.title || 'Unknown'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-light" style={{color: '#272030'}}>Email</p>
                      <p className="font-normal" style={{color: '#272030'}}>{contactEmail}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Sequence Status */}
              {sequence && (
                <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
                  <CardHeader>
                    <CardTitle className="text-lg font-normal" style={{color: '#272030'}}>
                      Sequence Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm font-light" style={{color: '#272030'}}>Current Step</p>
                      <p className="font-normal" style={{color: '#272030'}}>Step {sequence.current_step}</p>
                    </div>
                    <div>
                      <p className="text-sm font-light" style={{color: '#272030'}}>Status</p>
                      <span 
                        className="px-2 py-1 rounded text-xs font-light"
                        style={{
                          backgroundColor: sequence.status === 'active' ? '#4e2780' : '#efebe2',
                          color: sequence.status === 'active' ? 'white' : '#272030'
                        }}
                      >
                        {sequence.status}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-light" style={{color: '#272030'}}>Next Email Due</p>
                      <p className="font-normal" style={{color: '#272030'}}>
                        {sequence.next_email_due ? 
                          new Date(sequence.next_email_due).toLocaleDateString() : 
                          'N/A'
                        }
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Email Timeline */}
              <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
                <CardHeader>
                  <CardTitle className="text-lg font-normal" style={{color: '#272030'}}>
                    Email Timeline ({sequence?.emails_sent.length || 0} emails)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {sequence && sequence.emails_sent.length > 0 ? (
                    <div className="space-y-4">
                      {sequence.emails_sent
                        .sort((a, b) => new Date(a.sent_at).getTime() - new Date(b.sent_at).getTime())
                        .map((email, index) => (
                        <div 
                          key={index} 
                          className="p-4 rounded"
                          style={{
                            borderLeft: '4px solid #4e2780',
                            backgroundColor: '#efebe2',
                            opacity: email.actually_sent ? 1 : 0.7
                          }}
                        >
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="font-normal" style={{color: '#272030'}}>
                                Step {email.step}: {email.subject}
                              </h4>
                              <p className="text-sm font-light" style={{color: '#272030'}}>
                                {new Date(email.sent_at).toLocaleDateString()} at{' '}
                                {new Date(email.sent_at).toLocaleTimeString()}
                              </p>
                            </div>
                            <span 
                              className="px-2 py-1 rounded text-xs font-light"
                              style={{
                                backgroundColor: email.actually_sent ? '#4e2780' : '#272030',
                                color: 'white'
                              }}
                            >
                              {email.actually_sent ? 'Sent' : 'Draft'}
                            </span>
                          </div>
                          
                          {email.content && (
                            <div className="mt-3 p-3 rounded text-sm" style={{backgroundColor: '#ffffff'}}>
                              <p className="font-light whitespace-pre-wrap" style={{color: '#272030'}}>
                                {email.content}
                              </p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-center py-8 font-light" style={{color: '#272030'}}>
                      No emails sent yet
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}