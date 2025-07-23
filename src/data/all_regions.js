import { useQuery } from "@tanstack/react-query"
import api from "../api"

export const useRegions = () => {
  return useQuery({
    queryKey: ['regions'],
    queryFn: async () => {
      const response = await api.get("regions/all/")
      return response.data
    },
  })
}