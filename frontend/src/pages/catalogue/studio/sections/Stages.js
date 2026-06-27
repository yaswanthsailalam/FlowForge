import React from 'react';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Layers, Plus, GripVertical, Info, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';

const Stages = ({ data, updateData }) => {
  const isLocked = data?.source_type === 'global' && !data?.is_platform_admin;

  const defaultStages = [
    { id: 1, name: 'Check-in & Verification', activities: 4, type: 'mandatory', origin: 'global' },
    { id: 2, name: 'Data Collection', activities: 6, type: 'mandatory', origin: 'global' },
    { id: 3, name: 'Review & Triage', activities: 2, type: 'optional', origin: 'workspace' }
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-900">Operational Map</h2>
        <p className="text-sm text-slate-500">Define the stages and activities that form the process backbone.</p>
      </div>

      <div className="space-y-4">
        {defaultStages.map((stage, idx) => (
          <div key={stage.id} className="group flex items-center space-x-4">
             <div className="flex-1 p-4 rounded-xl border border-slate-100 bg-white shadow-sm hover:border-slate-200 transition-all flex items-center justify-between">
                <div className="flex items-center space-x-4">
                   <div className="cursor-grab active:cursor-grabbing text-slate-300 hover:text-slate-500 transition-colors">
                      <GripVertical className="h-4 w-4" />
                   </div>
                   <div className="flex flex-col">
                      <div className="flex items-center space-x-2">
                         <span className="text-sm font-bold text-slate-900">{stage.name}</span>
                         {stage.type === 'mandatory' && <Badge className="bg-slate-50 text-slate-400 border-none text-[8px] font-bold uppercase h-4">Locked</Badge>}
                      </div>
                      <span className="text-[10px] text-slate-400 font-medium">{stage.activities} Activities defined</span>
                   </div>
                </div>
                <div className="flex items-center space-x-4">
                   <Badge variant="outline" className={cn(
                      "text-[9px] font-bold uppercase tracking-tight",
                      stage.origin === 'global' ? "text-indigo-500 border-indigo-100 bg-indigo-50/30" : "text-emerald-500 border-emerald-100 bg-emerald-50/30"
                   )}>
                      {stage.origin}
                   </Badge>
                   <Button variant="ghost" size="sm" className="h-8 text-[10px] font-bold text-primary px-3">Edit Details</Button>
                </div>
             </div>
             {!isLocked && stage.origin !== 'global' && (
                <Button variant="ghost" size="sm" className="h-10 w-10 p-0 text-slate-300 hover:text-destructive hover:bg-destructive/5 opacity-0 group-hover:opacity-100 transition-all">
                   <Trash2 className="h-4 w-4" />
                </Button>
             )}
          </div>
        ))}
      </div>

      <div className="flex items-center space-x-4">
         <Button variant="outline" disabled={isLocked} className="flex-1 border-dashed h-12 text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-primary transition-all">
            <Plus className="mr-2 h-4 w-4" />
            Add New Stage
         </Button>
         <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <Info className="h-4 w-4 text-slate-400" />
         </div>
      </div>
    </div>
  );
};

export default Stages;
