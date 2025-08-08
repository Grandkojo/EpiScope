import { useQuery } from "@tanstack/react-query"
import api from "../api"

export const useLocalities = (hospital) => {
  return useQuery({
    queryKey: ['localities', hospital],
    queryFn: async () => {
      const response = await api.get(`hospital-localities/by-hospital/?hospital=${hospital}`)
      return response.data
    },
    enabled: !!hospital,
    // Aggressive caching for better performance
    staleTime: 5 * 60 * 1000, // 5 minutes - data considered fresh for 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes - keep in cache for 10 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
    refetchOnMount: false, // Don't refetch when component mounts if data exists
    refetchOnReconnect: false, // Don't refetch when network reconnects
    retry: 1, // Only retry once on failure
    retryDelay: 1000, // Wait 1 second before retry
  })
}