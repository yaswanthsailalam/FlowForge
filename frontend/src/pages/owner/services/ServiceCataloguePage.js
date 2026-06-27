import React from 'react';
import { Cloud, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';

const ServiceCataloguePage = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Service Catalogue</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card><CardHeader><CardTitle>Rapid Implementation</CardTitle></CardHeader></Card>
      </div>
    </div>
  );
};
export default ServiceCataloguePage;
