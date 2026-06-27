import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Info, Lock, Globe, Share2, ShieldCheck, HelpCircle } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

const FieldOriginBadge = ({ origin, sourceModel, sourceVersion, policyRule }) => {
  const config = {
    'global_locked': { label: 'Global Locked', color: 'bg-red-50 text-red-600 border-red-100', icon: Lock, desc: 'Locked by global policy. Changes prohibited.' },
    'global_required': { label: 'Global Required', color: 'bg-amber-50 text-amber-600 border-amber-100', icon: ShieldCheck, desc: 'Required by global standards.' },
    'global_recommended': { label: 'Global Recommended', color: 'bg-blue-50 text-blue-600 border-blue-100', icon: Globe, desc: 'Best practice recommendation.' },
    'inherited_configurable': { label: 'Inherited', color: 'bg-slate-50 text-slate-600 border-slate-200', icon: Share2, desc: 'Inherited but customizable.' },
    'workspace_defined': { label: 'Local', color: 'bg-success/5 text-success border-success/20', icon: Share2, desc: 'Defined within this workspace.' },
  };

  const c = config[origin] || config['inherited_configurable'];

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge variant="outline" className={cn("text-[8px] font-extrabold uppercase px-1.5 py-0 cursor-help transition-all hover:scale-105", c.color)}>
            <c.icon className="h-2.5 w-2.5 mr-1" />
            {c.label}
          </Badge>
        </TooltipTrigger>
        <TooltipContent className="max-w-[200px] p-3 space-y-2">
          <div className="flex items-center space-x-2 border-b pb-2 mb-2">
             <c.icon className="h-4 w-4 text-primary" />
             <span className="font-bold text-xs">{c.label}</span>
          </div>
          <p className="text-[10px] font-medium leading-relaxed text-slate-500">{c.desc}</p>
          {sourceModel && (
            <div className="pt-1 border-t mt-1">
               <p className="text-[8px] font-bold text-slate-400 uppercase">Source</p>
               <p className="text-[10px] font-bold text-slate-700">{sourceModel} (v{sourceVersion})</p>
            </div>
          )}
          {policyRule && (
            <div className="pt-1">
               <p className="text-[8px] font-bold text-slate-400 uppercase">Policy Rule</p>
               <p className="text-[10px] italic text-slate-600">"{policyRule}"</p>
            </div>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

const cn = (...classes) => classes.filter(Boolean).join(' ');

export default FieldOriginBadge;
