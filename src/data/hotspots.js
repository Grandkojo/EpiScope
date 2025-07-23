import { useQuery } from "@tanstack/react-query"
import api from "../api"

export const useHotspots = (region, disease, year) => {
  return useQuery({
    queryKey: ['hotspots', region, disease, year],
    queryFn: async () => {
      const response = await api.get(`hotspots/national/?disease=${disease}&region=${region}&year=${year}`)
      return response.data
    },
    enabled: !!region && !!disease && !!year
  })
}