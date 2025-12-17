import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardData } from "./dashboard";

interface Props {
  data: DashboardData;
}

export function HeroStats({ data }: Props) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card className="border-gray-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-normal text-gray-600">Total Sales</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal text-gray-900">
            ${data.totalSales.toLocaleString()}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {data.salesChange >= 0 ? `+${data.salesChange}%` : `${data.salesChange}%`} from last month
          </p>
        </CardContent>
      </Card>
      
      <Card className="border-gray-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-normal text-gray-600">Active Sequences</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal text-gray-900">
            {data.activeSequences}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {data.totalSequences} total sequences
          </p>
        </CardContent>
      </Card>
      
      <Card className="border-gray-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-normal text-gray-600">Reply Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal text-gray-900">
            {data.replyRate}%
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Target: 5-8%
          </p>
        </CardContent>
      </Card>
      
      <Card className="border-gray-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-normal text-gray-600">Open Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-normal text-gray-900">
            {data.openRate}%
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Target: 40-50%
          </p>
        </CardContent>
      </Card>
    </div>
  );
}