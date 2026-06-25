import React from 'react';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

const CatalogueFilters = ({ filters, onFilterChange, industries, departments }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 bg-white p-4 rounded-lg shadow-sm mb-6 border">
      <div className="space-y-1">
        <Label htmlFor="search">Search</Label>
        <Input
          id="search"
          placeholder="Search models, tags..."
          value={filters.search}
          onChange={(e) => onFilterChange('search', e.target.value)}
        />
      </div>

      <div className="space-y-1">
        <Label>Industry</Label>
        <Select
          value={filters.industry || "all"}
          onValueChange={(val) => onFilterChange('industry', val === "all" ? "" : val)}
        >
          <SelectTrigger>
            <SelectValue placeholder="All Industries" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Industries</SelectItem>
            {industries.map(ind => (
              <SelectItem key={ind.industry_id} value={ind.industry_id}>{ind.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1">
        <Label>Department</Label>
        <Select
          value={filters.department || "all"}
          onValueChange={(val) => onFilterChange('department', val === "all" ? "" : val)}
        >
          <SelectTrigger>
            <SelectValue placeholder="All Departments" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Departments</SelectItem>
            {departments.map(dept => (
              <SelectItem key={dept.department_id} value={dept.department_id}>{dept.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1">
        <Label>Source</Label>
        <Select
          value={filters.source_type || "all"}
          onValueChange={(val) => onFilterChange('source_type', val === "all" ? "" : val)}
        >
          <SelectTrigger>
            <SelectValue placeholder="All Sources" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Sources</SelectItem>
            <SelectItem value="global">Global</SelectItem>
            <SelectItem value="workspace">Workspace</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};

export default CatalogueFilters;
