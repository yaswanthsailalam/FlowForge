import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import catalogueService from '@/services/catalogueService';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Loader2, ArrowLeft, Layers, FileText, CheckCircle, Archive } from 'lucide-react';
import { useWorkspace } from '@/contexts/WorkspaceContext';

const VariantDetailPage = () => {
  const { variantId } = useParams();
  const navigate = useNavigate();
  const { membership } = useWorkspace();
  const [variant, setVariant] = useState(null);
  const [baseModel, setBaseModel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVariantData = async () => {
      try {
        const varRes = await catalogueService.getVariant(variantId);
        setVariant(varRes.data);

        const modelRes = await catalogueService.getProcessModel(varRes.data.model_id);
        setBaseModel(modelRes.data);
      } catch (err) {
        console.error("Failed to fetch variant details", err);
        setError(err.response?.status === 403 ? "Access Denied" : "Failed to load variant");
      } finally {
        setLoading(false);
      }
    };
    fetchVariantData();
  }, [variantId]);

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="animate-spin" /></div>;
  if (error) return <div className="container mx-auto py-10 text-center text-red-500">{error}</div>;

  const isArchitect = membership?.role === 'workspace_admin' || membership?.role === 'process_architect';
  const isWorkspaceVariant = variant?.workspace_id !== null;

  return (
    <div className="container mx-auto py-6 px-4">
      <div className="flex items-center gap-2 mb-6 text-sm text-gray-500">
        <Link to="/processes" className="hover:text-blue-600">Catalogue</Link>
        <span>/</span>
        <Link to={`/processes/${baseModel?.model_id}`} className="hover:text-blue-600">{baseModel?.name}</Link>
        <span>/</span>
        <span className="font-medium text-gray-900">{variant.name}</span>
      </div>

      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back
      </Button>

      <div className="bg-white rounded-lg border shadow-sm p-8 mb-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold">{variant.name}</h1>
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Variant</Badge>
            </div>
            <p className="text-gray-500 mt-1">{variant.description}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Badge>{variant.status}</Badge>
            <span className="text-xs text-gray-400">Version {variant.version}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-lg">Variant Configuration</CardTitle>
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

              {variant.additional_stages?.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold mb-2">Additional Stages</h3>
                  <div className="space-y-2">
                    {variant.additional_stages.map((stage, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-2 bg-green-50 rounded border border-green-100">
                        <Badge variant="outline" className="bg-white text-green-700">+ Stage</Badge>
                        <span className="text-sm font-medium">{stage.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {variant.removed_optional_stages?.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold mb-2">Removed Optional Stages</h3>
                  <div className="space-y-2">
                    {variant.removed_optional_stages.map((stageId, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-2 bg-red-50 rounded border border-red-100">
                        <Badge variant="outline" className="bg-white text-red-700">- Removed</Badge>
                        <span className="text-sm font-medium">{stageId}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="text-sm font-semibold mb-2">Configuration Overrides</h3>
                {variant.configuration_overrides && Object.keys(variant.configuration_overrides).length > 0 ? (
                  <pre className="text-xs p-4 bg-gray-900 text-gray-100 rounded overflow-auto max-h-60">
                    {JSON.stringify(variant.configuration_overrides, null, 2)}
                  </pre>
                ) : (
                  <p className="text-xs text-gray-400 italic">No configuration overrides defined.</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <span className="text-xs text-gray-400 block">Created At</span>
                <span className="text-sm">{new Date(variant.created_at).toLocaleString()}</span>
              </div>
              <div>
                <span className="text-xs text-gray-400 block">Last Updated</span>
                <span className="text-sm">{new Date(variant.updated_at).toLocaleString()}</span>
              </div>

              <Separator />

              <div className="space-y-2">
                 <div className="flex items-center gap-2 text-xs text-blue-700">
                  <Layers className="h-3 w-3" />
                  <span>Variant ID: {variant.variant_id}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {isArchitect && isWorkspaceVariant && (
          <div className="flex gap-3 mt-8 pt-6 border-t">
            <Button variant="outline">Edit Variant</Button>
            <Button variant="destructive">Archive Variant</Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default VariantDetailPage;
