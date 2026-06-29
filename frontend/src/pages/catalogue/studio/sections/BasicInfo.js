import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import FieldOriginBadge from '@/components/catalogue/FieldOriginBadge';

const BasicInfo = ({ data, updateData }) => {
  const isLocked = data?.source_type === 'global' && !data?.is_platform_admin;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
             <Label htmlFor="name" className="text-sm font-bold uppercase tracking-widest text-slate-500">Process Model Name</Label>
             {isLocked && <FieldOriginBadge origin="global_locked" sourceModel="Standard Blueprint" sourceVersion="1.2" policyRule="allow_name_override: false" />}
          </div>
          <Input
            id="name"
            defaultValue={data?.name}
            disabled={isLocked}
            placeholder="e.g., Patient Intake & Triage"
            className="text-lg font-semibold h-12 border-slate-200 focus:border-primary focus:ring-4 focus:ring-primary/5 transition-all"
          />
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="description" className="text-sm font-bold uppercase tracking-widest text-slate-500">Description</Label>
            {isLocked && <FieldOriginBadge origin="global_locked" sourceModel="Standard Blueprint" sourceVersion="1.2" policyRule="allow_description_override: false" />}
          </div>
          <Textarea
            id="description"
            defaultValue={data?.description}
            disabled={isLocked}
            placeholder="High-level overview of the process flow..."
            className="min-h-[120px] resize-none border-slate-200 focus:border-primary transition-all"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label className="text-sm font-bold uppercase tracking-widest text-slate-500">Industry</Label>
          <Select disabled={isLocked}>
            <SelectTrigger className="h-11 border-slate-200 font-bold">
              <SelectValue placeholder="Select industry..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="healthcare">Healthcare</SelectItem>
              <SelectItem value="finance">Finance & Banking</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label className="text-sm font-bold uppercase tracking-widest text-slate-500">Process Family</Label>
          <Select disabled={isLocked}>
            <SelectTrigger className="h-11 border-slate-200 font-bold">
              <SelectValue placeholder="Select family..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="operations">Core Operations</SelectItem>
              <SelectItem value="compliance">Compliance & Risk</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
};

export default BasicInfo;
