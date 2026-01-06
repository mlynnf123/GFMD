import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardData } from "./dashboard";

interface Props {
  data: DashboardData;
  onActiveSequencesClick?: () => void;
}

export function HeroStats({ data, onActiveSequencesClick }: Props) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Card 
        style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}
        className={`${onActiveSequencesClick ? 'cursor-pointer hover:opacity-90 transition-opacity' : ''}`}
        onClick={onActiveSequencesClick}
      >
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-light" style={{color: '#272030'}}>Active Sequences</CardTitle>
          {onActiveSequencesClick && (
            <span className="text-xs font-light" style={{color: '#4e2780'}}>Click to view</span>
          )}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal" style={{color: '#272030'}}>
            {data.activeSequences}
          </div>
          <p className="text-xs font-light mt-1" style={{color: '#272030'}}>
            {data.totalSequences} total sequences
          </p>
        </CardContent>
      </Card>
      
      <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-light" style={{color: '#272030'}}>Reply Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal" style={{color: '#272030'}}>
            {data.replyRate}%
          </div>
          <p className="text-xs font-light mt-1" style={{color: '#272030'}}>
            Target: 5-8%
          </p>
        </CardContent>
      </Card>
      
      <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-light" style={{color: '#272030'}}>Open Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal" style={{color: '#272030'}}>
            {data.openRate}%
          </div>
          <p className="text-xs font-light mt-1" style={{color: '#272030'}}>
            Target: 40-50%
          </p>
        </CardContent>
      </Card>
    </div>
  );
}