import React from 'react';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, User, ArrowRight } from 'lucide-react';

const Participants = ({ data, updateData }) => {
  const isLocked = data?.source_type === 'global' && !data?.is_platform_admin;

  const roles = [
    { role: 'Process Owner', icon: User, color: 'text-indigo-600', bg: 'bg-indigo-50', desc: 'Accountable for the end-to-end execution.' },
    { role: 'Front Desk Operator', icon: Users, color: 'text-blue-600', bg: 'bg-blue-50', desc: 'Primary actor for initial data entry.' },
    { role: 'Nurse Practitioner', icon: Users, color: 'text-emerald-600', bg: 'bg-emerald-50', desc: 'Approver for clinical triage data.' }
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-900">Participants & Responsibilities</h2>
        <p className="text-sm text-slate-500">Define the roles required to execute and govern this process.</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {roles.map((item, idx) => (
          <Card key={idx} className="border-slate-100 shadow-sm hover:border-slate-200 transition-all group">
            <CardContent className="p-4 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={cn("p-2.5 rounded-lg", item.bg)}>
                  <item.icon className={cn("h-5 w-5", item.color)} />
                </div>
                <div>
                   <p className="text-sm font-bold text-slate-900">{item.role}</p>
                   <p className="text-[10px] text-slate-500">{item.desc}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                 <Badge variant="outline" className="text-[10px] font-bold border-slate-200">System Role</Badge>
                 <Button variant="ghost" size="sm" disabled={isLocked} className="h-8 w-8 p-0 text-slate-400 group-hover:text-primary">
                    <ArrowRight className="h-4 w-4" />
                 </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Button variant="outline" disabled={isLocked} className="w-full border-dashed h-12 text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-primary hover:border-primary/50 transition-all bg-slate-50/50">
         Add Participant Role
      </Button>
    </div>
  );
};

export default Participants;
