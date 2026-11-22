import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardData } from "./dashboard";

interface Props {
  data: DashboardData;
}

export function Charts({ data }: Props) {
  return (
    <div className="grid gap-4">
      <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
        <CardHeader>
          <CardTitle className="text-lg font-normal" style={{color: '#272030'}}>
            Email Performance (Last 7 Days)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.emailPerformance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#efebe2" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12, fill: '#272030', fontWeight: 300 }}
                axisLine={{ stroke: '#efebe2' }}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#272030', fontWeight: 300 }}
                axisLine={{ stroke: '#efebe2' }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #efebe2',
                  borderRadius: '8px',
                  fontSize: '12px',
                  fontWeight: 300
                }}
              />
              <Legend 
                wrapperStyle={{ fontSize: '12px', color: '#272030', fontWeight: 300 }}
              />
              <Line 
                type="monotone" 
                dataKey="sent" 
                stroke="#4e2780" 
                strokeWidth={2}
                name="Sent" 
                dot={{ fill: '#4e2780', strokeWidth: 2, r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="replies"
                stroke="#4e2780"
                strokeWidth={3}
                name="Replies"
                dot={{ fill: '#4e2780', stroke: '#272030', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}