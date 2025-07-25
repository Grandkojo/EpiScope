export const GenderDistribution = (maleCount, femaleCount) => {
    return [
        { name: "Male", value: maleCount, color: "#ef4444" },
        { name: "Female", value: femaleCount, color: "#22c55e" },
    ]
}

export const NHIAStatusDistribution = (yesCount, noCount) => {
    console.log(yesCount, noCount);
    return [
        { name: "Yes", value: yesCount, color: "#22c55e" },
        { name: "No", value: noCount, color: "#ef4444" },
    ]
}

export const PregnancyStatusDistribution = (yesCount, noCount) => {
    return [
        { name: "Yes", value: yesCount, color: "#22c55e" },
        { name: "No", value: noCount, color: "#ef4444" },
    ]
}