import { useQuery } from "@tanstack/react-query"
import api from "../api"

export const useDiseases = () => {
  return useQuery({
    queryKey: ['diseases'],
    queryFn: async () => {
      const response = await api.get("diseases/all/")
      return response.data
    },
  })
}