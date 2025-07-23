import { StatCard } from "../StatCard";
import { TrendingUp, AlertCircle, Loader2, Skull, TestTubeDiagonal, HeartPulse } from "lucide-react";

export const DiabetesDataStats = (dashboardData, isDashboardDataLoading, error, selectedDiseaseL) => {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Display counts */}
        <StatCard
          title={
            dashboardData?.error
              ? "Error"
              : dashboardData?.[selectedDiseaseL]
                ? `${dashboardData?.[selectedDiseaseL]?.title} - ${dashboardData?.[selectedDiseaseL]?.year}`
                : "Loading..."
          }
          value={
            isDashboardDataLoading
              ? "..."
              : dashboardData?.error
                ? "No data"
                : dashboardData?.[selectedDiseaseL]?.total_count || 0
          }
          description={
            isDashboardDataLoading ? (
              "Loading data..."
            ) : dashboardData?.error ? (
              dashboardData.error
            ) : dashboardData?.[selectedDiseaseL]?.delta_vals === "up" ? (
              <TrendingUp className="h-4 w-4 text-orange-500" />
            ) : (
              "No delta rate"
            )
          }
          icon={
            isDashboardDataLoading ? (
              <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
            ) : dashboardData?.error ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : (
              <TrendingUp className="h-4 w-4 text-orange-500" />
            )
          }
          isLoading={isDashboardDataLoading}
          error={dashboardData?.error || error}
        />

        {/* {<StatCard
          title="Death Counts"
          value={Math.round(
            healthMetrics.populationAtRisk *
            (selectedRegion === "All Regions" ? 1 : 0.15)
          )}
          description="In your region"
          // icon={<Users className="h-4 w-4 text-purple-500" />}
          icon={<Skull className="h-5 w-5 text-red-600" />}

        />} */}

        <StatCard
          title={
            dashboardData?.error
              ? "Error"
              : dashboardData?.[selectedDiseaseL]
                ? "Death Counts"
                : "Loading..."
          }
          value={
            isDashboardDataLoading
              ? "..."
              : dashboardData?.error
                ? "No data"
                : dashboardData?.[selectedDiseaseL]?.deaths_count || 0
          }
          description={
            isDashboardDataLoading ? (
              "Loading data..."
            ) : dashboardData?.error ? (
              dashboardData.error
            ) : dashboardData?.[selectedDiseaseL]?.delta_vals === "up" ? (
              <Skull className="h-5 w-5 text-red-600" />
            ) : (
              "No delta rate"
            )
          }
          icon={
            isDashboardDataLoading ? (
              <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
            ) : dashboardData?.error ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : (
              <Skull className="h-5 w-5 text-red-600" />
            )
          }
          isLoading={isDashboardDataLoading}
          error={dashboardData?.error || error}
        />

        <StatCard
          title={
            dashboardData?.error
              ? "Error"
              : dashboardData?.[selectedDiseaseL]
                ? "Lab Confirmed Cases"
                : "Loading..."
          }
          value={
            isDashboardDataLoading
              ? "..."
              : dashboardData?.error
                ? "No data"
                : dashboardData?.[selectedDiseaseL]?.lab_confirmed_cases_count ||
                0
          }
          description={
            isDashboardDataLoading ? (
              "Loading data..."
            ) : dashboardData?.error ? (
              dashboardData.error
            ) : dashboardData?.[selectedDiseaseL]?.delta_vals === "up" ? (
              <TestTubeDiagonal className="h-5 w-5 text-red-600" />
            ) : (
              "No delta rate"
            )
          }
          icon={
            isDashboardDataLoading ? (
              <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
            ) : dashboardData?.error ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : (
              <TestTubeDiagonal className="h-5 w-5 text-red-600" />
            )
          }
          isLoading={isDashboardDataLoading}
          error={dashboardData?.error || error}
        />

        <StatCard
          title="Health Status"
          value="Good"
          description="Your current health status"
          icon={<HeartPulse className="h-4 w-4 text-green-500" />}
        />

        {/* <StatCard
          title="Risk Level"
          value="Low"
          description="Based on your region"
          icon={<Activity className="h-4 w-4 text-blue-500" />}
        /> */}

        {/* 

        <StatCard
          title="Death Counts"
          value={Math.round(
            healthMetrics.populationAtRisk *
              (selectedRegion === "All Regions" ? 1 : 0.15)
          )}
          description="In your region"
          // icon={<Users className="h-4 w-4 text-purple-500" />}
          icon={<Skull className="h-5 w-5 text-red-600" />}

        /> */}
      </div>
    )
}

// export const MeningitisDataKeys = () => {}

// export const CholeraDataKeys = () => {}

// export const MalariaDataKeys = () => {}