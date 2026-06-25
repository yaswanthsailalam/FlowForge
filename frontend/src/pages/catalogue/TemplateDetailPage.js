import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import catalogueService from '@/services/catalogueService';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Loader2, ArrowLeft, Layout, FileText, CheckCircle, Info } from 'lucide-react';
import { useWorkspace } from '@/contexts/WorkspaceContext';

const TemplateDetailPage = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const { membership } = useWorkspace();
  const [template, setTemplate] = useState(null);
  const [baseModel, setBaseModel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTemplateData = async () => {
      try {
        const tempRes = await catalogueService.getWorkflowTemplate(templateId);
        setTemplate(tempRes.data);

        const modelRes = await catalogueService.getProcessModel(tempRes.data.process_model_id);
        setBaseModel(modelRes.data);
      } catch (err) {
        console.error("Failed to fetch template details", err);
        setError(err.response?.status === 403 ? "Access Denied" : "Failed to load template");
      } finally {
        setLoading(false);
      }
    };
    fetchTemplateData();
  }, [templateId]);

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="animate-spin" /></div>;
  if (error) return <div className="container mx-auto py-10 text-center text-red-500">{error}</div>;

  const isArchitect = membership?.role === 'workspace_admin' || membership?.role === 'process_architect';
  const isWorkspaceTemplate = template?.workspace_id !== null;

  return (
    <div className="container mx-auto py-6 px-4">
      <div className="flex items-center gap-2 mb-6 text-sm text-gray-500">
        <Link to="/processes" className="hover:text-blue-600">Catalogue</Link>
        <span>/</span>
        <Link to={`/processes/${baseModel?.model_id}`} className="hover:text-blue-600">{baseModel?.name}</Link>
        <span>/</span>
        <span className="font-medium text-gray-900">{template.name}</span>
      </div>

      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back
      </Button>

      <div className="bg-white rounded-lg border shadow-sm p-8 mb-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold">{template.name}</h1>
              <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">Template</Badge>
            </div>
            <p className="text-gray-500 mt-1">{template.description}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Badge variant="secondary">{template.publication_status}</Badge>
            <span className="text-xs text-gray-400">Version {template.version}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-lg">Template Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-sm font-semibold mb-2">Base Process Model</h3>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                   <div className="flex items-center gap-3">
                     <FileText className="h-5 w-5 text-gray-400" />
                     <span className="text-sm font-medium">{baseModel?.name}</span>
                   </div>
                   <Link to={`/processes/${baseModel?.model_id}`}>
                     <Button variant="link" size="sm">View Base Model</Button>
                   </Link>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-sm font-semibold mb-3">Preconfigured Trigger</h3>
                <div className="p-4 border rounded bg-slate-50">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="font-medium text-sm capitalize">{template.trigger_info?.type || 'Manual'} Trigger</span>
                  </div>
                  <p className="text-xs text-gray-500">{template.trigger_info?.description || 'This workflow is started manually by an authorized user.'}</p>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold mb-3">Workflow Stages & Steps</h3>
                <div className="space-y-4">
                  {template.stages?.map((stage, sIdx) => (
                    <div key={sIdx} className="border rounded overflow-hidden">
                      <div className="bg-gray-50 px-4 py-2 border-b font-medium text-sm flex justify-between">
                        <span>Stage {sIdx + 1}: {stage.name}</span>
                        <Badge variant="ghost" className="text-[10px]">{stage.steps?.length || 0} Steps</Badge>
                      </div>
                      <div className="p-4 space-y-2">
                         {template.steps?.filter(s => s.stage_id === stage.stage_id).map((step, stIdx) => (
                           <div key={stIdx} className="flex items-center gap-3 text-sm p-2 hover:bg-gray-50 rounded border border-transparent hover:border-gray-200 transition-colors">
                             <div className="h-2 w-2 rounded-full bg-blue-400" />
                             <span className="flex-1 font-medium">{step.name}</span>
                             <Badge variant="outline" className="text-[10px]">{step.step_type?.replace('_', ' ')}</Badge>
                           </div>
                         ))}
                      </div>
                    </div>
                  ))}
                  {(!template.stages || template.stages.length === 0) && (
                    <p className="text-sm text-gray-400 italic">No stages preconfigured in this template.</p>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold mb-2">Supported Roles</h3>
                <div className="flex flex-wrap gap-2">
                  {template.supported_roles?.map(role => (
                    <Badge key={role} variant="outline" className="capitalize">{role.replace('_', ' ')}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <span className="text-xs text-gray-400 block">Created At</span>
                <span className="text-sm">{new Date(template.created_at).toLocaleString()}</span>
              </div>
              <div>
                <span className="text-xs text-gray-400 block">Source</span>
                <Badge variant="secondary" className="mt-1">{template.source_type}</Badge>
              </div>

              <Separator />

              <div className="space-y-3">
                 <div className="flex items-start gap-2 text-xs text-slate-600 bg-slate-50 p-3 rounded">
                  <Info className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>Workflow templates are reusable definitions that can be instantiated into active workflows.</span>
                </div>
                 <div className="flex items-center gap-2 text-xs text-blue-700">
                  <Layout className="h-3 w-3" />
                  <span>Template ID: {template.template_id}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {isArchitect && isWorkspaceTemplate && (
          <div className="flex gap-3 mt-8 pt-6 border-t">
            <Button variant="outline">Edit Template</Button>
            <Button variant="destructive">Archive Template</Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TemplateDetailPage;
