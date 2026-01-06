import { Card, CardContent } from "@/components/ui/card";
import type { DashboardData } from "./dashboard";

interface Props {
  data: DashboardData;
}

export function SystemStatus({ data }: Props) {
  const isRunning = data.systemStatus.automationRunning;
  
  return (
    <Card style={{
      borderWidth: '2px', 
      borderColor: isRunning ? '#4e2780' : '#efebe2',
      backgroundColor: isRunning ? '#ffffff' : '#efebe2'
    }}>
      <CardContent className="py-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div 
              className="w-3 h-3 rounded-full"
              style={{backgroundColor: isRunning ? '#4e2780' : '#272030'}}
            ></div>
            <div>
              <h3 className="text-lg font-normal" style={{color: '#272030'}}>
                Email Automation System
              </h3>
              <p className="text-sm font-light" style={{color: '#272030'}}>
                Status: {isRunning ? 'Active and processing sequences' : 'Inactive'}
              </p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-sm font-light" style={{color: '#272030'}}>
              <div>Active Sequences: <span className="font-normal">{data.activeSequences}</span></div>
              <div>Total Contacts: <span className="font-normal">{data.totalSequences}</span></div>
              <div>Completed: <span className="font-normal">{data.completedSequences}</span></div>
            </div>
          </div>
        </div>
        
        {data.error && (
          <div className="mt-3 p-3 rounded text-sm" style={{backgroundColor: '#ffffff', border: '1px solid #efebe2'}}>
            <span className="font-light" style={{color: '#272030'}}>Note: </span>
            <span className="font-normal" style={{color: '#272030'}}>{data.error}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}