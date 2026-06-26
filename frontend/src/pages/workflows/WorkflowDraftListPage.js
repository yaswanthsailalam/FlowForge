import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2, Plus, FileText, Calendar, ChevronRight, Filter, Search } from 'lucide-react';
import workflowService from '@/services/workflowService';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useWorkspace } from '@/contexts/WorkspaceContext';

const WorkflowDraftListPage = () => {
  const navigate = useNavigate();
  const { membership } = useWorkspace();
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchDrafts = async () => {
      try {
        const res = await workflowService.getDrafts();
        setDrafts(res.data);
      } catch (err) {
        console.error("Failed to fetch drafts", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDrafts();
  }, []);

  const filteredDrafts = drafts.filter(d =>
    d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const isArchitect = membership?.role === 'workspace_admin' || membership?.role === 'process_architect';

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="animate-spin" /></div>;

  return (
    <div className="container mx-auto py-6 px-4">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflow Drafts</h1>
          <p className="text-muted-foreground mt-1">Configure and manage your organization's workflow definitions.</p>
        </div>
        {isArchitect && (
          <Button onClick={() => navigate('/workflows/new')}>
            <Plus className="mr-2 h-4 w-4" /> Create Blank Workflow
          </Button>
        )}
      </div>

      <Card className="mb-8">
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search drafts..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" /> Filter
            </Button>
          </div>
        </CardContent>
      </Card>

      {filteredDrafts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDrafts.map((draft) => (
            <Card key={draft.workflow_id} className="hover:shadow-md transition-shadow cursor-pointer group" onClick={() => navigate(`/workflows/edit/${draft.workflow_id}`)}>
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start mb-2">
                  <Badge variant="secondary">{draft.status.toUpperCase()}</Badge>
                  <div className="text-[10px] text-muted-foreground flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {new Date(draft.updated_at).toLocaleDateString()}
                  </div>
                </div>
                <CardTitle className="group-hover:text-primary transition-colors">{draft.name}</CardTitle>
                <CardDescription className="line-clamp-2 mt-2 h-10">
                  {draft.description || 'No description provided.'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center pt-4 border-t">
                  <span className="text-xs font-medium text-muted-foreground">
                    Updated {new Date(draft.updated_at).toLocaleDateString()}
                  </span>
                  <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-20 bg-muted/30 rounded-lg border-2 border-dashed">
          <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium">No drafts found</h3>
          <p className="text-muted-foreground mt-1 mb-6">Start by creating a new workflow from the catalogue or a blank slate.</p>
          <Button variant="outline" asChild>
            <Link to="/processes">Browse Catalogue</Link>
          </Button>
        </div>
      )}
    </div>
  );
};

export default WorkflowDraftListPage;
