import { useQuery } from "@tanstack/react-query"
import api from "../api"

export const useHospitals = () => {
  return useQuery({
    queryKey: ['hospitals'],
    queryFn: async () => {
      const response = await api.get(`hospitals/`)
      return response.data
    },
    // Aggressive caching for better performance
    staleTime: 10 * 60 * 1000, // 10 minutes - hospitals change less frequently
    cacheTime: 30 * 60 * 1000, // 30 minutes - keep in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
    refetchOnMount: false, // Don't refetch when component mounts if data exists
    refetchOnReconnect: false, // Don't refetch when network reconnects
    retry: 1, // Only retry once on failure
    retryDelay: 1000, // Wait 1 second before retry
  })
}