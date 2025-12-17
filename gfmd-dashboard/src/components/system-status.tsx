import { Card, CardContent } from "@/components/ui/card";
import type { DashboardData } from "./dashboard";

interface Props {
  data: DashboardData;
}

export function SystemStatus({ data }: Props) {
  const isRunning = data.systemStatus.automationRunning;
  
  return (
    <Card className={`border-2 ${isRunning ? 'border-blue-200 bg-blue-50' : 'border-gray-300 bg-gray-50'}`}>
      <CardContent className="py-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-blue-500' : 'bg-gray-400'}`}></div>
            <div>
              <h3 className="text-lg font-normal text-gray-900">
                Email Automation System
              </h3>
              <p className="text-sm text-gray-600">
                Status: {isRunning ? 'Active and processing sequences' : 'Inactive'}
              </p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-sm text-gray-600">
              <div>Active Sequences: <span className="font-normal text-gray-900">{data.activeSequences}</span></div>
              <div>Total Contacts: <span className="font-normal text-gray-900">{data.totalSequences}</span></div>
              <div>Completed: <span className="font-normal text-gray-900">{data.completedSequences}</span></div>
            </div>
          </div>
        </div>
        
        {data.error && (
          <div className="mt-3 p-3 bg-white border border-gray-200 rounded text-sm">
            <span className="text-gray-600">Note: </span>
            <span className="text-gray-700">{data.error}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}