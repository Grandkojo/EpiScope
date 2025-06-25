import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Loader2 } from "lucide-react";

const StatCard = ({ title, value, description, icon, isLoading, error }) => {
  // Helper function to extract error message
  const getErrorMessage = (error) => {
    if (typeof error === 'string') {
      return error;
    }
    if (error?.message) {
      return error.message;
    }
    if (error?.response?.data?.message) {
      return error.response.data.message;
    }
    if (error?.response?.data?.detail) {
      return error.response.data.detail;
    }
    return 'An error occurred';
  };

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-red-600">
            Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-red-600">{getErrorMessage(error)}</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          {isLoading ? "Loading..." : title}
        </CardTitle>
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        ) : (
          icon
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{isLoading ? "..." : value}</div>
        <p className="text-xs pt-1 text-muted-foreground">
          {isLoading ? "Loading data..." : description}
        </p>
      </CardContent>
    </Card>
  );
};

export { StatCard };
