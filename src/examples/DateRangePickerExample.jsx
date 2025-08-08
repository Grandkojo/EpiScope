import React, { useState } from 'react';
import DateRangePicker from '../components/ui/DateRangePicker';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

/**
 * Example component demonstrating DateRangePicker usage with API integration
 */
const DateRangePickerExample = () => {
  const [selectedDateRange, setSelectedDateRange] = useState(null);
  const [apiResponse, setApiResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Mock available years from your API
  const availableYears = [2020, 2021, 2022, 2023, 2024, 2025];

  // Handle date range change with API call
  const handleDateRangeChange = async (apiFormat, dateRangeObj) => {
    setSelectedDateRange({ apiFormat, dateRangeObj });
    
    if (apiFormat) {
      setIsLoading(true);
      
      try {
        // Example API call with the date range
        const response = await fetch('/api/analytics', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer your-token-here'
          },
          body: JSON.stringify({
            date_range: apiFormat,
            // Add other parameters as needed
            disease: 'diabetes',
            region: 'all'
          })
        });

        if (response.ok) {
          const data = await response.json();
          setApiResponse(data);
        } else {
          console.error('API request failed:', response.statusText);
        }
      } catch (error) {
        console.error('Error making API request:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Date Range Picker Example</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            <DateRangePicker
              onDateRangeChange={handleDateRangeChange}
              availableYears={availableYears}
              placeholder="Select date range"
              className="w-64"
            />
            
            {isLoading && (
              <div className="text-sm text-gray-500">
                Loading data...
              </div>
            )}
          </div>

          {selectedDateRange && (
            <div className="space-y-2">
              <h3 className="font-semibold">Selected Date Range:</h3>
              <div className="bg-gray-50 p-3 rounded text-sm">
                <div><strong>API Format:</strong> {selectedDateRange.apiFormat}</div>
                <div><strong>From:</strong> {selectedDateRange.dateRangeObj.from?.toLocaleDateString()}</div>
                <div><strong>To:</strong> {selectedDateRange.dateRangeObj.to?.toLocaleDateString()}</div>
              </div>
            </div>
          )}

          {apiResponse && (
            <div className="space-y-2">
              <h3 className="font-semibold">API Response:</h3>
              <pre className="bg-gray-50 p-3 rounded text-sm overflow-auto">
                {JSON.stringify(apiResponse, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Supported Date Formats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div><strong>Single Month:</strong> "2023-03"</div>
            <div><strong>Month Range:</strong> "2023-03:2023-08"</div>
            <div><strong>Full Date Range:</strong> "2023-03-01:2023-08-31"</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DateRangePickerExample; 