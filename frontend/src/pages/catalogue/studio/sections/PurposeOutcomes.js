import React from 'react';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Target, Flag, AlertCircle } from 'lucide-react';
import FieldOriginBadge from '@/components/catalogue/FieldOriginBadge';

const PurposeOutcomes = ({ data, updateData }) => {
  const isLocked = data?.source_type === 'global' && !data?.is_platform_admin;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-900">Purpose & Desired Outcomes</h2>
        <p className="text-sm text-slate-500">Why does this process exist and what constitutes success?</p>
      </div>

      <div className="space-y-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-xs font-bold uppercase tracking-widest text-slate-500">Business Purpose</Label>
            {isLocked && <FieldOriginBadge origin="global_locked" sourceModel="Standard Blueprint" sourceVersion="1.2" policyRule="allow_purpose_override: false" />}
          </div>
          <Card className="border-slate-100 shadow-sm">
             <CardContent className="p-0">
                <Textarea
                  disabled={isLocked}
                  placeholder="Explain the 'Why' behind this process..."
                  className="min-h-[100px] border-none focus-visible:ring-0 text-sm font-medium leading-relaxed"
                />
             </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-2 gap-6">
           <div className="space-y-3">
              <Label className="text-xs font-bold uppercase tracking-widest text-slate-500">Pre-conditions</Label>
              <div className="p-4 rounded-xl border border-slate-100 bg-white min-h-[120px] space-y-2">
                 <div className="flex items-center space-x-2 p-2 bg-slate-50 rounded border border-slate-100">
                    <Flag className="h-3 w-3 text-slate-400" />
                    <span className="text-[10px] font-bold text-slate-600">Patient Arrives at Clinic</span>
                 </div>
                 <Button variant="ghost" size="sm" disabled={isLocked} className="w-full text-[10px] font-bold text-primary h-7">Add Condition</Button>
              </div>
           </div>

           <div className="space-y-3">
              <Label className="text-xs font-bold uppercase tracking-widest text-slate-500">Success Criteria</Label>
              <div className="p-4 rounded-xl border border-slate-100 bg-white min-h-[120px] space-y-2">
                 <div className="flex items-center space-x-2 p-2 bg-success/5 rounded border border-success/10 text-success">
                    <Target className="h-3 w-3" />
                    <span className="text-[10px] font-bold">Patient Registered in EMR</span>
                 </div>
                 <Button variant="ghost" size="sm" disabled={isLocked} className="w-full text-[10px] font-bold text-primary h-7">Add Outcome</Button>
              </div>
           </div>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-amber-50 border border-amber-100 flex items-start space-x-3">
         <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5" />
         <p className="text-[10px] font-medium text-amber-700 leading-relaxed">
            Defining clear success criteria allows FlowForge AI to suggest better validation points in the Operational Map section.
         </p>
      </div>
    </div>
  );
};

export default PurposeOutcomes;
