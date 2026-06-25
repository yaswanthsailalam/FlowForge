import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { DASHBOARD } from '@/constants/testIds';
import { LayoutDashboard, Users, Zap, CheckCircle2 } from 'lucide-react';

const DashboardPage = () => {
  const { user } = useAuth();
  const { activeWorkspace } = useWorkspace();

  const stats = [
    { name: 'Active Workflows', value: '-', icon: Zap, color: 'text-blue-600' },
    { name: 'Team Members', value: '-', icon: Users, color: 'text-green-600' },
    { name: 'Completed Runs', value: '-', icon: CheckCircle2, color: 'text-purple-600' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight" data-testid={DASHBOARD.welcomeMessage}>
          Welcome back, {user?.full_name}!
        </h1>
        <p className="text-muted-foreground">
          Here's what's happening in <span className="font-semibold" data-testid={DASHBOARD.activeWorkspaceName}>{activeWorkspace?.name}</span> today.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.name}</CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">No data available yet</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground">
              No recent activity to display.
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Quick Links</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            <div className="rounded-lg border p-3 hover:bg-gray-50 cursor-pointer">
              <div className="font-medium text-sm">Create a new process</div>
              <div className="text-xs text-muted-foreground italic">Coming soon</div>
            </div>
            <div className="rounded-lg border p-3 hover:bg-gray-50 cursor-pointer">
              <div className="font-medium text-sm">Configure integrations</div>
              <div className="text-xs text-muted-foreground italic">Coming soon</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;
