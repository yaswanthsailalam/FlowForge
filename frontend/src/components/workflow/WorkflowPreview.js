import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2, ArrowLeft, Printer, Globe, Lock, Shield, Layers, Layout, Bell, Zap, Play, FileText, User, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import workflowService from '@/services/workflowService';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

const WorkflowPreview = () => {
  const { workflowId } = useParams();
  const navigate = useNavigate();
  const [draft, setDraft] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDraft = async () => {
      try {
        const res = await workflowService.getDraft(workflowId);
        setDraft(res.data);
      } catch (err) {
        console.error("Failed to fetch draft for preview", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDraft();
  }, [workflowId]);

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="animate-spin" /></div>;
  if (!draft) return <div className="container mx-auto py-10 text-center">Draft not found.</div>;

  const { definition } = draft;

  return (
    <div className="container mx-auto py-8 px-4 max-w-5xl">
      <div className="flex justify-between items-center mb-8 no-print">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Editor
        </Button>
        <div className="flex gap-2">
           <Button variant="outline" onClick={() => window.print()}>
              <Printer className="mr-2 h-4 w-4" /> Print Definition
           </Button>
        </div>
      </div>

      <div className="space-y-8 print:space-y-4">
        {/* Header Information */}
        <section>
          <div className="flex items-start justify-between mb-2">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight mb-2">{draft.name}</h1>
              <p className="text-xl text-muted-foreground">{draft.description}</p>
            </div>
            <Badge variant={draft.validation_status === 'valid' ? 'default' : 'outline'} className="text-lg py-1 px-4">
               {draft.validation_status?.toUpperCase() || 'DRAFT'}
            </Badge>
          </div>
          <div className="flex flex-wrap gap-4 mt-6">
            <div className="flex items-center gap-2 px-3 py-1 bg-muted rounded-full text-sm">
              <Shield className="h-4 w-4" />
              <span>Owner: {draft.workflow_owner_role || 'Not set'}</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-muted rounded-full text-sm">
              <Globe className="h-4 w-4" />
              <span>Source: {draft.source_type}</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-muted rounded-full text-sm">
              <Zap className="h-4 w-4" />
              <span>Trigger: {definition.trigger?.name || 'Manual'} ({definition.trigger?.type})</span>
            </div>
          </div>
        </section>

        <Separator />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
           <div className="md:col-span-2 space-y-8">
              {/* Stages and Steps */}
              <section>
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <Layers className="h-6 w-6 text-primary" />
                  Workflow Structure
                </h2>
                <div className="space-y-6">
                   {definition.stages.sort((a,b) => a.sequence - b.sequence).map(stage => (
                      <div key={stage.stage_id} className="relative pl-8 border-l-2 border-primary/20 pb-4 last:pb-0">
                         <div className="absolute -left-[9px] top-0 h-4 w-4 rounded-full bg-primary" />
                         <h3 className="text-lg font-bold mb-3">{stage.name}</h3>
                         <div className="space-y-3">
                            {definition.steps.filter(s => s.stage_id === stage.stage_id).map(step => (
                               <Card key={step.step_id} className="shadow-sm">
                                  <CardHeader className="py-3 px-4 flex flex-row items-center justify-between space-y-0">
                                     <div className="flex items-center gap-2">
                                        <Badge variant="outline" className="text-[10px] uppercase font-bold">{step.step_type.replace('_', ' ')}</Badge>
                                        <span className="font-semibold">{step.name}</span>
                                     </div>
                                     <div className="text-xs text-muted-foreground flex items-center gap-1">
                                        <User className="h-3 w-3" /> {step.assigned_role || 'System'}
                                     </div>
                                  </CardHeader>
                                  {step.transitions && Object.keys(step.transitions).length > 0 && (
                                     <CardContent className="py-2 px-4 bg-muted/30 border-t text-[10px] flex gap-4">
                                        {Object.entries(step.transitions).map(([key, target]) => (
                                           <div key={key} className="flex items-center gap-1">
                                              <span className="font-bold uppercase text-gray-500">{key}:</span>
                                              <span>{definition.steps.find(s => s.step_id === target)?.name || target}</span>
                                           </div>
                                        ))}
                                     </CardContent>
                                  )}
                               </Card>
                            ))}
                         </div>
                      </div>
                   ))}
                </div>
              </section>

              {/* Approvals */}
              {definition.approvals?.length > 0 && (
                <section>
                  <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                    <CheckCircle2 className="h-6 w-6 text-green-600" />
                    Approval Requirements
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                     {definition.approvals.map(appr => (
                        <Card key={appr.approval_id}>
                           <CardContent className="pt-6">
                              <p className="font-bold">{appr.name}</p>
                              <p className="text-sm text-muted-foreground mt-1">Approver: {appr.approver_role}</p>
                           </CardContent>
                        </Card>
                     ))}
                  </div>
                </section>
              )}
           </div>

           <div className="space-y-8">
              {/* Inputs */}
              <section>
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Required Inputs
                </h2>
                <div className="space-y-2">
                   {definition.inputs.map(input => (
                      <div key={input.key} className="flex justify-between items-center p-2 border-b text-sm">
                         <div>
                            <p className="font-medium">{input.label}</p>
                            <p className="text-[10px] text-muted-foreground font-mono">{input.key}</p>
                         </div>
                         <Badge variant="outline" className="text-[10px]">{input.data_type}</Badge>
                      </div>
                   ))}
                </div>
              </section>

              {/* Notifications */}
              {definition.notifications?.length > 0 && (
                <section>
                   <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Bell className="h-5 w-5 text-amber-500" />
                    Notifications
                  </h2>
                  <div className="space-y-2">
                     {definition.notifications.map(notif => (
                        <div key={notif.notification_id} className="p-2 border rounded-md text-sm">
                           <p className="font-medium">{notif.name}</p>
                           <p className="text-xs text-muted-foreground mt-1">To: {notif.recipient_role}</p>
                        </div>
                     ))}
                  </div>
                </section>
              )}

              {/* Validation Status Summary */}
              <section className="bg-muted p-4 rounded-lg no-print">
                 <h2 className="font-bold mb-2 flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    Integrity Check
                 </h2>
                 <div className="space-y-2">
                    {draft.validation_results?.length > 0 ? (
                       draft.validation_results.map((issue, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-xs">
                             {issue.severity === 'critical' ? (
                                <XCircle className="h-3 w-3 text-red-500 mt-0.5" />
                             ) : (
                                <AlertTriangle className="h-3 w-3 text-amber-500 mt-0.5" />
                             )}
                             <span>{issue.message}</span>
                          </div>
                       ))
                    ) : (
                       <div className="flex items-center gap-2 text-xs text-green-600">
                          <CheckCircle2 className="h-3 w-3" />
                          <span>Definition is consistent and valid.</span>
                       </div>
                    )}
                 </div>
              </section>
           </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowPreview;
