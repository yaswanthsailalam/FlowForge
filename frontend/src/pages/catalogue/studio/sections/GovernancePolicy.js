import React from 'react';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { ShieldCheck, Lock, Unlock, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

const GovernancePolicy = ({ data, updateData }) => {
  const isPlatformAdmin = !!data?.is_platform_admin;

  const policies = [
    { key: 'allow_name_override', label: 'Allow Name Override', desc: 'Permit workspace users to rename this model.', locked: !isPlatformAdmin },
    { key: 'allow_stage_reorder', label: 'Allow Stage Reordering', desc: 'Permit modifications to the operational sequence.', locked: !isPlatformAdmin },
    { key: 'require_internal_review', label: 'Mandatory Internal Review', desc: 'Force approval before publishing in workspace.', locked: false }
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-900">Governance & Extension Policy</h2>
        <p className="text-sm text-slate-500">Define how this model can be adapted by others.</p>
      </div>

      {!isPlatformAdmin && (
        <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-100 flex items-start space-x-3 mb-6">
           <Lock className="h-4 w-4 text-indigo-600 mt-0.5" />
           <div className="space-y-1">
              <p className="text-[10px] font-bold text-indigo-900 uppercase tracking-tight">Read-Only Governance</p>
              <p className="text-[10px] font-medium text-indigo-700 leading-relaxed">
                 Extension policies are controlled at the Platform level. You are viewing the effective policy for this variant.
              </p>
           </div>
        </div>
      )}

      <div className="space-y-4">
        {policies.map((p) => (
          <div key={p.key} className="flex items-center justify-between p-4 rounded-xl border border-slate-100 bg-white">
             <div className="flex items-center space-x-4">
                <div className={cn("p-2 rounded-lg", p.locked ? "bg-slate-100" : "bg-success/5")}>
                   {p.locked ? <Lock className="h-4 w-4 text-slate-400" /> : <Unlock className="h-4 w-4 text-success" />}
                </div>
                <div>
                   <p className="text-sm font-bold text-slate-900">{p.label}</p>
                   <p className="text-[10px] text-slate-500 font-medium">{p.desc}</p>
                </div>
             </div>
             <Switch disabled={p.locked} checked={true} />
          </div>
        ))}
      </div>

      <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 space-y-4">
         <div className="flex items-center space-x-3 text-slate-400">
            <ShieldCheck className="h-4 w-4" />
            <span className="text-[10px] font-bold uppercase tracking-widest">Effective Compliance Level</span>
         </div>
         <div className="flex items-center justify-between">
            <div className="space-y-1">
               <p className="text-sm font-bold text-slate-900">Enterprise Standard (Tier 1)</p>
               <p className="text-[10px] text-slate-400">Full audit logging and version traceability enabled.</p>
            </div>
            <Badge className="bg-indigo-600 text-white border-none text-[9px] font-bold px-3">Governed</Badge>
         </div>
      </div>
    </div>
  );
};

export default GovernancePolicy;
