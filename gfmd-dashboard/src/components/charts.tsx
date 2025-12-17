import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardData } from "./dashboard";

interface Props {
  data: DashboardData;
}

export function Charts({ data }: Props) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card className="border-gray-200">
        <CardHeader>
          <CardTitle className="text-lg font-normal text-gray-900">
            Email Performance (Last 7 Days)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.emailPerformance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#e2e8f0' }}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#e2e8f0' }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
              />
              <Legend 
                wrapperStyle={{ fontSize: '12px', color: '#64748b' }}
              />
              <Line 
                type="monotone" 
                dataKey="sent" 
                stroke="#64748b" 
                strokeWidth={2}
                name="Sent" 
                dot={{ fill: '#64748b', strokeWidth: 2, r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="opens" 
                stroke="#94a3b8" 
                strokeWidth={2}
                name="Opens" 
                dot={{ fill: '#94a3b8', strokeWidth: 2, r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="replies" 
                stroke="#3b82f6" 
                strokeWidth={2}
                name="Replies" 
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      
      <Card className="border-gray-200">
        <CardHeader>
          <CardTitle className="text-lg font-normal text-gray-900">
            Revenue Over Time (Last 90 Days)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.revenueOverTime}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="month" 
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#e2e8f0' }}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#e2e8f0' }}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
                formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Revenue']}
              />
              <Bar 
                dataKey="revenue" 
                fill="#3b82f6" 
                name="Revenue"
                radius={[2, 2, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}