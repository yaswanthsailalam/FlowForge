import React, { useState, useEffect, useCallback } from 'react';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import catalogueService from '@/services/catalogueService';
import CatalogueCard from '@/components/catalogue/CatalogueCard';
import CatalogueFilters from '@/components/catalogue/CatalogueFilters';
import { Button } from '@/components/ui/button';
import { Plus, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const CataloguePage = () => {
  const { currentWorkspace } = useWorkspace();
  const [models, setModels] = useState([]);
  const [pagination, setPagination] = useState({});
  const [industries, setIndustries] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [favourites, setFavourites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    industry: '',
    department: '',
    source_type: '',
    page: 1
  });

  const fetchCatalogueData = useCallback(async () => {
    if (!currentWorkspace) return;
    setLoading(true);
    try {
      const [modelsRes, indRes, deptRes, favRes] = await Promise.all([
        catalogueService.getProcessModels({ ...filters, workspace_id: currentWorkspace.workspace_id }),
        catalogueService.getIndustries(),
        catalogueService.getDepartments(),
        catalogueService.getFavourites()
      ]);
      setModels(modelsRes.data.items);
      setPagination(modelsRes.data.pagination);
      setIndustries(indRes.data);
      setDepartments(deptRes.data);
      setFavourites(favRes.data);
    } catch (error) {
      console.error("Failed to fetch catalogue data", error);
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, filters]);

  useEffect(() => {
    fetchCatalogueData();
  }, [fetchCatalogueData]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  const handleToggleFavourite = async (modelId) => {
    try {
      await catalogueService.toggleFavourite(modelId);
      setFavourites(prev =>
        prev.includes(modelId) ? prev.filter(id => id !== modelId) : [...prev, modelId]
      );
    } catch (error) {
      console.error("Failed to toggle favourite", error);
    }
  };

  return (
    <div className="container mx-auto py-6 px-4">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Process Catalogue</h1>
          <p className="text-gray-500">Browse and manage business process models.</p>
        </div>
        <Button asChild>
          <Link to="/processes/new">
            <Plus className="mr-2 h-4 w-4" /> New Custom Model
          </Link>
        </Button>
      </div>

      <CatalogueFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        industries={industries}
        departments={departments}
      />

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      ) : models.length > 0 ? (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {models.map(model => (
              <CatalogueCard
                key={model.model_id}
                model={model}
                isFavourited={favourites.includes(model.model_id)}
                onToggleFavourite={handleToggleFavourite}
              />
            ))}
          </div>

          {pagination.pages > 1 && (
            <div className="flex justify-center mt-8 gap-2">
              <Button
                variant="outline"
                disabled={!pagination.has_prev}
                onClick={() => handleFilterChange('page', filters.page - 1)}
              >
                Previous
              </Button>
              <div className="flex items-center px-4 text-sm font-medium">
                Page {pagination.page} of {pagination.pages}
              </div>
              <Button
                variant="outline"
                disabled={!pagination.has_next}
                onClick={() => handleFilterChange('page', filters.page + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-20 bg-gray-50 rounded-lg border-2 border-dashed">
          <h3 className="text-lg font-medium text-gray-900">No process models found</h3>
          <p className="text-gray-500 mt-1">Try adjusting your filters or search terms.</p>
          <Button variant="outline" className="mt-4" onClick={() => setFilters({
             search: '', industry: '', department: '', source_type: '', page: 1
          })}>
            Clear all filters
          </Button>
        </div>
      )}
    </div>
  );
};

export default CataloguePage;
