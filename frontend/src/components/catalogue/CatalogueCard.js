import React from 'react';
import { Link } from 'react-router-dom';
import { Star, FileText, Layers, Layout } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const CatalogueCard = ({ model, isFavourited, onToggleFavourite }) => {
  return (
    <Card className="flex flex-col h-full hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <Badge variant={model.source_type === 'global' ? 'secondary' : 'outline'}>
            {model.source_type}
          </Badge>
          <Button
            variant="ghost"
            size="icon"
            className={cn("h-8 w-8", isFavourited && "text-yellow-500")}
            onClick={(e) => {
              e.preventDefault();
              onToggleFavourite(model.model_id);
            }}
          >
            <Star className={cn("h-4 w-4", isFavourited && "fill-current")} />
          </Button>
        </div>
        <CardTitle className="line-clamp-1 mt-2">{model.name}</CardTitle>
        <CardDescription className="line-clamp-2 min-h-[2.5rem]">
          {model.description}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1 pb-2">
        <div className="flex flex-wrap gap-1 mt-2">
          {model.applicable_industries?.map(ind => (
            <Badge key={ind} variant="outline" className="text-[10px]">
              {ind.replace('ind-', '')}
            </Badge>
          ))}
          {model.tags?.slice(0, 3).map(tag => (
            <Badge key={tag} variant="ghost" className="text-[10px] bg-gray-100">
              #{tag}
            </Badge>
          ))}
        </div>
      </CardContent>
      <CardFooter className="pt-0 border-t mt-4">
        <div className="grid grid-cols-3 w-full gap-2 pt-3 text-[11px] text-gray-500">
          <div className="flex flex-col items-center">
            <Layers className="h-3 w-3 mb-1" />
            <span>Variants</span>
          </div>
          <div className="flex flex-col items-center">
            <Layout className="h-3 w-3 mb-1" />
            <span>Templates</span>
          </div>
          <Link to={`/processes/${model.model_id}`} className="flex flex-col items-center hover:text-blue-600">
            <FileText className="h-3 w-3 mb-1" />
            <span>Details</span>
          </Link>
        </div>
      </CardFooter>
    </Card>
  );
};

export default CatalogueCard;
