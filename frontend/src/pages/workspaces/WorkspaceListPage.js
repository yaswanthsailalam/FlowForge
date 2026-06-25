import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { WORKSPACE } from '@/constants/testIds';
import { Plus, Building2 } from 'lucide-react';

const WorkspaceListPage = () => {
  const { workspaces, selectWorkspace, loading } = useWorkspace();
  const navigate = useNavigate();

  const handleSelect = (workspace) => {
    selectWorkspace(workspace);
    navigate('/dashboard');
  };

  if (loading && workspaces.length === 0) {
    return <div className="flex h-screen items-center justify-center">Loading workspaces...</div>;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl font-bold">Your Workspaces</CardTitle>
              <CardDescription>
                Select a workspace to continue or create a new one
              </CardDescription>
            </div>
            <Link to="/workspaces/create">
              <Button size="sm" data-testid={WORKSPACE.createLink}>
                <Plus className="mr-2 h-4 w-4" /> New Workspace
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2" data-testid={WORKSPACE.list}>
            {workspaces.map((ws) => (
              <Button
                key={ws.workspace_id}
                variant="outline"
                className="h-24 flex-col items-start justify-between p-4"
                onClick={() => handleSelect(ws)}
                data-testid={WORKSPACE.item(ws.workspace_id)}
              >
                <div className="flex w-full items-center justify-between">
                  <Building2 className="h-5 w-5 text-gray-500" />
                  <span className="text-xs font-medium uppercase text-gray-400">{ws.status}</span>
                </div>
                <div className="text-left">
                  <div className="font-bold">{ws.name}</div>
                  <div className="text-xs text-gray-500">ID: {ws.workspace_id}</div>
                </div>
              </Button>
            ))}
            {workspaces.length === 0 && (
              <div className="col-span-2 py-8 text-center text-gray-500">
                You don't have any workspaces yet.
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter className="justify-center border-t p-4">
          <Link to="/logout" className="text-sm text-gray-500 hover:underline">
            Logout
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
};

export default WorkspaceListPage;
