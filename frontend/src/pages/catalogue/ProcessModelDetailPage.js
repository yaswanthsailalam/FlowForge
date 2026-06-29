import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import catalogueService from '@/services/catalogueService';
import ModelDetailsView from '@/components/catalogue/ModelDetailsView';
import { Button } from '@/components/ui/button';
import { Loader2, ArrowLeft, Edit, Archive, CheckCircle, Layers, Layout, ChevronRight, RefreshCcw, ShieldAlert, AlertCircle } from 'lucide-react';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Link } from 'react-router-dom';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';

const ProcessModelDetailPage = () => {
  const { modelId } = useParams();
  const navigate = useNavigate();
  const { membership } = useWorkspace();
  const [model, setModel] = useState(null);
  const [variants, setVariants] = useState([]);
  const [templates, setTemplates] = useState([]);

  const [loading, setLoading] = useState(true);
  const [loadingRelated, setLoadingRelated] = useState(false);
  const [error, setError] = useState(null);
  const [relatedError, setRelatedError] = useState(null);

  const fetchRelatedData = useCallback(async () => {
    setLoadingRelated(true);
    setRelatedError(null);
    try {
      const results = await Promise.allSettled([
        catalogueService.getVariants(modelId),
        catalogueService.getWorkflowTemplates({ model_id: modelId })
      ]);

      const [variantsRes, templatesRes] = results;

      if (variantsRes.status === 'fulfilled') {
        setVariants(variantsRes.value.data || []);
      } else {
        console.error("Failed to fetch variants", variantsRes.reason);
        // If 404, we assume it's just empty or endpoint mismatch, handle silently for user
        if (variantsRes.reason?.response?.status !== 404) {
            setRelatedError("Some related resources could not be loaded.");
        }
      }

      if (templatesRes.status === 'fulfilled') {
        setTemplates(templatesRes.value.data || []);
      } else {
        console.error("Failed to fetch templates", templatesRes.reason);
        if (templatesRes.reason?.response?.status !== 404) {
            setRelatedError("Some related resources could not be loaded.");
        }
      }
    } catch (err) {
      console.error("Unexpected error in fetchRelatedData", err);
    } finally {
      setLoadingRelated(false);
    }
  }, [modelId]);

  const fetchModelData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const modelRes = await catalogueService.getProcessModel(modelId);

      // Basic normalization to prevent crashes
      const modelData = modelRes.data || {};
      setModel({
        ...modelData,
        applicable_industries: modelData.applicable_industries || [],
        applicable_departments: modelData.applicable_departments || [],
        tags: modelData.tags || [],
        expected_stages: modelData.expected_stages || [],
        suggested_roles: modelData.suggested_roles || [],
        approval_points: modelData.approval_points || []
      });

      // Load related data independently
      fetchRelatedData();
    } catch (err) {
      console.error("Failed to fetch model details", err);
      if (err.response?.status === 404) {
        setError("Process Model not found.");
      } else if (err.response?.status === 403) {
        setError("You do not have permission to view this process model.");
      } else {
        setError("Failed to load model details. Please check your connection and try again.");
      }
    } finally {
      setLoading(false);
    }
  }, [modelId, fetchRelatedData]);

  useEffect(() => {
    if (modelId) {
      fetchModelData();
    }
  }, [modelId, fetchModelData]);

  const handlePublish = async () => {
    try {
      await catalogueService.publishProcessModel(modelId);
      await fetchModelData();
    } catch (err) {
      console.error("Failed to publish", err);
    }
  };

  const handleArchive = async () => {
    try {
      await catalogueService.archiveProcessModel(modelId);
      await fetchModelData();
    } catch (err) {
      console.error("Failed to archive", err);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[400px] items-center justify-center flex-col space-y-4">
        <Loader2 className="h-8 w-8 text-primary animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Loading Process Model...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-20 px-4 max-w-xl">
        <Alert variant="destructive" className="bg-red-50 border-red-200">
          <ShieldAlert className="h-5 w-5" />
          <AlertTitle className="text-red-900 font-bold ml-2">Error</AlertTitle>
          <AlertDescription className="text-red-700 ml-2 mt-2">
            {error}
          </AlertDescription>
        </Alert>
        <div className="mt-8 flex justify-center space-x-4">
          <Button variant="outline" onClick={() => navigate(-1)}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Go Back
          </Button>
          <Button onClick={fetchModelData}>
            <RefreshCcw className="mr-2 h-4 w-4" /> Retry
          </Button>
        </div>
      </div>
    );
  }

  const isArchitect = membership?.role === 'workspace_admin' || membership?.role === 'process_architect';
  const isWorkspaceModel = model?.source_type === 'workspace';

  return (
    <div className="container mx-auto py-6 px-4">
      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Catalogue
      </Button>

      <div className="bg-white rounded-xl border shadow-sm p-8 mb-6">
        <ModelDetailsView model={model} />

        {relatedError && (
            <Alert className="mt-8 bg-amber-50 border-amber-200 text-amber-800">
                <AlertCircle className="h-4 w-4 text-amber-600" />
                <AlertDescription className="text-xs font-medium ml-2">
                    {relatedError} <Button variant="link" className="h-auto p-0 text-xs font-bold" onClick={fetchRelatedData}>Try reloading related resources</Button>
                </AlertDescription>
            </Alert>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <Card className="border-slate-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
              <CardTitle className="text-sm font-bold uppercase tracking-widest text-slate-400">Variants</CardTitle>
              <Layers className="h-4 w-4 text-slate-300" />
            </CardHeader>
            <CardContent>
              {loadingRelated ? (
                  <div className="flex justify-center py-4"><Loader2 className="h-4 w-4 animate-spin text-slate-300" /></div>
              ) : variants.length > 0 ? (
                <div className="space-y-2">
                  {variants.map(v => (
                    <Link
                      key={v.variant_id}
                      to={`/variants/${v.variant_id}`}
                      className="flex items-center justify-between p-3 hover:bg-slate-50 rounded-lg border border-slate-100 transition-all group"
                    >
                      <span className="text-sm font-semibold text-slate-700">{v.name}</span>
                      <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-primary transition-colors" />
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400 italic">No organisation variants have been created for this Process Model.</p>
              )}
            </CardContent>
          </Card>

          <Card className="border-slate-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
              <CardTitle className="text-sm font-bold uppercase tracking-widest text-slate-400">Workflow Templates</CardTitle>
              <Layout className="h-4 w-4 text-slate-300" />
            </CardHeader>
            <CardContent>
              {loadingRelated ? (
                  <div className="flex justify-center py-4"><Loader2 className="h-4 w-4 animate-spin text-slate-300" /></div>
              ) : templates.length > 0 ? (
                <div className="space-y-2">
                  {templates.map(t => (
                    <Link
                      key={t.template_id}
                      to={`/templates/${t.template_id}`}
                      className="flex items-center justify-between p-3 hover:bg-slate-50 rounded-lg border border-slate-100 transition-all group"
                    >
                      <span className="text-sm font-semibold text-slate-700">{t.name}</span>
                      <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-primary transition-colors" />
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400 italic">No Workflow Templates are available for this Process Model.</p>
              )}
            </CardContent>
          </Card>
        </div>

        {isArchitect && isWorkspaceModel && (
          <div className="flex gap-3 mt-10 pt-8 border-t border-slate-100">
            <Button variant="outline" className="h-10 px-6 font-bold uppercase tracking-widest text-[10px]">
              <Edit className="mr-2 h-3.5 w-3.5" /> Edit Model
            </Button>
            {model.catalogue_status !== 'published' && (
              <Button onClick={handlePublish} className="h-10 px-6 font-bold uppercase tracking-widest text-[10px]">
                <CheckCircle className="mr-2 h-3.5 w-3.5" /> Publish to Catalogue
              </Button>
            )}
            {model.catalogue_status !== 'archived' && (
              <Button variant="destructive" onClick={handleArchive} className="h-10 px-6 font-bold uppercase tracking-widest text-[10px]">
                <Archive className="mr-2 h-3.5 w-3.5" /> Archive Model
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessModelDetailPage;
