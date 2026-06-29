import React from 'react';
import { Outlet } from 'react-router-dom';
import GlobalHeader from '../GlobalHeader';
import OwnerSidebar from './OwnerSidebar';
import { Badge } from '@/components/ui/badge';
import { Shield } from 'lucide-react';

const OwnerLayout = () => {
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <OwnerSidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <GlobalHeader>
          <div className="flex items-center space-x-2">
            <Shield className="h-5 w-5 text-side-a" />
            <h1 className="text-sm font-bold uppercase tracking-tight text-slate-500">Platform Management</h1>
            <Badge variant="outline" className="bg-side-a/10 text-side-a border-side-a/20 px-2 py-0">Global</Badge>
          </div>
        </GlobalHeader>
        <main className="flex-1 overflow-y-auto p-10">
          <div className="max-w-7xl mx-auto"><Outlet /></div>
        </main>
      </div>
    </div>
  );
};
export default OwnerLayout;
