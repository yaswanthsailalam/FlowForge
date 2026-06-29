import React from 'react';
import { ShieldCheck, Eye, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useNavigate } from 'react-router-dom';

const ProcessGovernancePage = () => {
  const navigate = useNavigate();
  const models = [
    { id: 'm1', name: 'Global Patient Intake', version: '1.2.0', status: 'published', updated: '2h ago', author: 'Mark Architect' },
    { id: 'm2', name: 'Standard Procurement', version: '2.0.1', status: 'in_review', updated: '1d ago', author: 'Alex Owner' }
  ];
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Process Governance</h1>
        <Button className="bg-side-a hover:bg-side-a/90 font-bold" onClick={() => navigate('/processes/new')}>
          <Plus className="mr-2 h-4 w-4" /> Create Global Model
        </Button>
      </div>
      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-slate-50">
            <TableRow>
              <TableHead>Model Name</TableHead><TableHead>Status</TableHead><TableHead>Version</TableHead><TableHead className="text-right"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {models.map((model) => (
              <TableRow key={model.id}>
                <TableCell className="font-bold">{model.name}</TableCell>
                <TableCell><Badge variant="outline">{model.status}</Badge></TableCell>
                <TableCell>v{model.version}</TableCell>
                <TableCell className="text-right"><Button variant="ghost" size="icon"><Eye className="h-4 w-4" /></Button></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
export default ProcessGovernancePage;
