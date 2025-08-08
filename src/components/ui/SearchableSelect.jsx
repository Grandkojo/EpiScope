import React, { useState, useMemo } from 'react';
import { Search } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './select';

const SearchableSelect = ({
  value,
  onValueChange,
  placeholder,
  searchPlaceholder = "Search...",
  options = [],
  className,
  disabled = false,
  loading = false,
  loadingText = "Loading...",
  allOption = null, // { value: "all", label: "All" }
  noOptionsMessage = () => "No options found",
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  // Filter options based on search term
  const filteredOptions = useMemo(() => {
    if (!searchTerm.trim()) return options;
    
    return options.filter(option => {
      const label = typeof option === 'string' ? option : option.label;
      return label.toLowerCase().includes(searchTerm.toLowerCase());
    });
  }, [options, searchTerm]);

  const handleOpenChange = (open) => {
    setIsOpen(open);
    if (!open) {
      setSearchTerm(''); // Clear search when closing
    }
  };

  const handleSearchChange = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setSearchTerm(e.target.value);
  };

  const handleSearchClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleSearchKeyDown = (e) => {
    e.stopPropagation();
  };

  return (
    <Select
      value={value}
      onValueChange={onValueChange}
      open={isOpen}
      onOpenChange={handleOpenChange}
      disabled={disabled}
    >
      <SelectTrigger className={className}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {/* Search Input */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 p-2">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder={searchPlaceholder}
              value={searchTerm}
              onChange={handleSearchChange}
              onClick={handleSearchClick}
              onKeyDown={handleSearchKeyDown}
              className="w-full pl-8 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <SelectItem value="loading" disabled>
            {loadingText}
          </SelectItem>
        )}

        {/* All Option */}
        {allOption && (
          <SelectItem value={allOption.value}>
            {allOption.label}
          </SelectItem>
        )}

        {/* Filtered Options */}
        {!loading && filteredOptions.length > 0 ? (
          filteredOptions.map((option, index) => {
            const value = typeof option === 'string' ? option : option.value;
            const label = typeof option === 'string' ? option : option.label;
            
            return (
              <SelectItem key={`${value}-${index}`} value={value}>
                {label}
              </SelectItem>
            );
          })
        ) : !loading && searchTerm && (
          <div className="px-2 py-2 text-sm text-gray-500 text-center">
            {noOptionsMessage(searchTerm)}
          </div>
        )}
      </SelectContent>
    </Select>
  );
};

export default SearchableSelect; 