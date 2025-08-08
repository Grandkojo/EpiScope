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


export const usePrincipalDiagnosesAnalyticsData = (disease_name,year, orgname) => {
    return useQuery({
        queryKey: ['principal_diagnoses_analytics', disease_name, year, orgname],
        queryFn: async () => {
            const response = await api.get(`analytics/principal-diagnoses/?disease=${disease_name}&year=${year}&orgname=${orgname}`)
            return response.data
        },
        enabled: !!disease_name && !!year && !!orgname
    })
}

export const useAdditionalDiagnosesAnalyticsData = (disease_name,year, orgname) => {
    return useQuery({
        queryKey: ['additional_diagnoses_analytics', disease_name, year, orgname],
        queryFn: async () => {
            const response = await api.get(`analytics/additional-diagnoses/?disease=${disease_name}&year=${year}&orgname=${orgname}`)
            return response.data
        },
        enabled: !!disease_name && !!year && !!orgname
    })
}

export const useSexDistributionAnalyticsData = (disease_name,year, orgname) => {
    return useQuery({
        queryKey: ['sex_distribution_analytics', disease_name, year, orgname],
        queryFn: async () => {
            const response = await api.get(`analytics/sex-distribution/?disease=${disease_name}&year=${year}&orgname=${orgname}`)
            return response.data
        },
        enabled: !!disease_name && !!year && !!orgname
    })
}

export const useAgeDistributionAnalyticsData = (disease_name,year, orgname) => {
    return useQuery({
        queryKey: ['age_distribution_analytics', disease_name, year, orgname],
        queryFn: async () => {
            const response = await api.get(`analytics/age-distribution/?disease=${disease_name}&year=${year}&orgname=${orgname}`)
            return response.data
        },
        enabled: !!disease_name && !!year && !!orgname
    })
}

export const useLocalitiesTrendAnalyticsData = (disease_name,year, orgname, locality) => {
    return useQuery({
        queryKey: ['localities_trend_analytics', disease_name, year, orgname, locality],
        queryFn: async () => {
            const response = await api.get(`analytics/trends/?disease=${disease_name}&year=${year}&orgname=${orgname}&locality=${locality}`)
            return response.data
        },
        enabled: !!disease_name && !!year && !!orgname && !!locality
    })
}
