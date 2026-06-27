import React from 'react';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Card, CardContent } from '@/components/ui/card';
import { Globe, Home, Copy, FileCode } from 'lucide-react';
import { cn } from '@/lib/utils';

const SourceScope = ({ data, updateData }) => {
  const sources = [
    {
      id: 'workspace',
      title: 'Workspace Model',
      description: 'Create a new process blueprint specific to this workspace.',
      icon: Home,
      color: 'text-blue-500',
      bg: 'bg-blue-50'
    },
    {
      id: 'global_variant',
      title: 'Organisation Variant',
      description: 'Adapt a global FlowForge model for your organisation.',
      icon: Copy,
      color: 'text-purple-500',
      bg: 'bg-purple-50',
      disabled: data.is_platform_admin === false && data.source_type !== 'global'
    },
    {
      id: 'blank',
      title: 'Governed Blank',
      description: 'Start from a validated empty structure with default controls.',
      icon: FileCode,
      color: 'text-slate-500',
      bg: 'bg-slate-50'
    }
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-900">Source & Ownership</h2>
        <p className="text-sm text-slate-500">Define the origin and governance scope of this process model.</p>
      </div>

      <RadioGroup
        value={data.source_type}
        onValueChange={(val) => updateData({ source_type: val })}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        {sources.map((source) => (
          <Label
            key={source.id}
            htmlFor={source.id}
            className={cn(
              "cursor-pointer",
              source.disabled && "opacity-50 cursor-not-allowed"
            )}
          >
            <RadioGroupItem value={source.id} id={source.id} className="sr-only" disabled={source.disabled} />
            <Card className={cn(
              "h-full transition-all border-2",
              data.source_type === source.id ? "border-primary bg-primary/5 ring-4 ring-primary/5" : "border-slate-100 hover:border-slate-200"
            )}>
              <CardContent className="p-6 flex flex-col items-center text-center space-y-4">
                <div className={cn("p-3 rounded-xl", source.bg)}>
                  <source.icon className={cn("h-6 w-6", source.color)} />
                </div>
                <div className="space-y-1">
                  <p className="font-bold text-slate-900">{source.title}</p>
                  <p className="text-[10px] leading-relaxed text-slate-500">{source.description}</p>
                </div>
              </CardContent>
            </Card>
          </Label>
        ))}
      </RadioGroup>

      {data.source_type === 'global_variant' && (
        <div className="p-6 rounded-xl border border-dashed border-slate-200 bg-slate-50/50 space-y-4">
          <Label className="text-xs font-bold uppercase tracking-widest text-slate-400">Target Global Model</Label>
          <div className="flex items-center justify-between p-4 bg-white border rounded-lg shadow-sm">
             <div className="flex items-center space-x-3">
                <Globe className="h-5 w-5 text-primary" />
                <div>
                   <p className="text-sm font-bold text-slate-900">Standard Patient Intake</p>
                   <p className="text-[10px] text-slate-400">Global ID: ff-proc-001 | v1.2.0</p>
                </div>
             </div>
             <Button variant="ghost" size="sm" className="text-xs font-bold text-primary">Change Source</Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SourceScope;
