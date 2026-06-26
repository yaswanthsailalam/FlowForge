import React, { useState, useEffect } from 'react';
import {
  ChevronRight,
  ChevronLeft,
  Save,
  CheckCircle2,
  AlertCircle,
  FileText,
  Target,
  Users,
  Layers,
  ShieldCheck,
  Zap,
  Eye,
  Settings,
  Database,
  GitBranch,
  Globe,
  Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

// Section Components
import SourceScope from './sections/SourceScope';
import Classification from './sections/Classification';
import BasicInfo from './sections/BasicInfo';
import PurposeOutcomes from './sections/PurposeOutcomes';
import Participants from './sections/Participants';
import InputsDocsOutputs from './sections/InputsDocsOutputs';
import Stages from './sections/Stages';
import DecisionsApprovals from './sections/DecisionsApprovals';
import GovernancePolicy from './sections/GovernancePolicy';
import ReviewPublish from './sections/ReviewPublish';

const sections = [
  { id: 'source', title: 'Source & Scope', icon: Globe, component: SourceScope },
  { id: 'classification', title: 'Classification', icon: Settings, component: Classification },
  { id: 'basic', title: 'Identity', icon: FileText, component: BasicInfo },
  { id: 'strategy', title: 'Purpose', icon: Target, component: PurposeOutcomes },
  { id: 'participants', title: 'Participants', icon: Users, component: Participants },
  { id: 'data', title: 'Data & Docs', icon: Database, component: InputsDocsOutputs },
  { id: 'stages', title: 'Operational Map', icon: Layers, component: Stages },
  { id: 'logic', title: 'Logic & Approvals', icon: GitBranch, component: DecisionsApprovals },
  { id: 'governance', title: 'Policy', icon: ShieldCheck, component: GovernancePolicy },
  { id: 'review', title: 'Finalize', icon: Zap, component: ReviewPublish },
];

const ProcessModelStudio = () => {
  const { modelId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [activeSection, setActiveSection] = useState('source');
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(!!modelId);
  const [data, setData] = useState({
      name: '',
      description: '',
      source_type: 'workspace',
      lifecycle_status: 'draft',
      version: '1.0.0',
      stages: []
  });
  const [progress, setProgress] = useState(10);
  const [isDirty, setIsDirty] = useState(false);

  // Mock Loading existing data
  useEffect(() => {
    if (modelId) {
      setTimeout(() => {
        setData({
          model_id: modelId,
          name: 'Patient Intake v1.2',
          description: 'Initial clinic intake blueprint.',
          source_type: 'global',
          lifecycle_status: 'draft',
          version: '1.2.0',
          is_platform_admin: false // Mock for locking
        });
        setIsLoading(false);
      }, 1000);
    }
  }, [modelId]);

  // Protect unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);

  const currentSectionIndex = sections.findIndex(s => s.id === activeSection);
  const CurrentComponent = sections[currentSectionIndex].component;

  const handleNext = () => {
    if (currentSectionIndex < sections.length - 1) {
      setActiveSection(sections[currentSectionIndex + 1].id);
      setProgress(Math.min(100, ((currentSectionIndex + 2) / sections.length) * 100));
    }
  };

  const handleBack = () => {
    if (currentSectionIndex > 0) {
      setActiveSection(sections[currentSectionIndex - 1].id);
    }
  };

  const handleSave = async () => {
     setIsSaving(true);
     // In a real app: await catalogueService.updateModel(modelId, data);
     setTimeout(() => {
        setIsSaving(false);
        setIsDirty(false);
     }, 800);
  };

  if (isLoading) {
     return (
        <div className="flex h-screen items-center justify-center bg-slate-50 flex-col space-y-4">
           <Loader2 className="h-10 w-10 text-primary animate-spin" />
           <p className="text-sm font-bold uppercase tracking-widest text-slate-400">Loading Blueprint Studio...</p>
        </div>
     );
  }

  return (
    <div className="flex h-[calc(100vh-8.5rem)] overflow-hidden bg-white rounded-xl border shadow-xl shadow-slate-200/50">
      {/* Left Panel: Navigation */}
      <div className="w-64 border-r bg-slate-50/50 flex flex-col">
        <div className="p-6 border-b bg-white">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400">Studio</h2>
            <Badge variant="outline" className="bg-success/5 text-success border-success/20 text-[10px] font-bold uppercase tracking-tighter">
               {data.lifecycle_status} Mode
            </Badge>
          </div>
          <Progress value={progress} className="h-1.5 bg-slate-100" />
          <p className="text-[10px] text-slate-400 mt-2 font-bold uppercase tracking-tight">{Math.round(progress)}% Complete</p>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {sections.map((section, idx) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={cn(
                "w-full flex items-center justify-between px-3 py-3 rounded-lg text-sm font-bold transition-all group text-left",
                activeSection === section.id
                  ? "bg-white text-primary shadow-sm border border-slate-200 ring-4 ring-primary/5"
                  : "text-slate-500 hover:bg-slate-100 hover:text-slate-900"
              )}
            >
              <div className="flex items-center">
                <section.icon className={cn("mr-3 h-4 w-4", activeSection === section.id ? "text-primary" : "text-slate-400 group-hover:text-slate-600")} />
                {section.title}
              </div>
              {idx < currentSectionIndex && <CheckCircle2 className="h-4 w-4 text-success fill-success/10" />}
            </button>
          ))}
        </nav>

        {isDirty && (
          <div className="p-4 border-t bg-amber-50">
             <div className="flex items-center justify-between px-2 py-1 bg-amber-100 rounded border border-amber-200">
                <span className="text-[10px] font-bold text-amber-700 uppercase">Unsaved Changes</span>
                <div className="h-1.5 w-1.5 rounded-full bg-amber-600 animate-pulse" />
             </div>
          </div>
        )}
      </div>

      {/* Center Panel: Editor */}
      <div className="flex-1 flex flex-col bg-slate-50/20">
        <header className="h-14 border-b bg-white px-6 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Section {currentSectionIndex + 1}</span>
            <ChevronRight className="h-3 w-3 text-slate-300" />
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-tight">{sections[currentSectionIndex].title}</h3>
          </div>
          <div className="flex items-center space-x-3">
            {isSaving && <Loader2 className="h-3.5 w-3.5 animate-spin text-slate-400" />}
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tight">
               {isSaving ? 'Saving...' : 'Saved 2m ago'}
            </span>
            <Button
               variant="outline"
               size="sm"
               disabled={!isDirty || isSaving}
               onClick={handleSave}
               className="h-8 text-xs font-bold uppercase tracking-wider"
            >
              <Save className="mr-2 h-3.5 w-3.5" />
              Save Draft
            </Button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="p-10 max-w-4xl mx-auto min-h-full flex flex-col">
            <div className="flex-1">
              <CurrentComponent data={data} updateData={(newData) => { setData(prev => ({...prev, ...newData})); setIsDirty(true); }} />
            </div>

            <div className="flex items-center justify-between pt-10 mt-10 border-t">
              <Button
                variant="ghost"
                onClick={handleBack}
                disabled={currentSectionIndex === 0}
                className="font-bold text-slate-500 uppercase tracking-wider text-xs h-10 px-6"
              >
                <ChevronLeft className="mr-2 h-4 w-4" />
                Previous
              </Button>
              <Button
                onClick={handleNext}
                className="bg-primary hover:bg-primary/90 px-10 font-bold uppercase tracking-widest text-xs h-10 shadow-lg shadow-primary/20"
              >
                {currentSectionIndex === sections.length - 1 ? 'Finish' : 'Continue'}
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        </main>
      </div>

      {/* Right Panel: Live Preview */}
      <div className="w-80 border-l bg-white flex flex-col hidden xl:flex">
        <header className="h-14 border-b px-4 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center space-x-2">
            <Eye className="h-4 w-4 text-slate-400" />
            <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Real-time Preview</span>
          </div>
          <Badge variant="outline" className="text-[10px] bg-white">v{data.version}</Badge>
        </header>
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          <div className="space-y-3">
             <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Model Context</h4>
             <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-2">
                <p className="text-xs font-bold text-slate-900">{data.name || 'Untitled Process'}</p>
                <p className="text-[10px] text-slate-500 line-clamp-3">{data.description || 'No description provided.'}</p>
             </div>
          </div>

          <div className="space-y-4">
             <div className="flex items-center justify-between">
               <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Stage Topology</h4>
               <Badge className="bg-side-b/10 text-side-b border-none text-[8px] font-bold uppercase tracking-tighter">Verified</Badge>
             </div>
             <div className="space-y-4 relative">
               <div className="absolute left-[11px] top-2 bottom-2 w-0.5 bg-slate-100" />
               {(data.stages?.length > 0 ? data.stages : [1,2,3]).map((s, i) => (
                 <div key={i} className="flex items-start space-x-4 relative">
                    <div className="h-6 w-6 rounded-full bg-slate-100 border-2 border-white shadow-sm flex items-center justify-center text-[10px] font-bold text-slate-400 z-10">{i + 1}</div>
                    <div className="flex-1">
                      <div className={cn("h-3 w-24 rounded mb-1 bg-slate-200", !data.stages?.length && "animate-pulse")} />
                      <div className={cn("h-2 w-full rounded bg-slate-100", !data.stages?.length && "animate-pulse")} />
                    </div>
                 </div>
               ))}
             </div>
          </div>
        </div>
        <div className="p-4 border-t bg-slate-50/50">
          <Button variant="outline" className="w-full text-[10px] font-bold h-9 uppercase tracking-widest hover:bg-white transition-all shadow-sm">
            View Source Spec (JSON)
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProcessModelStudio;
