# DateRangePicker Component

A comprehensive date range picker component that supports different date formats for API integration and integrates with available years from your data source.

## Features

- **Multiple Date Formats**: Supports month ranges (YYYY-MM) and full date ranges (YYYY-MM-DD)
- **API Integration**: Automatically formats dates for your API endpoints
- **Year Filtering**: Only shows years that have data available
- **Visual Feedback**: Clear indication of available vs unavailable dates
- **Responsive Design**: Works well on different screen sizes
- **Accessibility**: Keyboard navigation and screen reader support

## Supported Date Formats

The component outputs dates in the following formats for API integration:

1. **Single Month**: `"2023-03"`
2. **Month Range**: `"2023-03:2023-08"`
3. **Full Date Range**: `"2023-03-01:2023-08-31"`

## Usage

### Basic Usage

```jsx
import DateRangePicker from '../components/ui/DateRangePicker';

const MyComponent = () => {
  const handleDateRangeChange = (apiFormat, dateRangeObj) => {
    console.log('API Format:', apiFormat);
    console.log('Date Range Object:', dateRangeObj);
  };

  return (
    <DateRangePicker
      onDateRangeChange={handleDateRangeChange}
      availableYears={[2020, 2021, 2022, 2023, 2024, 2025]}
    />
  );
};
```

### With API Integration

```jsx
const handleDateRangeChange = async (apiFormat, dateRangeObj) => {
  if (apiFormat) {
    try {
      const response = await fetch('/api/analytics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          date_range: apiFormat,
          disease: 'diabetes',
          region: 'all'
        })
      });
      
      const data = await response.json();
      // Update your component state with the new data
    } catch (error) {
      console.error('Error:', error);
    }
  }
};
```

### With Disease Years Integration

```jsx
import { useDiseaseYears } from '../data/all_years';
import { useDiseases } from '../data/all_diseases';

const AnalyticsComponent = () => {
  const { data: diseases } = useDiseases();
  const selectedDisease = diseases?.find(d => d.disease_name === "Diabetes");
  const { data: diseaseYears } = useDiseaseYears(selectedDisease?.id);
  
  // Extract available years from API data
  const availableYears = diseaseYears 
    ? diseaseYears.map(year => year.periodname).filter(Boolean)
    : [];

  return (
    <DateRangePicker
      onDateRangeChange={handleDateRangeChange}
      availableYears={availableYears}
      placeholder="Select date range"
    />
  );
};
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onDateRangeChange` | `Function` | Required | Callback function called when date range changes |
| `availableYears` | `Array<number>` | `[]` | Array of available years from your API |
| `className` | `string` | `""` | Additional CSS classes |
| `placeholder` | `string` | `"Select date range"` | Placeholder text for the button |
| `disabled` | `boolean` | `false` | Whether the picker is disabled |

## Callback Function

The `onDateRangeChange` callback receives two parameters:

1. **apiFormat** (string | null): The formatted date string for API requests
2. **dateRangeObj** (object): Object containing `from` and `to` Date objects

```jsx
const handleDateRangeChange = (apiFormat, dateRangeObj) => {
  // apiFormat examples:
  // "2023-03" (single month)
  // "2023-03:2023-08" (month range)
  // "2023-03-01:2023-08-31" (full date range)
  // null (when cleared)
  
  // dateRangeObj example:
  // { from: Date, to: Date }
  // { from: Date, to: null }
  // { from: null, to: null }
};
```

## Styling

The component uses Tailwind CSS classes and can be customized with additional classes:

```jsx
<DateRangePicker
  className="w-64 bg-white border-2 border-blue-200"
  // ... other props
/>
```

## Integration with Existing Components

The DateRangePicker is designed to work seamlessly with your existing analytics components. It automatically:

- Filters available years based on your API data
- Disables dates outside the available range
- Provides visual feedback for data availability
- Integrates with your existing UI components

## Example Integration

See `src/examples/DateRangePickerExample.jsx` for a complete example of how to integrate the DateRangePicker with your API endpoints. 