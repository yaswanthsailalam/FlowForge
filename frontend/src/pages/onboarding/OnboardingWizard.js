import React, { useState, useEffect } from 'react';
import {
  Building2,
  CheckCircle2,
  ArrowRight,
  ChevronLeft,
  Globe,
  Users,
  Package,
  ShieldCheck,
  Rocket,
  Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { useNavigate } from 'react-router-dom';

const OnboardingWizard = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const totalSteps = 4;

  // Simulate resuming onboarding from localStorage/API
  useEffect(() => {
    const savedStep = localStorage.getItem('onboarding_step');
    if (savedStep) setStep(parseInt(savedStep));
  }, []);

  const nextStep = () => {
    const next = Math.min(totalSteps, step + 1);
    setStep(next);
    localStorage.setItem('onboarding_step', next.toString());
  };

  const prevStep = () => {
    const prev = Math.max(1, step - 1);
    setStep(prev);
    localStorage.setItem('onboarding_step', prev.toString());
  };

  const handleFinish = async () => {
     setLoading(true);
     // In a real app: await orgService.completeOnboarding(orgId);
     setTimeout(() => {
        localStorage.removeItem('onboarding_step');
        navigate('/dashboard');
     }, 1000);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center space-y-2">
           <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-white shadow-lg mb-4">
              <Rocket className="h-6 w-6" />
           </div>
           <h1 className="text-3xl font-bold tracking-tight text-slate-900">Organisation Setup</h1>
           <p className="text-slate-500">Resume your setup and establish your operational foundation.</p>
        </div>

        <div className="space-y-2">
           <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-slate-400">
              <span>Step {step} of {totalSteps}</span>
              <span>{Math.round((step / totalSteps) * 100)}% Complete</span>
           </div>
           <Progress value={(step / totalSteps) * 100} className="h-2 bg-slate-200" />
        </div>

        <Card className="border-none shadow-2xl shadow-slate-200/60 overflow-hidden">
          <CardContent className="p-10">
            {step === 1 && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="space-y-2 text-center pb-4">
                   <h2 className="text-xl font-bold">Organisation Profile</h2>
                   <p className="text-sm text-slate-500">Provide your basic corporate details.</p>
                </div>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-xs font-bold uppercase text-slate-400">Legal Entity Name</Label>
                    <Input placeholder="e.g., Acme Health Systems" className="h-12 text-lg font-medium" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-xs font-bold uppercase text-slate-400">Primary Industry</Label>
                      <Select><SelectTrigger className="h-11"><SelectValue placeholder="Select..." /></SelectTrigger>
                        <SelectContent><SelectItem value="health">Healthcare</SelectItem></SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs font-bold uppercase text-slate-400">Region</Label>
                      <Select><SelectTrigger className="h-11"><SelectValue placeholder="Select..." /></SelectTrigger>
                        <SelectContent><SelectItem value="na">North America</SelectItem></SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="space-y-2 text-center pb-4">
                   <h2 className="text-xl font-bold">Initial Workspace</h2>
                   <p className="text-sm text-slate-500">Establish your first secure operating space.</p>
                </div>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-xs font-bold uppercase text-slate-400">Workspace Label</Label>
                    <Input placeholder="e.g., North Region Operations" className="h-12" />
                  </div>
                  <div className="p-4 bg-primary/5 rounded-lg border border-primary/10 flex items-start space-x-3 text-xs text-slate-600">
                     <ShieldCheck className="h-5 w-5 text-primary flex-shrink-0" />
                     <p>Workspaces provide strict data isolation between departments or regions while inheriting global policies.</p>
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="space-y-2 text-center pb-4">
                   <h2 className="text-xl font-bold">Feature Entitlements</h2>
                   <p className="text-sm text-slate-500">Select standard capabilities for your trial.</p>
                </div>
                <div className="grid grid-cols-1 gap-3">
                   {['Process Model Studio', 'Workflow Engine', 'AI Governance'].map((p, i) => (
                     <div key={i} className="flex items-center p-4 border rounded-xl bg-white shadow-sm hover:border-primary transition-colors cursor-pointer">
                        <div className="h-10 w-10 rounded-lg bg-slate-100 flex items-center justify-center mr-4"><Package className="h-5 w-5 text-slate-400" /></div>
                        <div className="flex-1"><p className="text-sm font-bold text-slate-900">{p}</p></div>
                        <div className="h-5 w-5 rounded-full border-2 border-slate-200" />
                     </div>
                   ))}
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-8 text-center animate-in zoom-in duration-500">
                <div className="flex justify-center"><div className="h-20 w-20 bg-success/10 text-success rounded-full flex items-center justify-center"><CheckCircle2 className="h-10 w-10" /></div></div>
                <div className="space-y-2"><h2 className="text-2xl font-bold">Configuration Complete</h2><p className="text-slate-500 max-w-sm mx-auto">Your organisation is provisioned and your Enterprise Trial has been activated.</p></div>
              </div>
            )}

            <div className="flex items-center justify-between mt-12 pt-8 border-t">
               <Button variant="ghost" onClick={prevStep} disabled={step === 1 || loading} className="font-bold text-slate-500 uppercase tracking-widest text-[10px]">
                 <ChevronLeft className="mr-2 h-4 w-4" /> Back
               </Button>
               {step < totalSteps ? (
                 <Button onClick={nextStep} disabled={loading} className="bg-primary hover:bg-primary/90 px-8 font-bold uppercase tracking-widest text-[10px]">
                    Continue <ArrowRight className="ml-2 h-4 w-4" />
                 </Button>
               ) : (
                 <Button onClick={handleFinish} disabled={loading} className="bg-success hover:bg-success/90 px-10 font-bold uppercase tracking-widest text-[10px] shadow-lg shadow-success/20">
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Enter Workspace'}
                    {!loading && <Rocket className="ml-2 h-4 w-4" />}
                 </Button>
               )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default OnboardingWizard;
