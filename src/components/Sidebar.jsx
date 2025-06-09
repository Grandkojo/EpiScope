import React, { useState } from 'react';
import { cn } from '../lib/utils';
import { Button } from './ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import Logo from './Logo';

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div
      className={cn(
        "h-screen bg-white border-r border-gray-200 transition-all duration-300 flex flex-col glass-effect",
        isCollapsed ? "w-16" : "w-64",
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div
            className={cn("flex items-center space-x-3 transition-opacity duration-200", isCollapsed && "opacity-0")}
          >
            <Logo className="w-8 h-8" />
            <div>
              <h1 className="text-xl font-bold text-green-600">Episcope</h1>
              <p className="text-xs text-gray-500">Health Monitor</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={() => setIsCollapsed(!isCollapsed)} className="h-8 w-8">
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>
      </div>
      {/* ... existing code ... */}
      <div className="p-4 border-t border-gray-200">
        <div className={cn("text-center transition-opacity duration-200", isCollapsed && "opacity-0")}> 
          <p className="text-xs text-gray-500">Ghana Health Monitor</p>
          <p className="text-xs text-green-600 font-medium">v1.0.0</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar; 