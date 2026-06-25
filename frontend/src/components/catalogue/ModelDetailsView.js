import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle2, AlertCircle } from 'lucide-react';

const ModelDetailsView = ({ model }) => {
  if (!model) return null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">{model.name}</h1>
          <p className="text-gray-500 mt-1">{model.description}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <Badge variant={model.catalogue_status === 'published' ? 'default' : 'secondary'}>
            {model.catalogue_status}
          </Badge>
          <span className="text-xs text-gray-400">Version {model.version}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Process Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold mb-1">Purpose</h3>
              <p className="text-sm text-gray-600">{model.purpose || 'No purpose defined.'}</p>
            </div>

            <Separator />

            <div>
              <h3 className="text-sm font-semibold mb-2">Expected Stages</h3>
              <div className="space-y-2">
                {model.expected_stages?.map((stage, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-2 bg-gray-50 rounded border">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-blue-700 text-xs font-bold">
                      {idx + 1}
                    </span>
                    <span className="text-sm font-medium">{stage.name}</span>
                  </div>
                ))}
                {(!model.expected_stages || model.expected_stages.length === 0) && (
                  <p className="text-xs text-gray-400 italic">No stages defined.</p>
                )}
              </div>
            </div>

            <Separator />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-semibold mb-1">Suggested Roles</h3>
                <div className="flex flex-wrap gap-1">
                  {model.suggested_roles?.map(role => (
                    <Badge key={role} variant="outline" className="text-[10px]">{role}</Badge>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold mb-1">Approval Points</h3>
                <div className="flex flex-wrap gap-1">
                  {model.approval_points?.map(ap => (
                    <Badge key={ap} variant="outline" className="text-[10px] border-orange-200 text-orange-700 bg-orange-50">{ap}</Badge>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Metadata & Scope</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-xs text-gray-400">Industries</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {model.applicable_industries?.map(ind => (
                  <Badge key={ind} variant="secondary" className="text-[10px]">{ind}</Badge>
                ))}
              </div>
            </div>
            <div>
              <Label className="text-xs text-gray-400">Departments</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {model.applicable_departments?.map(dept => (
                  <Badge key={dept} variant="secondary" className="text-[10px]">{dept}</Badge>
                ))}
              </div>
            </div>
            <div>
              <Label className="text-xs text-gray-400">Tags</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {model.tags?.map(tag => (
                  <Badge key={tag} variant="outline" className="text-[10px]">#{tag}</Badge>
                ))}
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <div className="flex items-center gap-2 text-xs text-green-700">
                <CheckCircle2 className="h-3 w-3" />
                <span>Source: {model.source_type}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-blue-700">
                <AlertCircle className="h-3 w-3" />
                <span>Scope: {model.ownership_scope}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Internal Label shim if needed, or import from UI
const Label = ({ children, className }) => <span className={className}>{children}</span>;

export default ModelDetailsView;
