import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardData } from "./dashboard";

interface Props {
  data: DashboardData;
  onContactClick?: (contactEmail: string, contactId?: string) => void;
}

const statusColors = {
  Engaged: '#4e2780',
  Waiting: '#efebe2', 
  Customer: '#272030',
};

export function ActivityTable({ data, onContactClick }: Props) {
  return (
    <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
      <CardHeader>
        <CardTitle className="text-lg font-normal" style={{color: '#272030'}}>
          Recent Lead Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow style={{borderColor: '#efebe2'}}>
              <TableHead className="font-light" style={{color: '#272030'}}>Name</TableHead>
              <TableHead className="font-light" style={{color: '#272030'}}>Organization</TableHead>
              <TableHead className="font-light" style={{color: '#272030'}}>Stage</TableHead>
              <TableHead className="font-light" style={{color: '#272030'}}>Last Contact</TableHead>
              <TableHead className="font-light" style={{color: '#272030'}}>Days Unanswered</TableHead>
              <TableHead className="font-light" style={{color: '#272030'}}>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.leadActivity.map((lead, index) => (
              <TableRow 
                key={index} 
                style={{borderColor: '#efebe2'}} 
                className={`${onContactClick ? 'cursor-pointer hover:opacity-70' : 'hover:bg-white'}`}
                onClick={() => onContactClick && onContactClick(lead.contactEmail || lead.name, lead.contactId)}
              >
                <TableCell className="font-normal" style={{color: '#272030'}}>
                  <div className="flex items-center">
                    {lead.name}
                    {onContactClick && (
                      <span className="ml-2 text-xs font-light" style={{color: '#4e2780'}}>
                        View emails →
                      </span>
                    )}
                  </div>
                </TableCell>
                <TableCell className="font-light" style={{color: '#272030'}}>
                  {lead.organization}
                </TableCell>
                <TableCell className="font-light" style={{color: '#272030'}}>
                  {lead.stage}
                </TableCell>
                <TableCell className="font-light" style={{color: '#272030'}}>
                  {lead.lastContact}
                </TableCell>
                <TableCell className="font-light" style={{color: '#272030'}}>
                  {lead.daysUnanswered ?? 'N/A'}
                </TableCell>
                <TableCell>
                  <div className="flex items-center">
                    <span 
                      className="h-2 w-2 rounded-full mr-2"
                      style={{backgroundColor: statusColors[lead.status], border: lead.status === 'Waiting' ? '1px solid #272030' : 'none'}}
                    ></span>
                    <span className="font-light" style={{color: '#272030'}}>
                      {lead.status}
                    </span>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}