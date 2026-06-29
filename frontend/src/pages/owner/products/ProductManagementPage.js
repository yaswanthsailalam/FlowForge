import React from 'react';
import { Package, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const ProductManagementPage = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Products & Plans</h1>
        <Button className="bg-side-a hover:bg-side-a/90 font-bold"><Plus className="mr-2 h-4 w-4" /> New Product</Button>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <Card><CardHeader><CardTitle>Process Model Studio</CardTitle></CardHeader><CardContent><Badge>v2.0.0</Badge></CardContent></Card>
      </div>
    </div>
  );
};
export default ProductManagementPage;
