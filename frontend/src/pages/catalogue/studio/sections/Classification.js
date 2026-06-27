import React from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tag } from 'lucide-react';

const Classification = ({ data, updateData }) => {
  const isLocked = data?.source_type === 'global' && !data?.is_platform_admin;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-900">Taxonomy & Taxonomy</h2>
        <p className="text-sm text-slate-500">Categorize this process for discovery and reporting.</p>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="space-y-2">
            <Label className="text-xs font-bold uppercase tracking-widest text-slate-400">Business Segment</Label>
            <Select disabled={isLocked} defaultValue="operations">
              <SelectTrigger className="h-11 font-bold">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="operations">Clinical Operations</SelectItem>
                <SelectItem value="finance">Revenue Cycle</SelectItem>
                <SelectItem value="it">Digital Health IT</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label className="text-xs font-bold uppercase tracking-widest text-slate-400">Process Family</Label>
            <Select disabled={isLocked} defaultValue="intake">
              <SelectTrigger className="h-11 font-bold">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="intake">Patient Access & Intake</SelectItem>
                <SelectItem value="billing">Claims & Billing</SelectItem>
                <SelectItem value="care">Direct Care Delivery</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-2">
            <Label className="text-xs font-bold uppercase tracking-widest text-slate-400">Department Applicability</Label>
            <div className="p-4 border rounded-lg bg-white space-y-3">
               <div className="flex flex-wrap gap-2">
                  {['Admissions', 'Nursing', 'Finance'].map(dept => (
                    <Badge key={dept} variant="secondary" className="px-2 py-1 text-[10px] font-bold uppercase tracking-tight">
                       {dept}
                    </Badge>
                  ))}
               </div>
               <Button variant="ghost" size="sm" disabled={isLocked} className="w-full text-[10px] font-bold text-primary h-7">Add Department</Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-xs font-bold uppercase tracking-widest text-slate-400">Search Tags</Label>
            <div className="relative">
               <Tag className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
               <Input
                  disabled={isLocked}
                  placeholder="Add tags..."
                  className="pl-9 h-11 text-xs font-medium"
               />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Classification;
