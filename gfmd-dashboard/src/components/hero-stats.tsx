import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardData } from "./dashboard";

interface Props {
  data: DashboardData;
  onActiveSequencesClick?: () => void;
}

export function HeroStats({ data, onActiveSequencesClick }: Props) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
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
            {data.replyCount || 0} replies received
          </p>
        </CardContent>
      </Card>
      
      <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-light" style={{color: '#272030'}}>Total Emails Sent</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal" style={{color: '#272030'}}>
            {data.totalEmailsSent || 0}
          </div>
          <p className="text-xs font-light mt-1" style={{color: '#272030'}}>
            To law enforcement
          </p>
        </CardContent>
      </Card>
      
      <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-light" style={{color: '#272030'}}>Bounced Emails</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal" style={{color: '#4e2780'}}>
            {data.bouncedEmails || 0}
          </div>
          <p className="text-xs font-light mt-1" style={{color: '#272030'}}>
            {data.totalSuppressed || 0} total suppressed
          </p>
        </CardContent>
      </Card>
      
      <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-light" style={{color: '#272030'}}>Suppressed</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal" style={{color: '#272030'}}>
            {data.totalSuppressed || 0}
          </div>
          <p className="text-xs font-light mt-1" style={{color: '#272030'}}>
            Contacts not receiving emails
          </p>
        </CardContent>
      </Card>
    </div>
  );
}