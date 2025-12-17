'use client';

import { useEffect, useState } from 'react';
import { HeroStats } from './hero-stats';
import { Charts } from './charts';
import { ActivityTable } from './activity-table';
import { SystemStatus } from './system-status';

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Loading GFMD Dashboard...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-normal text-gray-800 mb-2">Connection Failed</h2>
          <p className="text-gray-600 mb-4">Unable to connect to GFMD automation system.</p>
          <button 
            onClick={fetchData}
            className="bg-slate-600 text-white px-4 py-2 rounded hover:bg-slate-700"
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
          <h1 className="text-3xl font-normal text-gray-900">GFMD Email Automation Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Real-time monitoring of your law enforcement outreach campaigns
          </p>
        </div>
        <div className="text-sm text-gray-500">
          Last updated: {lastRefresh.toLocaleTimeString()}
          {data.error && (
            <span className="ml-2 text-slate-600 font-normal">
              (Using cached data)
            </span>
          )}
        </div>
      </div>

      {/* System Status Banner */}
      <SystemStatus data={data} />
      
      {/* Main Stats */}
      <HeroStats data={data} />
      
      {/* Charts */}
      <Charts data={data} />
      
      {/* Activity Table */}
      <ActivityTable data={data} />
      
      {/* Footer */}
      <div className="text-center text-sm text-gray-500 mt-8 p-4 border-t">
        <p>
          GFMD Automation System • Railway Deployment Status: 
          <span className="ml-1 text-blue-600 font-normal">
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