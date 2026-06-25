import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  Workflow,
  Play,
  CheckSquare,
  UserCheck,
  History,
  Settings,
  Share2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { NAV } from '@/constants/testIds';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, testId: NAV.dashboard },
  { name: 'Process Catalogue', href: '/processes', icon: BookOpen, testId: NAV.processes },
  { name: 'Workflows', href: '/workflows', icon: Workflow, testId: NAV.workflows },
  { name: 'Runs', href: '/runs', icon: Play, testId: NAV.runs },
  { name: 'Tasks', href: '/tasks', icon: CheckSquare, testId: NAV.tasks },
  { name: 'Approvals', href: '/approvals', icon: UserCheck, testId: NAV.approvals },
  { name: 'Audit Logs', href: '/audit-logs', icon: History, testId: NAV.auditLogs },
  { name: 'Integrations', href: '/integrations', icon: Share2, testId: NAV.integrations },
  { name: 'Members & Settings', href: '/settings', icon: Settings, testId: NAV.settings },
];

const Sidebar = () => {
  return (
    <div className="flex h-full w-64 flex-col bg-gray-900 text-white" data-testid={NAV.sidebar}>
      <div className="flex h-16 items-center px-6">
        <span className="text-xl font-bold tracking-tight">FlowForge AI</span>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            data-testid={item.testId}
            className={({ isActive }) =>
              cn(
                "group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              )
            }
          >
            <item.icon className="mr-3 h-5 w-5 flex-shrink-0" aria-hidden="true" />
            {item.name}
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
