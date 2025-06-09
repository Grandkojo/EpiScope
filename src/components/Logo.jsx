const Logo = ({ className = "w-8 h-8" }) => {
  return (
    <div className={`${className} flex items-center justify-center`}>
      <svg viewBox="0 0 100 100" className="w-full h-full" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Outer circle - representing global health monitoring */}
        <circle cx="50" cy="50" r="45" stroke="currentColor" strokeWidth="3" className="text-health-400" />

        {/* Cross symbol - medical/health */}
        <rect x="46" y="25" width="8" height="50" rx="4" className="fill-health-500" />
        <rect x="25" y="46" width="50" height="8" rx="4" className="fill-health-500" />

        {/* Data points - representing monitoring */}
        <circle cx="30" cy="30" r="3" className="fill-health-300" />
        <circle cx="70" cy="30" r="3" className="fill-health-300" />
        <circle cx="30" cy="70" r="3" className="fill-health-300" />
        <circle cx="70" cy="70" r="3" className="fill-health-300" />

        {/* Connecting lines - representing data analysis */}
        <path
          d="M30 30 L70 30 L70 70 L30 70 Z"
          stroke="currentColor"
          strokeWidth="1"
          fill="none"
          className="text-health-300 opacity-50"
        />
      </svg>
    </div>
  )
}

export default Logo
