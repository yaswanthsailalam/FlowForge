import React from 'react';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, AlertCircle, Send, FileText, Globe } from 'lucide-react';
import { cn } from '@/lib/utils';

const ReviewPublish = ({ data, updateData }) => {
  const validations = [
    { label: 'Basic Identity', status: 'pass' },
    { label: 'Operational Map Integrity', status: 'pass' },
    { label: 'Extension Policy Compliance', status: 'pass' },
    { label: 'Data Classification assigned', status: 'warn', msg: 'Confidentiality tag recommended.' }
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-900">Finalize & Submit</h2>
        <p className="text-sm text-slate-500">Review the validation results and publish the process model.</p>
      </div>

      <div className="grid grid-cols-2 gap-8">
         <div className="space-y-6">
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Validation Summary</h3>
            <div className="space-y-3">
               {validations.map((v, i) => (
                  <div key={i} className="flex items-start space-x-3 p-3 rounded-lg border border-slate-100 bg-white">
                     {v.status === 'pass' ? (
                        <CheckCircle2 className="h-4 w-4 text-success mt-0.5" />
                     ) : (
                        <AlertCircle className="h-4 w-4 text-amber-500 mt-0.5" />
                     )}
                     <div className="space-y-1">
                        <p className="text-xs font-bold text-slate-900">{v.label}</p>
                        {v.msg && <p className="text-[10px] text-slate-500">{v.msg}</p>}
                     </div>
                  </div>
               ))}
            </div>
         </div>

         <div className="space-y-6">
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Publication Context</h3>
            <div className="p-6 rounded-2xl border-2 border-primary/10 bg-primary/5 space-y-6">
               <div className="flex items-center space-x-4">
                  <div className="p-3 bg-white rounded-xl shadow-sm border border-primary/10">
                     <FileText className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                     <p className="text-sm font-bold text-slate-900">v{data.version || '1.0.0'}</p>
                     <p className="text-[10px] text-slate-500 font-bold uppercase tracking-tight">Version Label</p>
                  </div>
               </div>

               <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs font-medium">
                     <span className="text-slate-500">Scope:</span>
                     <span className="font-bold text-slate-900 capitalize">{data.source_type}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs font-medium">
                     <span className="text-slate-500">Visibility:</span>
                     <span className="font-bold text-slate-900">Workspace Only</span>
                  </div>
                  <div className="flex items-center justify-between text-xs font-medium">
                     <span className="text-slate-500">Approver:</span>
                     <span className="font-bold text-slate-900">Internal Reviewer</span>
                  </div>
               </div>

               <Button className="w-full h-11 bg-slate-900 hover:bg-slate-800 text-white font-bold uppercase tracking-widest text-[10px] shadow-lg">
                  <Send className="mr-2 h-4 w-4" />
                  Submit for Review
               </Button>
            </div>
         </div>
      </div>

      <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 flex items-center justify-between">
         <div className="flex items-center space-x-3">
            <Globe className="h-4 w-4 text-slate-400" />
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Global Sync</span>
         </div>
         <Badge variant="outline" className="text-[9px] font-bold uppercase tracking-widest text-slate-400">Not Eligible</Badge>
      </div>
    </div>
  );
};

export default ReviewPublish;
