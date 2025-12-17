import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardData } from "./dashboard";

interface Props {
  data: DashboardData;
}

const statusColors = {
  Engaged: 'bg-blue-500',
  Waiting: 'bg-gray-400',
  Customer: 'bg-slate-600',
};

export function ActivityTable({ data }: Props) {
  return (
    <Card className="border-gray-200">
      <CardHeader>
        <CardTitle className="text-lg font-normal text-gray-900">
          Recent Lead Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-gray-200">
              <TableHead className="font-normal text-gray-600">Name</TableHead>
              <TableHead className="font-normal text-gray-600">Organization</TableHead>
              <TableHead className="font-normal text-gray-600">Stage</TableHead>
              <TableHead className="font-normal text-gray-600">Last Contact</TableHead>
              <TableHead className="font-normal text-gray-600">Days Unanswered</TableHead>
              <TableHead className="font-normal text-gray-600">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.leadActivity.map((lead, index) => (
              <TableRow key={index} className="border-gray-200 hover:bg-gray-50">
                <TableCell className="font-normal text-gray-900">
                  {lead.name}
                </TableCell>
                <TableCell className="text-gray-600">
                  {lead.organization}
                </TableCell>
                <TableCell className="text-gray-600">
                  {lead.stage}
                </TableCell>
                <TableCell className="text-gray-600">
                  {lead.lastContact}
                </TableCell>
                <TableCell className="text-gray-600">
                  {lead.daysUnanswered ?? 'N/A'}
                </TableCell>
                <TableCell>
                  <div className="flex items-center">
                    <span className={`h-2 w-2 rounded-full ${statusColors[lead.status]} mr-2`}></span>
                    <span className="text-gray-600 font-normal">
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