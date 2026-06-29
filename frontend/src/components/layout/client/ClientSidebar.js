import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  Workflow,
  Play,
  CheckSquare,
  History,
  Settings,
  Briefcase,
  Share2,
  Cloud
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Discover Processes', href: '/processes', icon: Search },
  { name: 'Workflow Drafts', href: '/workflows', icon: Workflow },
  { name: 'My Applications', href: '/integrations', icon: Share2 },
  { name: 'Org Services', href: '/services', icon: Cloud },
  { name: 'Runs', href: '/runs', icon: Play, status: 'beta', unavailable: true },
  { name: 'Task Inbox', href: '/tasks', icon: CheckSquare, status: 'beta', unavailable: true },
  { name: 'Approvals', href: '/approvals', icon: Briefcase, status: 'beta', unavailable: true },
  { name: 'Audit Logs', href: '/audit-logs', icon: History, status: 'beta', unavailable: true },
  { name: 'Org Settings', href: '/settings', icon: Settings },
];

const ClientSidebar = () => {
  return (
    <nav className="flex h-full w-64 flex-col bg-white border-r text-slate-900 side-b-border" aria-label="Main Navigation">
      <div className="flex h-16 items-center px-6 border-b">
        <span className="text-xl font-extrabold tracking-tight">FlowForge <span className="text-side-b">Client</span></span>
      </div>
      <div className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.unavailable ? '#' : item.href}
            onClick={(e) => item.unavailable && e.preventDefault()}
            className={({ isActive }) =>
              cn(
                "group flex items-center justify-between rounded-md px-3 py-2.5 text-sm font-bold transition-all duration-200",
                isActive && !item.unavailable
                  ? "bg-side-b/10 text-side-b shadow-sm"
                  : "text-slate-500 hover:bg-slate-100 hover:text-slate-900",
                item.unavailable && "opacity-50 cursor-not-allowed grayscale"
              )
            }
          >
            <div className="flex items-center">
               <item.icon className={cn("mr-3 h-4 w-4 flex-shrink-0 transition-colors", !item.unavailable && "group-hover:text-slate-600")} aria-hidden="true" />
               {item.name}
            </div>
            {item.status === 'beta' && (
               <Badge className="bg-slate-100 text-slate-400 border-none text-[8px] font-extrabold uppercase px-1.5 h-4">Beta</Badge>
            )}
          </NavLink>
        ))}
      </div>
      <div className="p-4 border-t bg-slate-50/50">
        <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2">
          <span>Enterprise Plan</span>
          <span className="text-side-b">80% used</span>
        </div>
        <div className="h-1 w-full bg-slate-200 rounded-full overflow-hidden" role="progressbar" aria-valuenow="80" aria-valuemin="0" aria-valuemax="100">
          <div className="h-full bg-side-b w-[80%]" />
        </div>
      </div>
    </nav>
  );
};

export default ClientSidebar;
