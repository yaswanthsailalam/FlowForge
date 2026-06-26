import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { ChevronLeft, ChevronRight, Save, CheckCircle, AlertCircle, Loader2, Plus, Trash2, GripVertical, Settings2, Bell, Ban, Flag, Eye } from 'lucide-react';
import workflowService from '@/services/workflowService';
import catalogueService from '@/services/catalogueService';
import { useToast } from '@/hooks/use-toast';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

const SECTIONS = [
  { id: 'details', title: 'Details' },
  { id: 'ownership', title: 'Ownership' },
  { id: 'trigger', title: 'Trigger' },
  { id: 'inputs', title: 'Inputs & Documents' },
  { id: 'stages', title: 'Stages & Steps' },
  { id: 'approvals', title: 'Approvals' },
  { id: 'conditions', title: 'Conditions' },
  { id: 'notifications', title: 'Notifications' },
  { id: 'exceptions', title: 'Exceptions' },
  { id: 'review', title: 'Review' },
];

const STEP_TYPES = [
  { value: 'form_input', label: 'Form Input' },
  { value: 'manual_task', label: 'Manual Task' },
  { value: 'review', label: 'Review' },
  { value: 'approval', label: 'Approval' },
  { value: 'condition', label: 'Condition' },
  { value: 'notification', label: 'Notification' },
  { value: 'data_write', label: 'Data Write' },
  { value: 'integration_action', label: 'Integration Action' },
  { value: 'document_request', label: 'Document Request' },
  { value: 'document_verification', label: 'Document Verification' },
  { value: 'assignment', label: 'Assignment' },
  { value: 'wait', label: 'Wait' },
  { value: 'end', label: 'End' },
];

const WorkflowWizard = ({ workflowId, onSave, onValidate }) => {
  const [currentSectionIdx, setCurrentSectionIdx] = useState(0);
  const [draft, setDraft] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [teams, setTeams] = useState([]);
  const { toast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [draftRes, deptsRes] = await Promise.all([
          workflowService.getDraft(workflowId),
          catalogueService.getDepartments()
        ]);
        setDraft(draftRes.data);
        setDepartments(deptsRes.data);
      } catch (err) {
        console.error("Failed to fetch wizard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [workflowId]);

  useEffect(() => {
    if (draft?.owning_department) {
      catalogueService.getTeams(draft.owning_department).then(res => setTeams(res.data));
    }
  }, [draft?.owning_department]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await workflowService.updateDraft(workflowId, draft);
      setDirty(false);
      toast({
        title: "Draft saved",
        description: "Your changes have been saved successfully.",
      });
      if (onSave) onSave(draft);
    } catch (err) {
      toast({
        title: "Save failed",
        description: "There was an error saving your changes.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async () => {
    setValidating(true);
    try {
      await workflowService.updateDraft(workflowId, draft);
      const res = await workflowService.validateDraft(workflowId);
      setDraft(prev => ({
        ...prev,
        validation_results: res.data.issues,
        validation_status: res.data.validation_status
      }));
      toast({
        title: "Validation complete",
        description: res.data.validation_status === 'valid' ? "No critical issues found." : "Validation failed. Please check issues.",
        variant: res.data.validation_status === 'valid' ? "default" : "destructive",
      });
      if (onValidate) onValidate(res.data);
    } catch (err) {
      toast({
        title: "Validation error",
        description: "Failed to validate workflow.",
        variant: "destructive",
      });
    } finally {
      setValidating(false);
    }
  };

  const next = () => {
    if (currentSectionIdx < SECTIONS.length - 1) {
      setCurrentSectionIdx(currentSectionIdx + 1);
    }
  };

  const prev = () => {
    if (currentSectionIdx > 0) {
      setCurrentSectionIdx(currentSectionIdx - 1);
    }
  };

  const updateDraft = (updates) => {
    setDraft(prev => ({ ...prev, ...updates }));
    setDirty(true);
  };

  const updateDefinition = (updates) => {
    setDraft(prev => ({
      ...prev,
      definition: { ...prev.definition, ...updates }
    }));
    setDirty(true);
  };

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="animate-spin" /></div>;
  if (!draft) return <div>Draft not found.</div>;

  const currentSection = SECTIONS[currentSectionIdx];

  const renderSection = () => {
    const definition = draft.definition;
    switch (currentSection.id) {
      case 'details':
        return (
          <div className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Workflow Name</Label>
              <Input
                id="name"
                value={draft.name || ''}
                onChange={(e) => updateDraft({ name: e.target.value })}
                placeholder="e.g. Employee Onboarding"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                rows={4}
                value={draft.description || ''}
                onChange={(e) => updateDraft({ description: e.target.value })}
                placeholder="Describe the purpose of this workflow..."
              />
            </div>
          </div>
        );
      case 'ownership':
        return (
          <div className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="department">Owning Department</Label>
              <Select
                value={draft.owning_department || ''}
                onValueChange={(val) => updateDraft({ owning_department: val })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map(d => (
                    <SelectItem key={d.department_id} value={d.department_id}>{d.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="owner_role">Workflow Owner Role</Label>
              <Input
                id="owner_role"
                value={draft.workflow_owner_role || ''}
                onChange={(e) => updateDraft({ workflow_owner_role: e.target.value })}
                placeholder="e.g. HR Manager"
              />
            </div>
          </div>
        );
      case 'trigger':
        const trigger = definition.trigger || {};
        return (
          <div className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="trigger_type">Trigger Type</Label>
              <Select
                value={trigger.type || 'manual'}
                onValueChange={(val) => updateDefinition({ trigger: { ...trigger, type: val } })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="manual">Manual</SelectItem>
                  <SelectItem value="form_submission">Form Submission</SelectItem>
                  <SelectItem value="scheduled">Scheduled</SelectItem>
                  <SelectItem value="api">API</SelectItem>
                  <SelectItem value="webhook">Webhook (Placeholder)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="trigger_name">Trigger Name</Label>
              <Input
                id="trigger_name"
                value={trigger.name || ''}
                onChange={(e) => updateDefinition({ trigger: { ...trigger, name: e.target.value } })}
              />
            </div>
          </div>
        );
      case 'inputs':
        const inputs = definition.inputs || [];
        return (
          <div className="space-y-6">
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Input Definitions</h3>
                <Button variant="outline" size="sm" onClick={() => {
                  const newInputs = [...inputs, { key: `input_${inputs.length + 1}`, label: 'New Input', data_type: 'string', required: true }];
                  updateDefinition({ inputs: newInputs });
                }}>
                  <Plus className="mr-2 h-4 w-4" /> Add Input
                </Button>
              </div>
              <div className="space-y-4">
                {inputs.map((input, idx) => (
                  <Card key={idx}>
                    <CardContent className="pt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="grid gap-2">
                        <Label>Key</Label>
                        <Input value={input.key} onChange={(e) => {
                          const newInputs = [...inputs];
                          newInputs[idx].key = e.target.value;
                          updateDefinition({ inputs: newInputs });
                        }} />
                      </div>
                      <div className="grid gap-2">
                        <Label>Label</Label>
                        <Input value={input.label} onChange={(e) => {
                          const newInputs = [...inputs];
                          newInputs[idx].label = e.target.value;
                          updateDefinition({ inputs: newInputs });
                        }} />
                      </div>
                      <div className="flex items-end justify-between">
                         <div className="grid gap-2 flex-1 mr-4">
                          <Label>Type</Label>
                          <Select value={input.data_type} onValueChange={(val) => {
                            const newInputs = [...inputs];
                            newInputs[idx].data_type = val;
                            updateDefinition({ inputs: newInputs });
                          }}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                              <SelectItem value="string">String</SelectItem>
                              <SelectItem value="number">Number</SelectItem>
                              <SelectItem value="boolean">Boolean</SelectItem>
                              <SelectItem value="date">Date</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <Button variant="ghost" size="icon" className="text-red-500" onClick={() => {
                          updateDefinition({ inputs: inputs.filter((_, i) => i !== idx) });
                        }}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        );
      case 'stages':
        const stages = definition.stages || [];
        const steps = definition.steps || [];
        return (
          <div className="space-y-8">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">Stages & Steps</h3>
              <Button variant="outline" size="sm" onClick={() => {
                const newStages = [...stages, { stage_id: `stage_${stages.length + 1}`, name: 'New Stage', sequence: stages.length + 1 }];
                updateDefinition({ stages: newStages });
              }}>
                <Plus className="mr-2 h-4 w-4" /> Add Stage
              </Button>
            </div>

            {stages.sort((a, b) => a.sequence - b.sequence).map((stage, sIdx) => {
              const stageSteps = steps.filter(s => s.stage_id === stage.stage_id);
              return (
                <div key={stage.stage_id} className="border rounded-lg p-4 bg-gray-50/50">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <GripVertical className="h-4 w-4 text-gray-400" />
                      <Input
                        className="font-bold bg-transparent border-none p-0 focus-visible:ring-0 w-auto text-lg"
                        value={stage.name}
                        onChange={(e) => {
                          const newStages = [...stages];
                          newStages[sIdx].name = e.target.value;
                          updateDefinition({ stages: newStages });
                        }}
                      />
                      <Badge variant="outline">{stageSteps.length} Steps</Badge>
                    </div>
                    <div className="flex gap-2">
                       <Button variant="ghost" size="sm" className="text-red-500" onClick={() => {
                        updateDefinition({
                          stages: stages.filter(s => s.stage_id !== stage.stage_id),
                          steps: steps.filter(s => s.stage_id !== stage.stage_id)
                        });
                      }}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-3 ml-6">
                    {stageSteps.map((step, stIdx) => (
                      <Card key={step.step_id} className="bg-white">
                        <CardContent className="p-3 flex items-center justify-between">
                          <div className="flex items-center gap-3 flex-1">
                             <Badge variant="secondary" className="uppercase text-[10px]">{step.step_type.replace('_', ' ')}</Badge>
                             <Input
                                className="bg-transparent border-none p-0 h-auto focus-visible:ring-0 font-medium"
                                value={step.name}
                                onChange={(e) => {
                                  const newSteps = [...steps];
                                  const idx = steps.findIndex(s => s.step_id === step.step_id);
                                  newSteps[idx].name = e.target.value;
                                  updateDefinition({ steps: newSteps });
                                }}
                             />
                          </div>
                          <div className="flex items-center gap-2">
                             <Select value={step.step_type} onValueChange={(val) => {
                                const newSteps = [...steps];
                                const idx = steps.findIndex(s => s.step_id === step.step_id);
                                newSteps[idx].step_type = val;
                                updateDefinition({ steps: newSteps });
                             }}>
                               <SelectTrigger className="h-8 w-32 text-xs"><SelectValue /></SelectTrigger>
                               <SelectContent>
                                  {STEP_TYPES.map(st => <SelectItem key={st.value} value={st.value}>{st.label}</SelectItem>)}
                               </SelectContent>
                             </Select>
                             <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500" onClick={() => {
                               updateDefinition({ steps: steps.filter(s => s.step_id !== step.step_id) });
                             }}>
                               <Trash2 className="h-4 w-4" />
                             </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                    <Button variant="dashed" className="w-full h-10 border-gray-300 text-gray-500 hover:text-gray-700" onClick={() => {
                      const newSteps = [...steps, {
                        step_id: `step_${steps.length + 1}`,
                        name: 'New Step',
                        step_type: 'manual_task',
                        stage_id: stage.stage_id,
                        transitions: {}
                      }];
                      updateDefinition({ steps: newSteps });
                    }}>
                      <Plus className="mr-2 h-4 w-4" /> Add Step to Stage
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        );
      case 'approvals':
        const approvals = definition.approvals || [];
        return (
          <div className="space-y-6">
             <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">Approval Points</h3>
              <Button variant="outline" size="sm" onClick={() => {
                const newApprovals = [...approvals, {
                  approval_id: `appr_${approvals.length + 1}`,
                  name: 'New Approval',
                  approver_role: '',
                  outcomes: ['approved', 'rejected']
                }];
                updateDefinition({ approvals: newApprovals });
              }}>
                <Plus className="mr-2 h-4 w-4" /> Add Approval Point
              </Button>
            </div>
            <div className="space-y-4">
              {approvals.map((appr, idx) => (
                <Card key={appr.approval_id}>
                  <CardContent className="pt-4 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="grid gap-2">
                        <Label>Approval Name</Label>
                        <Input value={appr.name} onChange={(e) => {
                           const newA = [...approvals];
                           newA[idx].name = e.target.value;
                           updateDefinition({ approvals: newA });
                        }} />
                      </div>
                      <div className="grid gap-2">
                        <Label>Approver Role</Label>
                        <Input value={appr.approver_role} onChange={(e) => {
                           const newA = [...approvals];
                           newA[idx].approver_role = e.target.value;
                           updateDefinition({ approvals: newA });
                        }} />
                      </div>
                    </div>
                    <div className="flex justify-end">
                      <Button variant="ghost" size="sm" className="text-red-500" onClick={() => {
                         updateDefinition({ approvals: approvals.filter((_, i) => i !== idx) });
                      }}>
                        <Trash2 className="mr-2 h-4 w-4" /> Remove Approval
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              {approvals.length === 0 && <p className="text-muted-foreground italic text-center py-8 border rounded-lg border-dashed">No approvals configured.</p>}
            </div>
          </div>
        );
      case 'conditions':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium">Transitions & Decisions</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Configure how the workflow flows between steps based on outcomes or conditions.
            </p>
            {definition.steps.filter(s => s.step_type !== 'end').map((step, idx) => (
               <Card key={step.step_id} className="mb-4">
                 <CardHeader className="py-3 px-4 bg-gray-50 border-b">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                       <Settings2 className="h-4 w-4" />
                       Transitions for: {step.name}
                    </CardTitle>
                 </CardHeader>
                 <CardContent className="p-4 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                       <div className="grid gap-2">
                          <Label className="text-xs uppercase text-gray-500">Success / Approved Path</Label>
                          <Select
                            value={step.transitions?.success || ''}
                            onValueChange={(val) => {
                               const newSteps = [...definition.steps];
                               const sIdx = newSteps.findIndex(s => s.step_id === step.step_id);
                               newSteps[sIdx].transitions = { ...newSteps[sIdx].transitions, success: val };
                               updateDefinition({ steps: newSteps });
                            }}
                          >
                             <SelectTrigger><SelectValue placeholder="Next step..." /></SelectTrigger>
                             <SelectContent>
                                {definition.steps.filter(s => s.step_id !== step.step_id).map(s => (
                                   <SelectItem key={s.step_id} value={s.step_id}>{s.name}</SelectItem>
                                ))}
                             </SelectContent>
                          </Select>
                       </div>
                       {(step.step_type === 'approval' || step.step_type === 'condition') && (
                          <div className="grid gap-2">
                             <Label className="text-xs uppercase text-gray-500">Rejection / Failure Path</Label>
                             <Select
                                value={step.transitions?.rejection || step.transitions?.failure || ''}
                                onValueChange={(val) => {
                                   const newSteps = [...definition.steps];
                                   const sIdx = newSteps.findIndex(s => s.step_id === step.step_id);
                                   const key = step.step_type === 'approval' ? 'rejection' : 'failure';
                                   newSteps[sIdx].transitions = { ...newSteps[sIdx].transitions, [key]: val };
                                   updateDefinition({ steps: newSteps });
                                }}
                             >
                                <SelectTrigger><SelectValue placeholder="Next step..." /></SelectTrigger>
                                <SelectContent>
                                   {definition.steps.filter(s => s.step_id !== step.step_id).map(s => (
                                      <SelectItem key={s.step_id} value={s.step_id}>{s.name}</SelectItem>
                                   ))}
                                </SelectContent>
                             </Select>
                          </div>
                       )}
                    </div>
                 </CardContent>
               </Card>
            ))}
          </div>
        );
      case 'notifications':
        const notifications = definition.notifications || [];
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">Notifications (Placeholders)</h3>
              <Button variant="outline" size="sm" onClick={() => {
                const newN = [...notifications, {
                  notification_id: `notif_${notifications.length + 1}`,
                  name: 'New Notification',
                  trigger_event: 'run_started',
                  recipient_role: '',
                  title_template: 'Workflow Alert',
                  message_template: 'A workflow event has occurred.'
                }];
                updateDefinition({ notifications: newN });
              }}>
                <Plus className="mr-2 h-4 w-4" /> Add Notification
              </Button>
            </div>
            <div className="space-y-4">
              {notifications.map((notif, idx) => (
                <Card key={notif.notification_id}>
                  <CardContent className="pt-4 grid gap-4">
                    <div className="grid grid-cols-2 gap-4">
                       <div className="grid gap-2">
                          <Label>Notification Name</Label>
                          <Input value={notif.name} onChange={(e) => {
                             const newN = [...notifications];
                             newN[idx].name = e.target.value;
                             updateDefinition({ notifications: newN });
                          }} />
                       </div>
                       <div className="grid gap-2">
                          <Label>Recipient Role</Label>
                          <Input value={notif.recipient_role} onChange={(e) => {
                             const newN = [...notifications];
                             newN[idx].recipient_role = e.target.value;
                             updateDefinition({ notifications: newN });
                          }} />
                       </div>
                    </div>
                    <div className="flex justify-end">
                      <Button variant="ghost" size="sm" className="text-red-500" onClick={() => {
                         updateDefinition({ notifications: notifications.filter((_, i) => i !== idx) });
                      }}>
                        <Trash2 className="mr-2 h-4 w-4" /> Remove Notification
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              {notifications.length === 0 && <p className="text-muted-foreground italic text-center py-8 border rounded-lg border-dashed">No notifications configured.</p>}
            </div>
          </div>
        );
      case 'exceptions':
        const completion = definition.completion || { valid_states: ['completed'] };
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium">Exceptions & Completion</h3>
            <div className="grid gap-4 border rounded-lg p-4">
               <div className="grid gap-2">
                  <Label>Cancellation Behaviour</Label>
                  <Select value={completion.cancellation_behaviour} onValueChange={(val) => updateDefinition({ completion: { ...completion, cancellation_behaviour: val } })}>
                     <SelectTrigger><SelectValue /></SelectTrigger>
                     <SelectContent>
                        <SelectItem value="cancel_pending">Cancel all pending steps</SelectItem>
                        <SelectItem value="keep_running">Keep other branches running</SelectItem>
                     </SelectContent>
                  </Select>
               </div>
               <div className="grid gap-2">
                  <Label>Incomplete Data Behaviour</Label>
                  <Select value={completion.incomplete_data_behaviour} onValueChange={(val) => updateDefinition({ completion: { ...completion, incomplete_data_behaviour: val } })}>
                     <SelectTrigger><SelectValue /></SelectTrigger>
                     <SelectContent>
                        <SelectItem value="allow_completion">Allow completion with missing data</SelectItem>
                        <SelectItem value="prevent_completion">Prevent completion until data supplied</SelectItem>
                     </SelectContent>
                  </Select>
               </div>
            </div>
          </div>
        );
      case 'review':
        const issues = draft.validation_results || [];
        const criticalIssues = issues.filter(i => i.severity === 'critical');
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium">Review & Validate</h3>
            <div className="grid gap-4">
               <Card className={draft.validation_status === 'valid' ? 'border-green-200 bg-green-50' : draft.validation_status === 'invalid' ? 'border-red-200 bg-red-50' : ''}>
                  <CardContent className="pt-6 flex items-center justify-between">
                     <div className="flex items-center gap-3">
                        {draft.validation_status === 'valid' ? (
                           <CheckCircle className="h-8 w-8 text-green-600" />
                        ) : draft.validation_status === 'invalid' ? (
                           <AlertCircle className="h-8 w-8 text-red-600" />
                        ) : (
                           <Loader2 className="h-8 w-8 text-gray-400" />
                        )}
                        <div>
                           <p className="font-bold">Status: {draft.validation_status?.replace('_', ' ').toUpperCase() || 'NOT VALIDATED'}</p>
                           <p className="text-sm text-muted-foreground">
                              {criticalIssues.length} critical issues, {issues.length - criticalIssues.length} warnings.
                           </p>
                        </div>
                     </div>
                     <Button onClick={handleValidate} disabled={validating}>
                        {validating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Flag className="mr-2 h-4 w-4" />}
                        Run Validation
                     </Button>
                  </CardContent>
               </Card>

               {issues.length > 0 && (
                  <div className="space-y-2">
                     <h4 className="font-medium">Validation Issues</h4>
                     {issues.map((issue, idx) => (
                        <div
                          key={idx}
                          className={`p-3 rounded border text-sm flex items-start gap-3 cursor-pointer hover:bg-muted transition-colors ${
                            issue.severity === 'critical' ? 'border-red-200 bg-red-50' : 'border-amber-200 bg-amber-50'
                          }`}
                          onClick={() => {
                             const sectionIdx = SECTIONS.findIndex(s => s.id === issue.section);
                             if (sectionIdx !== -1) setCurrentSectionIdx(sectionIdx);
                          }}
                        >
                           {issue.severity === 'critical' ? <Ban className="h-4 w-4 text-red-600 mt-0.5" /> : <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5" />}
                           <div>
                              <p className="font-medium capitalize">{issue.section}: {issue.message}</p>
                              {issue.correction && <p className="text-xs text-muted-foreground mt-1">Suggested: {issue.correction}</p>}
                           </div>
                        </div>
                     ))}
                  </div>
               )}
            </div>
          </div>
        );
      default:
        return <div className="text-muted-foreground italic">Section content for {currentSection.id} is under development.</div>;
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Progress Bar */}
      <div className="w-full bg-gray-200 h-2 mb-6 rounded-full overflow-hidden">
        <div
          className="bg-primary h-full transition-all duration-300"
          style={{ width: `${((currentSectionIdx + 1) / SECTIONS.length) * 100}%` }}
        />
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        {/* Sidebar Navigation */}
        <div className="w-64 flex-shrink-0 hidden md:block overflow-y-auto">
          <nav className="space-y-1">
            {SECTIONS.map((section, idx) => (
              <button
                key={section.id}
                onClick={() => setCurrentSectionIdx(idx)}
                className={`w-full text-left px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  idx === currentSectionIdx
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted'
                }`}
              >
                {idx + 1}. {section.title}
              </button>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Card className="flex-1 overflow-y-auto">
            <CardContent className="pt-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">{currentSection.title}</h2>
                <Button variant="ghost" size="sm" asChild>
                   <a href={`/workflows/preview/${workflowId}`} target="_blank" rel="noreferrer">
                      <Eye className="mr-2 h-4 w-4" /> Preview
                   </a>
                </Button>
              </div>
              {renderSection()}
            </CardContent>
          </Card>

          {/* Footer Navigation */}
          <div className="flex justify-between items-center mt-6 py-4 border-t">
            <Button variant="outline" onClick={prev} disabled={currentSectionIdx === 0}>
              <ChevronLeft className="mr-2 h-4 w-4" /> Previous
            </Button>

            <div className="flex gap-2">
              <Button variant="outline" onClick={handleSave} disabled={!dirty || saving}>
                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                Save Draft
              </Button>
              {currentSectionIdx === SECTIONS.length - 1 ? (
                <Button className="bg-green-600 hover:bg-green-700" onClick={handleValidate} disabled={validating}>
                  {validating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <CheckCircle className="mr-2 h-4 w-4" />}
                  Finalize & Validate
                </Button>
              ) : (
                <Button onClick={next}>
                  Next <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowWizard;
