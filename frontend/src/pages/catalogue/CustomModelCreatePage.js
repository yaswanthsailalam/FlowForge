import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import catalogueService from '@/services/catalogueService';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { ArrowLeft, Save } from 'lucide-react';

const CustomModelCreatePage = () => {
  const navigate = useNavigate();
  const { currentWorkspace } = useWorkspace();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    purpose: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await catalogueService.createProcessModel({
        ...formData,
        applicable_industries: [],
        applicable_departments: [],
        tags: []
      });
      navigate(`/processes/${res.data.model_id}`);
    } catch (error) {
      console.error("Failed to create model", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-6 px-4 max-w-2xl">
      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back
      </Button>

      <Card>
        <form onSubmit={handleSubmit}>
          <CardHeader>
            <CardTitle>Create Custom Process Model</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Model Name</Label>
              <Input
                id="name"
                required
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="e.g. Quarterly Performance Review"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Short Description</Label>
              <Textarea
                id="description"
                required
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Briefly describe what this process does."
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="purpose">Business Purpose</Label>
              <Textarea
                id="purpose"
                value={formData.purpose}
                onChange={(e) => setFormData({...formData, purpose: e.target.value})}
                placeholder="What is the objective or outcome of this process?"
              />
            </div>
          </CardContent>
          <CardFooter className="flex justify-end gap-3 border-t pt-6">
            <Button type="button" variant="ghost" onClick={() => navigate(-1)}>Cancel</Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : <><Save className="mr-2 h-4 w-4" /> Create Model</>}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};

export default CustomModelCreatePage;
