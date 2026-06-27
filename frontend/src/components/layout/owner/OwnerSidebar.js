import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Package, ShieldCheck, ClipboardList, Activity, Settings, AppWindow, Cloud } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Owner Dashboard', href: '/owner/dashboard', icon: LayoutDashboard },
  { name: 'Client Management', href: '/owner/clients', icon: Users },
  { name: 'Products & Plans', href: '/owner/products', icon: Package },
  { name: 'Service Catalogue', href: '/owner/services', icon: Cloud },
  { name: 'App Catalogue', href: '/owner/applications', icon: AppWindow },
  { name: 'Process Governance', href: '/owner/governance', icon: ShieldCheck },
  { name: 'Platform Audit', href: '/owner/audit', icon: ClipboardList },
  { name: 'System Health', href: '/owner/health', icon: Activity },
  { name: 'Administration', href: '/owner/settings', icon: Settings },
];

const OwnerSidebar = () => {
  return (
    <div className="flex h-full w-64 flex-col bg-slate-950 text-white side-a-border">
      <div className="flex h-16 items-center px-6 border-b border-white/10">
        <span className="text-xl font-extrabold tracking-tight text-white">FlowForge <span className="text-side-a">Owner</span></span>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink key={item.name} to={item.href} className={({ isActive }) => cn("group flex items-center rounded-md px-3 py-2.5 text-sm font-bold transition-all duration-200", isActive ? "bg-side-a/10 text-side-a shadow-sm" : "text-slate-400 hover:bg-white/5 hover:text-white")}>
            <item.icon className="mr-3 h-4 w-4 flex-shrink-0" /> {item.name}
          </NavLink>
        ))}
      </nav>
    </div>
  );
};
export default OwnerSidebar;
