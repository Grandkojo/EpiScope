import { useQuery } from "@tanstack/react-query"
import api from "../api"
export const useAnalyticsData = (disease_name,year) => {}

export const useNHIAStatusAnalyticsData = (disease_name,year) => {
    return useQuery({
        queryKey: ['nhia_status_analytics', disease_name, year],
        queryFn: async () => {
            if (year) {
                const response = await api.get(`analytics/nhia-status/?disease_name=${disease_name}&year=${year}`)
                return response.data
            } else {
                const response = await api.get(`analytics/nhia-status/?disease_name=${disease_name}`)
                return response.data
            }
        },
        enabled: !!disease_name
    })
}

export const usePregnancyStatusAnalyticsData =  (disease_name,year) => {
    return useQuery({
        queryKey: ['pregnancy_status_analytics', disease_name, year],
        queryFn: async () => {
            if (year) {
                const response = await api.get(`analytics/pregnancy-status/?disease_name=${disease_name}&year=${year}`)
                return response.data
            } else {
                const response = await api.get(`analytics/pregnancy-status/?disease_name=${disease_name}`)
                return response.data
            }
        },
        enabled: !!disease_name
    })
}

