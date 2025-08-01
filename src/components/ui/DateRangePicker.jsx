import React, { useState, useRef, useEffect } from "react";
import { Calendar, ChevronLeft, ChevronRight, X } from "lucide-react";
import { Button } from "./button";
import { Card, CardContent } from "./card";

/**
 * DateRangePicker Component
 * 
 * A comprehensive date range picker that supports different date formats for API integration.
 * 
 * @param {Object} props - Component props
 * @param {Function} props.onDateRangeChange - Callback function called when date range changes
 * @param {Array} props.availableYears - Array of available years from API (e.g., [2020, 2021, 2022, 2023, 2024, 2025])
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.placeholder - Placeholder text for the button
 * @param {boolean} props.disabled - Whether the picker is disabled
 * 
 * @example
 * // Basic usage
 * <DateRangePicker
 *   onDateRangeChange={(apiFormat, dateRangeObj) => {
 *     console.log('API Format:', apiFormat); // "2023-03", "2023-03:2023-08", or "2023-03-01:2023-08-31"
 *     console.log('Date Range Object:', dateRangeObj); // { from: Date, to: Date }
 *   }}
 *   availableYears={[2020, 2021, 2022, 2023, 2024, 2025]}
 * />
 * 
 * @example
 * // With API integration
 * const handleDateRangeChange = async (apiFormat, dateRangeObj) => {
 *   if (apiFormat) {
 *     const response = await fetch('/api/analytics', {
 *       method: 'POST',
 *       headers: { 'Content-Type': 'application/json' },
 *       body: JSON.stringify({ date_range: apiFormat })
 *     });
 *     const data = await response.json();
 *     // Update your component state with the new data
 *   }
 * };
 * 
 * <DateRangePicker
 *   onDateRangeChange={handleDateRangeChange}
 *   availableYears={diseaseYears.map(year => year.periodname)}
 *   placeholder="Select date range"
 * />
 */
const DateRangePicker = ({ 
  onDateRangeChange, 
  availableYears = [], 
  className = "",
  placeholder = "Select date range",
  disabled = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [dateRange, setDateRange] = useState({ from: null, to: null });
  const [currentView, setCurrentView] = useState("range"); // "range", "from", "to"
  const [currentMonth, setCurrentMonth] = useState(() => {
    // Initialize with the first available year and March (first available month)
    const years = availableYears.length > 0 ? availableYears.sort((a, b) => b - a) : [new Date().getFullYear()];
    return new Date(years[0], 2, 1); // March (month 2) of first available year
  });
  const [selectedRangeType, setSelectedRangeType] = useState("month"); // "month", "full"
  const [tempRange, setTempRange] = useState({ from: null, to: null });
  
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Get available years for the picker
  const getAvailableYears = () => {
    if (availableYears.length > 0) {
      // Convert all values to numbers and sort in descending order
      return availableYears
        .map(year => parseInt(year, 10))
        .filter(year => !isNaN(year))
        .sort((a, b) => b - a);
    }
    // Fallback to current year and previous 10 years
    const currentYear = new Date().getFullYear();
    return Array.from({ length: 11 }, (_, i) => currentYear - i);
  };

  const years = getAvailableYears();

  // Check if a date is available (within available years)
  const isDateAvailable = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth(); // 0-11 (January = 0, December = 11)
    
    // Check if year is available
    if (!years.includes(year)) return false;
    
    // For now, only allow specific months: March(2), June(5), September(8), October(9)
    const allowedMonths = [2, 5, 8, 9]; // March, June, September, October
    
    return allowedMonths.includes(month);
  };

  // Check if a date is disabled (outside available years or not in allowed months)
  const isDateDisabled = (date) => {
    return !isDateAvailable(date);
  };

  // Update current month when available years change
  useEffect(() => {
    const availableYearsList = getAvailableYears();
    if (availableYearsList.length > 0) {
      const currentYear = currentMonth.getFullYear();
      const currentMonthIndex = currentMonth.getMonth();
      const allowedMonths = [2, 5, 8, 9]; // March, June, September, October
      
      // Check if current year is available
      if (!availableYearsList.includes(currentYear)) {
        // If current year is not available, set to March of first available year
        setCurrentMonth(new Date(availableYearsList[0], 2, 1)); // March of first available year
      } else if (!allowedMonths.includes(currentMonthIndex)) {
        // If year is available but month is not, set to first available month of that year
        setCurrentMonth(new Date(currentYear, 2, 1)); // March of current year
      }
    }
  }, [availableYears]);

  // Get days in month
  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  // Get first day of month
  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  // Format date for display
  const formatDate = (date, format = "short") => {
    if (!date) return "";
    
    if (format === "month") {
      return date.toLocaleDateString("en-US", { year: "numeric", month: "short" });
    }
    
    if (format === "full") {
      return date.toLocaleDateString("en-US", { 
        year: "numeric", 
        month: "2-digit", 
        day: "2-digit" 
      });
    }
    
    return date.toLocaleDateString("en-US", { year: "numeric", month: "short" });
  };

  // Format date range for API
  const formatDateRangeForAPI = (from, to, type) => {
    if (!from) return null;
    
    if (type === "month") {
      const fromStr = from.toISOString().slice(0, 7); // YYYY-MM
      if (!to) return fromStr;
      const toStr = to.toISOString().slice(0, 7); // YYYY-MM
      return fromStr === toStr ? fromStr : `${fromStr}:${toStr}`;
    }
    
    if (type === "full") {
      const fromStr = from.toISOString().slice(0, 10); // YYYY-MM-DD
      if (!to) return fromStr;
      const toStr = to.toISOString().slice(0, 10); // YYYY-MM-DD
      return fromStr === toStr ? fromStr : `${fromStr}:${toStr}`;
    }
    
    return null;
  };

  // Handle date selection
  const handleDateSelect = (date) => {
    if (isDateDisabled(date)) return;

    if (currentView === "from") {
      setTempRange({ from: date, to: tempRange.to });
      setCurrentView("to");
    } else if (currentView === "to") {
      if (date < tempRange.from) {
        setTempRange({ from: date, to: tempRange.from });
      } else {
        setTempRange({ from: tempRange.from, to: date });
      }
      setCurrentView("range");
    } else {
      setTempRange({ from: date, to: null });
      setCurrentView("to");
    }
  };

  // Apply date range
  const applyDateRange = () => {
    setDateRange(tempRange);
    const apiFormat = formatDateRangeForAPI(tempRange.from, tempRange.to, selectedRangeType);
    onDateRangeChange(apiFormat, tempRange);
    setIsOpen(false);
  };

  // Clear date range
  const clearDateRange = () => {
    setDateRange({ from: null, to: null });
    setTempRange({ from: null, to: null });
    onDateRangeChange(null, { from: null, to: null });
  };

  // Navigate months
  const navigateMonth = (direction) => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      newMonth.setMonth(prev.getMonth() + direction);
      
      // Check if the new month is within available years
      const newYear = newMonth.getFullYear();
      
      // Only restrict by year, allow navigation to all months
      if (!years.includes(newYear)) {
        return prev; // Stay on current month if year is not available
      }
      
      return newMonth;
    });
  };

  // Check if navigation is disabled in a direction
  const isNavigationDisabled = (direction) => {
    const testMonth = new Date(currentMonth);
    testMonth.setMonth(currentMonth.getMonth() + direction);
    
    const testYear = testMonth.getFullYear();
    
    // Only disable navigation if year is not available
    return !years.includes(testYear);
  };

  // Generate calendar days
  const generateCalendarDays = () => {
    const daysInMonth = getDaysInMonth(currentMonth);
    const firstDay = getFirstDayOfMonth(currentMonth);
    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
      days.push(date);
    }

    return days;
  };

  const calendarDays = generateCalendarDays();

  // Get display text
  const getDisplayText = () => {
    if (!dateRange.from && !dateRange.to) {
      return placeholder;
    }
    
    if (dateRange.from && !dateRange.to) {
      return formatDate(dateRange.from, selectedRangeType);
    }
    
    if (dateRange.from && dateRange.to) {
      if (selectedRangeType === "month") {
        const fromText = dateRange.from.toLocaleDateString("en-US", { year: "numeric", month: "2-digit" });
        const toText = dateRange.to.toLocaleDateString("en-US", { year: "numeric", month: "2-digit" });
        return `${fromText} - ${toText}`;
      } else {
        const fromText = dateRange.from.toLocaleDateString("en-US", { year: "numeric", month: "2-digit", day: "2-digit" });
        const toText = dateRange.to.toLocaleDateString("en-US", { year: "numeric", month: "2-digit", day: "2-digit" });
        return `${fromText} - ${toText}`;
      }
    }
    
    return placeholder;
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className="w-full justify-between shadow-sm hover:shadow-md transition-shadow"
      >
        <div className="flex items-center">
          <Calendar className="h-4 w-4 mr-2" />
          <span className="truncate">{getDisplayText()}</span>
        </div>
        {dateRange.from && (
          <X 
            className="h-4 w-4 ml-2 hover:text-red-500" 
            onClick={(e) => {
              e.stopPropagation();
              clearDateRange();
            }}
          />
        )}
      </Button>

      {isOpen && (
        <Card className="absolute top-full left-0 mt-2 w-80 z-50 shadow-lg border-slate-200 bg-white">
          <CardContent className="p-4">
            {/* Range Type Selector */}
            <div className="flex gap-2 mb-4">
              <Button
                variant={selectedRangeType === "month" ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedRangeType("month")}
                className="flex-1"
                title="Select by month (e.g., 2023-03 or 2023-03:2023-08)"
              >
                Month Range
              </Button>
              <Button
                variant={selectedRangeType === "full" ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedRangeType("full")}
                className="flex-1"
                title="Select specific dates (e.g., 2023-03-01:2023-08-31)"
              >
                Full Date Range
              </Button>
            </div>

            {/* Year Selection - Moved to top */}
            <div className="mb-4">
              <div className="text-xs font-medium text-gray-700 mb-2">Select Year:</div>
              {years.length > 0 ? (
                <div className="min-w-[200px]">
                  <select
                    value={currentMonth.getFullYear()}
                    onChange={(e) => {
                      const selectedYear = parseInt(e.target.value);
                      const currentMonthIndex = currentMonth.getMonth();
                      const allowedMonths = [2, 5, 8, 9]; // March, June, September, October
                      
                      // If current month is not allowed in the new year, default to March
                      const newMonthIndex = allowedMonths.includes(currentMonthIndex) ? currentMonthIndex : 2;
                      const newDate = new Date(selectedYear, newMonthIndex, 1);
                      setCurrentMonth(newDate);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  >
                    {years.map(year => (
                      <option key={year} value={year}>
                        {year}
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <div className="text-xs text-orange-500 p-2 bg-orange-50 rounded">
                  No years available. Please configure available years.
                </div>
              )}
            </div>

            {/* Range Type Explanation */}
            <div className="mb-3 p-2 bg-blue-50 rounded text-xs text-blue-700">
              <div>
                {selectedRangeType === "month" 
                  ? "Month format: 2023-03 or 2023-03:2023-08"
                  : "Date format: 2023-03-01:2023-08-31"
                }
              </div>
            </div>

            {/* Selection Status */}
            <div className="mb-3 p-2 bg-gray-50 rounded text-xs">
              <div className="font-medium text-gray-700">
                {currentView === "from" && "Click to select start date"}
                {currentView === "to" && "Click to select end date"}
                {currentView === "range" && "Click to start new selection"}
              </div>
              {tempRange.from && (
                <div className="text-gray-600 mt-1">
                  Start: {formatDate(tempRange.from, selectedRangeType)}
                  {tempRange.to && ` | End: ${formatDate(tempRange.to, selectedRangeType)}`}
                </div>
              )}
            </div>

            {/* Calendar Header */}
            <div className="flex items-center justify-between mb-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateMonth(-1)}
                className="hover:bg-gray-100"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <div className="text-center">
                <div className="font-semibold text-gray-900">
                  {currentMonth.toLocaleDateString("en-US", { month: "long", year: "numeric" })}
                </div>
                <div className="text-xs text-gray-500">
                  {isDateAvailable(currentMonth) ? "Available" : "Not available"}
                </div>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateMonth(1)}
                className="hover:bg-gray-100"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1 mb-4">
              {/* Day headers */}
              {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(day => (
                <div key={day} className="text-center text-xs font-medium text-gray-500 py-1">
                  {day}
                </div>
              ))}
              
              {/* Calendar days */}
              {calendarDays.map((day, index) => (
                <div key={index} className="text-center">
                  {day ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      className={`w-8 h-8 p-0 text-xs transition-colors ${
                        isDateDisabled(day) 
                          ? "text-gray-300 cursor-not-allowed bg-gray-50 border border-gray-100" 
                          : "hover:bg-blue-100 text-gray-900 border border-transparent hover:border-blue-200 font-medium"
                      } ${
                        tempRange.from && day.getTime() === tempRange.from.getTime()
                          ? "bg-blue-500 text-white hover:bg-blue-600 border-blue-500 font-bold"
                          : ""
                      } ${
                        tempRange.to && day.getTime() === tempRange.to.getTime()
                          ? "bg-blue-500 text-white hover:bg-blue-600 border-blue-500 font-bold"
                          : ""
                      } ${
                        tempRange.from && tempRange.to && 
                        day > tempRange.from && day < tempRange.to
                          ? "bg-blue-100 border-blue-200"
                          : ""
                      }`}
                      onClick={() => handleDateSelect(day)}
                      disabled={isDateDisabled(day)}
                      title={isDateDisabled(day) ? "This date is not available for selection" : "Click to select this date"}
                    >
                      {day.getDate()}
                    </Button>
                  ) : (
                    <div className="w-8 h-8" />
                  )}
                </div>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={applyDateRange}
                disabled={!tempRange.from}
                className="flex-1"
              >
                Apply
              </Button>
            </div>

            {/* Selected Range Display */}
            {tempRange.from && (
              <div className="mt-3 p-2 bg-gray-50 rounded text-xs">
                <div className="font-medium">Selected Range:</div>
                <div className="text-gray-600">
                  {formatDateRangeForAPI(tempRange.from, tempRange.to, selectedRangeType)}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DateRangePicker; 