#calculate the delta between two disease to update the statcard
def calculate_delta(current, previous):
    diff = current - previous
    pct_change = round((diff / previous) * 100, 1) if previous else 0
    direction = "up" if diff > 0 else "down" if diff < 0 else "nil"
    return {
        "value": current,
        "change": abs(diff),
        "percent_change": abs(pct_change),
        "direction": direction
    }

# def summarize_insights(df, disease, current_year, previous_year=None):
#     row = df[df["periodname"] == current_year].iloc[0]
#     summary = {
#         "title": f"Summary of {disease} Cases",
#         "year": current_year,
#         "total_count": row["Diabetes Mellitus"],
#         "male": row.get("Diabetes Mellitus +AC0- Male"),
#         "female": row.get("Diabetes Mellitus +AC0- Female"),
#         "deaths": row["Diabetes mellitus deaths"],
#         "lab_confirmed": row["Diabetes mellitus lab confirmed cases"]
#     }

#     if previous_year:
#         prev = df[df["periodname"] == previous_year].iloc[0]
#         diff = row["Diabetes Mellitus"] - prev["Diabetes Mellitus"]
#         pct = (diff / prev["Diabetes Mellitus"]) * 100
#         summary["trend_summary"] = f"Compared to {previous_year}, total cases {'increased' if diff > 0 else 'decreased'} by {abs(diff)} ({pct:.1f}%)."
    
#     return summary
