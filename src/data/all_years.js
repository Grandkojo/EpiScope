import { useQuery } from "@tanstack/react-query"
import api from "../api"

export const useDiseaseYears = (diseaseId) => {
  return useQuery({
    queryKey: ['diseaseYears', diseaseId],
    queryFn: async () => {
      const response = await api.get(`diseases/years/?disease_id=${diseaseId}`)
      return response.data
    },
    enabled: !!diseaseId
  })
}