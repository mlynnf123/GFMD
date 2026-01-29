'use client';

import { useEffect, useState } from 'react';
import { HeroStats } from './hero-stats';
import { Charts } from './charts';
import { ActivityTable } from './activity-table';
import { SystemStatus } from './system-status';
import { SequencesModal } from './sequences-modal';
import { EmailHistoryModal } from './email-history-modal';
import { SuppressionModal } from './suppression-modal';
import { UploadContactsModal } from './upload-contacts-modal';

// Define the types for our GFMD data
export interface DashboardData {
  totalSales: number;
  salesChange: number;
  convertedLeads: number;
  leadsChange: number;
  replyRate: number;
  openRate: number;
  totalSequences: number;
  activeSequences: number;
  completedSequences: number;
  
  // New KPI metrics
  totalEmailsSent?: number;
  bouncedEmails?: number;
  totalSuppressed?: number;
  humanReplies?: number;
  trueResponseRate?: number;
  deliveredEmails?: number;
  emailPerformance: {
    date: string;
    sent: number;
    opens: number;
    replies: number;
  }[];
  revenueOverTime: {
    month: string;
    revenue: number;
  }[];
  leadActivity: {
    name: string;
    organization: string;
    stage: string;
    lastContact: string;
    daysUnanswered: number | null;
    status: 'Engaged' | 'Waiting' | 'Customer';
    contactEmail?: string;
    contactId?: string;
  }[];
  stepDistribution?: {
    _id: number;
    count: number;
  }[];
  systemStatus: {
    automationRunning: boolean;
    lastContactAddition: string;
    nextScheduledRun: string;
  };
  error?: string;
}

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [sequencesModalOpen, setSequencesModalOpen] = useState(false);
  const [emailHistoryModalOpen, setEmailHistoryModalOpen] = useState(false);
  const [suppressionModalOpen, setSuppressionModalOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedContact, setSelectedContact] = useState<{email: string, id: string} | null>(null);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/dashboard-data', {
        cache: 'no-store' // Always fetch fresh data
      });
      const result = await response.json();
      setData(result);
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 30 seconds for real-time monitoring
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleActiveSequencesClick = () => {
    setSequencesModalOpen(true);
  };

  const handleContactClick = (contactEmail: string, contactId?: string) => {
    setSelectedContact({ email: contactEmail, id: contactId || '' });
    setEmailHistoryModalOpen(true);
  };

  const handleSequenceContactClick = (contactEmail: string, contactId: string) => {
    setSequencesModalOpen(false);
    setSelectedContact({ email: contactEmail, id: contactId });
    setEmailHistoryModalOpen(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 mx-auto mb-4" style={{borderColor: '#4e2780'}}></div>
          <p className="text-lg font-normal" style={{color: '#272030'}}>Loading GFMD Dashboard...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-normal mb-2" style={{color: '#272030'}}>Connection Failed</h2>
          <p className="mb-4 font-light" style={{color: '#272030'}}>Unable to connect to GFMD automation system.</p>
          <button 
            onClick={fetchData}
            className="px-4 py-2 rounded font-normal text-white hover:opacity-90"
            style={{backgroundColor: '#4e2780'}}
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-4 md:p-8 max-w-7xl mx-auto">
      {/* Header with system status */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-normal" style={{color: '#272030'}}>GFMD Email Automation Dashboard</h1>
          <p style={{color: '#272030'}} className="mt-1 font-light">
            Real-time monitoring of your law enforcement outreach campaigns
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setUploadModalOpen(true)}
            className="px-4 py-2 rounded font-normal text-white hover:opacity-90"
            style={{backgroundColor: '#4e2780'}}
          >
            Upload Contacts
          </button>
          <button
            onClick={() => setSuppressionModalOpen(true)}
            className="px-4 py-2 rounded font-normal hover:opacity-90"
            style={{backgroundColor: '#efebe2', color: '#272030'}}
          >
            Suppression List
          </button>
          <div className="text-sm font-light" style={{color: '#272030'}}>
            Last updated: {lastRefresh.toLocaleTimeString()}
            {data.error && (
              <span className="ml-2 font-normal" style={{color: '#4e2780'}}>
                (Using cached data)
              </span>
            )}
          </div>
        </div>
      </div>

      {/* System Status Banner */}
      <SystemStatus data={data} />
      
      {/* Main Stats */}
      <HeroStats data={data} onActiveSequencesClick={handleActiveSequencesClick} />
      
      {/* Charts */}
      <Charts data={data} />
      
      {/* Activity Table */}
      <ActivityTable data={data} onContactClick={handleContactClick} />

      {/* Modals */}
      <SequencesModal 
        isOpen={sequencesModalOpen}
        onClose={() => setSequencesModalOpen(false)}
        onContactClick={handleSequenceContactClick}
      />
      
      <EmailHistoryModal
        isOpen={emailHistoryModalOpen}
        onClose={() => setEmailHistoryModalOpen(false)}
        contactEmail={selectedContact?.email || ''}
        contactId={selectedContact?.id || ''}
      />
      
      <SuppressionModal
        isOpen={suppressionModalOpen}
        onClose={() => setSuppressionModalOpen(false)}
      />

      <UploadContactsModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
      />
      
      {/* Footer */}
      <div className="text-center text-sm font-light mt-8 p-4" style={{borderTop: '1px solid #efebe2', color: '#272030'}}>
        <p>
          GFMD Automation System • Railway Deployment Status: 
          <span className="ml-1 font-normal" style={{color: '#4e2780'}}>
            {data.systemStatus.automationRunning ? 'ACTIVE' : 'INACTIVE'}
          </span>
        </p>
        <p className="mt-1">
          Next scheduled contact addition: {new Date(data.systemStatus.nextScheduledRun).toLocaleString()}
        </p>
      </div>
    </div>
  );
}