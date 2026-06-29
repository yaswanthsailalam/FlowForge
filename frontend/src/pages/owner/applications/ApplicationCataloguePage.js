import React from 'react';
import { AppWindow, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';

const ApplicationCataloguePage = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">App Catalogue</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card><CardHeader><CardTitle>Salesforce</CardTitle></CardHeader></Card>
      </div>
    </div>
  );
};
export default ApplicationCataloguePage;
