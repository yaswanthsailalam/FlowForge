import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Construction } from 'lucide-react';

const PlaceholderPage = ({ title }) => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
      </div>
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-20">
          <div className="rounded-full bg-yellow-100 p-6 mb-4">
            <Construction className="h-12 w-12 text-yellow-600" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Under Construction</h2>
          <p className="text-muted-foreground text-center max-w-md">
            The {title} module is currently being developed. Please check back later for updates.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default PlaceholderPage;
