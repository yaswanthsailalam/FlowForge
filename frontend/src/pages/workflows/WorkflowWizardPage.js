import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import WorkflowWizard from '@/components/workflow/WorkflowWizard';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, Save } from 'lucide-react';

const WorkflowWizardPage = () => {
  const { workflowId } = useParams();
  const navigate = useNavigate();
  const [draft, setDraft] = useState(null);

  return (
    <div className="container mx-auto py-6 px-4 h-[calc(100vh-120px)] flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/workflows')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Configure Workflow</h1>
            <p className="text-sm text-muted-foreground">{draft?.name || 'Loading...'}</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <WorkflowWizard
          workflowId={workflowId}
          onSave={(data) => setDraft(data)}
          onValidate={(data) => {
            console.log("Validated", data);
          }}
        />
      </div>
    </div>
  );
};

export default WorkflowWizardPage;
