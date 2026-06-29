import React from 'react';
import { Users, Plus, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const ClientManagementPage = () => {
  const clients = [{ id: 'c1', name: 'Acme Health Systems', status: 'active', plan: 'Enterprise' }];
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Client Management</h1>
        <Button className="bg-side-a hover:bg-side-a/90 font-bold"><Plus className="mr-2 h-4 w-4" /> Provision Client</Button>
      </div>
      <div className="bg-white rounded-2xl border shadow-sm overflow-hidden">
        <Table>
          <TableHeader><TableRow><TableHead>Organisation</TableHead><TableHead>Status</TableHead><TableHead>Plan</TableHead><TableHead></TableHead></TableRow></TableHeader>
          <TableBody>
            {clients.map((client) => (
              <TableRow key={client.id}>
                <TableCell className="font-bold">{client.name}</TableCell>
                <TableCell><Badge>{client.status}</Badge></TableCell>
                <TableCell>{client.plan}</TableCell>
                <TableCell className="text-right"><Button variant="ghost" size="icon"><MoreVertical className="h-4 w-4" /></Button></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
export default ClientManagementPage;
