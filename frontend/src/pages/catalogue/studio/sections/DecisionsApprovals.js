import React from 'react';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { GitBranch, CheckSquare, AlertTriangle, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

const DecisionsApprovals = ({ data, updateData }) => {
  const isLocked = data?.source_type === 'global' && !data?.is_platform_admin;

  const nodes = [
    { type: 'decision', label: 'Eligibility Verified?', result: 'Boolean (Yes/No)', icon: GitBranch, color: 'text-blue-500' },
    { type: 'approval', label: 'Nurse Final Review', actor: 'Nurse Practitioner', icon: CheckSquare, color: 'text-purple-500' },
    { type: 'exception', label: 'Missing Health ID', flow: 'Redirect to Support', icon: AlertTriangle, color: 'text-amber-500' }
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-900">Logic & Approvals</h2>
        <p className="text-sm text-slate-500">Define the branch points and human-in-the-loop requirements.</p>
      </div>

      <div className="space-y-4">
        {nodes.map((node, idx) => (
          <Card key={idx} className="border-slate-100 shadow-sm group hover:border-slate-200 transition-all">
             <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                   <div className="p-2.5 rounded-lg bg-slate-50">
                      <node.icon className={cn("h-5 w-5", node.color)} />
                   </div>
                   <div>
                      <div className="flex items-center space-x-2">
                         <span className="text-sm font-bold text-slate-900">{node.label}</span>
                         <Badge variant="outline" className="text-[8px] font-bold uppercase tracking-tight text-slate-400 border-slate-100">{node.type}</Badge>
                      </div>
                      <p className="text-[10px] text-slate-500 font-medium">
                         {node.actor || node.result || node.flow}
                      </p>
                   </div>
                </div>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-slate-300 group-hover:text-primary transition-colors">
                   <ArrowRight className="h-4 w-4" />
                </Button>
             </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4">
         {['Add Decision', 'Add Approval', 'Add Exception'].map(action => (
            <Button key={action} variant="outline" disabled={isLocked} className="border-dashed h-11 text-[9px] font-bold uppercase tracking-widest text-slate-500">
               {action}
            </Button>
         ))}
      </div>
    </div>
  );
};

export default DecisionsApprovals;
