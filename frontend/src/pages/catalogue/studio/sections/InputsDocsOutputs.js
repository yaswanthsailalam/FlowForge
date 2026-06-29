import React from 'react';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, FileText, Share2, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

const InputsDocsOutputs = ({ data, updateData }) => {
  const isLocked = data?.source_type === 'global' && !data?.is_platform_admin;

  const dataItems = [
    { type: 'input', label: 'National Health ID', format: 'String (Masked)', req: true, icon: Database, color: 'text-blue-500' },
    { type: 'document', label: 'Photo ID Scan', format: 'Image/PDF', req: true, icon: FileText, color: 'text-amber-500' },
    { type: 'output', label: 'Intake Confirmation', format: 'JSON', req: false, icon: Share2, color: 'text-emerald-500' }
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-900">Data, Documents & Hand-offs</h2>
        <p className="text-sm text-slate-500">Map the information flow required for process integrity.</p>
      </div>

      <div className="space-y-4">
        {dataItems.map((item, idx) => (
          <div key={idx} className="flex items-center space-x-4 p-4 rounded-xl border border-slate-100 bg-white group hover:border-slate-200 transition-all shadow-sm">
             <div className="p-2 rounded-lg bg-slate-50">
                <item.icon className={cn("h-5 w-5", item.color)} />
             </div>
             <div className="flex-1">
                <div className="flex items-center space-x-2">
                   <span className="text-sm font-bold text-slate-900">{item.label}</span>
                   {item.req && <Badge className="bg-amber-50 text-amber-700 hover:bg-amber-100 border-none text-[8px] font-bold uppercase tracking-tight h-4">Required</Badge>}
                </div>
                <p className="text-[10px] text-slate-400 font-medium">{item.format}</p>
             </div>
             <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-[9px] font-bold uppercase tracking-tighter text-slate-400 border-slate-100">{item.type}</Badge>
                {!isLocked && <Button variant="ghost" size="sm" className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 text-slate-400">...</Button>}
             </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
         <Button variant="outline" disabled={isLocked} className="border-dashed h-11 text-[10px] font-bold uppercase tracking-widest text-slate-500">Add Data Field</Button>
         <Button variant="outline" disabled={isLocked} className="border-dashed h-11 text-[10px] font-bold uppercase tracking-widest text-slate-500">Add Document</Button>
      </div>

      <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/30 flex items-center justify-between">
         <div className="flex items-center space-x-3">
            <Shield className="h-4 w-4 text-slate-400" />
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Data Classification</span>
         </div>
         <Badge className="bg-slate-900 text-white text-[9px] font-bold uppercase tracking-widest border-none px-3 h-5">Confidential (PII)</Badge>
      </div>
    </div>
  );
};

export default InputsDocsOutputs;
