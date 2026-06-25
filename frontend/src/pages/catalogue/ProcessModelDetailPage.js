import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import catalogueService from '@/services/catalogueService';
import ModelDetailsView from '@/components/catalogue/ModelDetailsView';
import { Button } from '@/components/ui/button';
import { Loader2, ArrowLeft, Edit, Archive, CheckCircle, Layers, Layout, ChevronRight } from 'lucide-react';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Link } from 'react-router-dom';

const ProcessModelDetailPage = () => {
  const { modelId } = useParams();
  const navigate = useNavigate();
  const { membership } = useWorkspace();
  const [model, setModel] = useState(null);
  const [variants, setVariants] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchModelData = async () => {
      try {
        const [modelRes, variantsRes, templatesRes] = await Promise.all([
          catalogueService.getProcessModel(modelId),
          catalogueService.getVariants(modelId),
          catalogueService.getWorkflowTemplates({ model_id: modelId })
        ]);
        setModel(modelRes.data);
        setVariants(variantsRes.data);
        setTemplates(templatesRes.data);
      } catch (err) {
        console.error("Failed to fetch model details", err);
        setError(err.response?.status === 403 ? "Access Denied" : "Failed to load model");
      } finally {
        setLoading(false);
      }
    };
    fetchModel();
  }, [modelId]);

  const handlePublish = async () => {
    try {
      await catalogueService.publishProcessModel(modelId);
      const res = await catalogueService.getProcessModel(modelId);
      setModel(res.data);
    } catch (err) {
      console.error("Failed to publish", err);
    }
  };

  const handleArchive = async () => {
    try {
      await catalogueService.archiveProcessModel(modelId);
      const res = await catalogueService.getProcessModel(modelId);
      setModel(res.data);
    } catch (err) {
      console.error("Failed to archive", err);
    }
  };

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="animate-spin" /></div>;
  if (error) return <div className="container mx-auto py-10 text-center text-red-500">{error}</div>;

  const isArchitect = membership?.role === 'workspace_admin' || membership?.role === 'process_architect';
  const isWorkspaceModel = model?.source_type === 'workspace';

  return (
    <div className="container mx-auto py-6 px-4">
      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Catalogue
      </Button>

      <div className="bg-white rounded-lg border shadow-sm p-8 mb-6">
        <ModelDetailsView model={model} />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-md font-medium">Variants</CardTitle>
              <Layers className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {variants.length > 0 ? (
                <div className="space-y-2 mt-2">
                  {variants.map(v => (
                    <Link
                      key={v.variant_id}
                      to={`/variants/${v.variant_id}`}
                      className="flex items-center justify-between p-2 hover:bg-gray-50 rounded border transition-colors group"
                    >
                      <span className="text-sm">{v.name}</span>
                      <ChevronRight className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400 italic mt-2">No variants available.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-md font-medium">Workflow Templates</CardTitle>
              <Layout className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {templates.length > 0 ? (
                <div className="space-y-2 mt-2">
                  {templates.map(t => (
                    <Link
                      key={t.template_id}
                      to={`/templates/${t.template_id}`}
                      className="flex items-center justify-between p-2 hover:bg-gray-50 rounded border transition-colors group"
                    >
                      <span className="text-sm">{t.name}</span>
                      <ChevronRight className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400 italic mt-2">No templates available.</p>
              )}
            </CardContent>
          </Card>
        </div>

        {isArchitect && isWorkspaceModel && (
          <div className="flex gap-3 mt-8 pt-6 border-t">
            <Button variant="outline">
              <Edit className="mr-2 h-4 w-4" /> Edit Model
            </Button>
            {model.catalogue_status !== 'published' && (
              <Button onClick={handlePublish}>
                <CheckCircle className="mr-2 h-4 w-4" /> Publish to Catalogue
              </Button>
            )}
            {model.catalogue_status !== 'archived' && (
              <Button variant="destructive" onClick={handleArchive}>
                <Archive className="mr-2 h-4 w-4" /> Archive Model
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessModelDetailPage;
