import { useQuery } from "@tanstack/react-query"
import api from "../api"


export const useDashboardData = (disease_name,year) => {
  return useQuery({
    queryKey: ['diseaseYears', year, disease_name],
    queryFn: async () => {
      const response = await api.get(`diseases/dashboard/?disease_name=${disease_name}&year=${year}`)
      return response.data
    },
    enabled: !!year
  })
}