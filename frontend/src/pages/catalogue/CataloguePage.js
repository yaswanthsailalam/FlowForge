import React, { useState, useEffect, useCallback } from 'react';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import { useAuth } from '@/contexts/AuthContext';
import catalogueService from '@/services/catalogueService';
import CatalogueCard from '@/components/catalogue/CatalogueCard';
import CatalogueFilters from '@/components/catalogue/CatalogueFilters';
import { Button } from '@/components/ui/button';
import { Plus, Loader2, RefreshCcw, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

const CataloguePage = () => {
  const { activeWorkspace, loading: workspaceLoading } = useWorkspace();
  const { isAuthenticated, loading: authLoading } = useAuth();

  const [models, setModels] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 });
  const [industries, setIndustries] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [favourites, setFavourites] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [filters, setFilters] = useState({
    search: '',
    industry: '',
    department: '',
    source_type: '',
    page: 1
  });

  const fetchCatalogueData = useCallback(async () => {
    // Wait for auth and workspace to be fully resolved
    if (authLoading || workspaceLoading) return;

    // If not authenticated or no workspace selected, we can't fetch
    if (!isAuthenticated || !activeWorkspace) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [modelsRes, indRes, deptRes, favRes] = await Promise.allSettled([
        catalogueService.getProcessModels({
          ...filters,
          workspace_id: activeWorkspace.workspace_id
        }),
        catalogueService.getIndustries(),
        catalogueService.getDepartments(),
        catalogueService.getFavourites()
      ]);

      // 1. Handle Models Response (Required)
      if (modelsRes.status === 'fulfilled') {
        const data = modelsRes.value.data;
        // Robust normalization
        const items = Array.isArray(data) ? data : (data?.items || []);
        const pag = data?.pagination || { page: filters.page, pages: 1, total: items.length };

        setModels(items);
        setPagination(pag);
      } else {
        console.error("Failed to fetch models", modelsRes.reason);
        throw modelsRes.reason;
      }

      // 2. Handle Optional metadata
      if (indRes.status === 'fulfilled') setIndustries(indRes.value.data || []);
      if (deptRes.status === 'fulfilled') setDepartments(deptRes.value.data || []);
      if (favRes.status === 'fulfilled') setFavourites(favRes.value.data || []);

    } catch (err) {
      console.error("Catalogue data fetch failed", err);
      setError(err.response?.status === 403
        ? "You do not have permission to view the catalogue in this workspace."
        : "Unable to load the process catalogue. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, authLoading, activeWorkspace, workspaceLoading, filters]);

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

  // Determine which UI to show
  const isContextReady = isAuthenticated && activeWorkspace;

  if (authLoading || workspaceLoading || (loading && isContextReady && models.length === 0)) {
    return (
      <div className="flex flex-col h-[400px] items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-sm font-medium text-slate-400">Preparing Catalogue...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
      return (
          <div className="container mx-auto py-20 text-center">
              <h2 className="text-xl font-bold">Authentication Required</h2>
              <p className="text-slate-500 mt-2">Please log in to view the process catalogue.</p>
              <Button asChild className="mt-6">
                  <Link to="/login">Login</Link>
              </Button>
          </div>
      );
  }

  if (!activeWorkspace) {
      return (
          <div className="container mx-auto py-20 text-center">
              <AlertCircle className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <h2 className="text-xl font-bold">No Workspace Selected</h2>
              <p className="text-slate-500 mt-2">Please select a workspace to browse its catalogue.</p>
              <Button asChild className="mt-6" variant="outline">
                  <Link to="/workspaces">Select Workspace</Link>
              </Button>
          </div>
      );
  }

  if (error) {
    return (
      <div className="container mx-auto py-20 max-w-lg">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button className="mt-6 w-full" onClick={fetchCatalogueData}>
          <RefreshCcw className="mr-2 h-4 w-4" /> Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 px-4">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Process Catalogue</h1>
          <p className="text-slate-500 mt-1 font-medium">Standardized blueprints for {activeWorkspace.name} operations.</p>
        </div>
        <Button asChild className="shadow-lg shadow-primary/20">
          <Link to="/processes/new">
            <Plus className="mr-2 h-4 w-4" /> Create Process Model
          </Link>
        </Button>
      </div>

      <div className="mb-8">
        <CatalogueFilters
            filters={filters}
            onFilterChange={handleFilterChange}
            industries={industries}
            departments={departments}
        />
      </div>

      {models.length > 0 ? (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
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
            <div className="flex justify-center mt-12 gap-4 items-center">
              <Button
                variant="outline"
                size="sm"
                disabled={!pagination.has_prev}
                onClick={() => handleFilterChange('page', filters.page - 1)}
                className="font-bold uppercase tracking-widest text-[10px]"
              >
                Previous
              </Button>
              <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
                Page {pagination.page} of {pagination.pages}
              </div>
              <Button
                variant="outline"
                size="sm"
                disabled={!pagination.has_next}
                onClick={() => handleFilterChange('page', filters.page + 1)}
                className="font-bold uppercase tracking-widest text-[10px]"
              >
                Next
              </Button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-32 bg-slate-50/50 rounded-3xl border-2 border-dashed border-slate-200">
          <div className="bg-white h-16 w-16 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-center mx-auto mb-6">
            <Loader2 className="h-8 w-8 text-slate-200" />
          </div>
          <h3 className="text-xl font-bold text-slate-900">No process models found</h3>
          <p className="text-slate-500 mt-2 max-w-sm mx-auto">We couldn't find any blueprints matching your current filters in {activeWorkspace.name}.</p>
          <div className="mt-8 flex justify-center space-x-4">
             <Button variant="outline" onClick={() => setFilters({
                search: '', industry: '', department: '', source_type: '', page: 1
             })} className="font-bold uppercase tracking-widest text-[10px]">
               Clear all filters
             </Button>
             <Button asChild variant="default" className="font-bold uppercase tracking-widest text-[10px]">
                <Link to="/processes/new">Create first model</Link>
             </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CataloguePage;
