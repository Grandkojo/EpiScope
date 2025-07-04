import React from "react";

export const MapComponent = ({ hotspots = [], onMarkerClick }) => (
  <svg
    viewBox="0 0 100 100"
    className="absolute inset-0 w-full h-full"
    style={{ display: "block" }}
  >
    <path
      d="M25 10 L75 10 L80 15 L85 20 L85 25 L80 30 L75 35 L70 40 L75 45 L80 50 L85 55 L85 60 L80 65 L90 80 L80 85 L75 90 L70 95 L65 95 L40 95 L45 90 L40 92 L25 90 L10 85 L15 80 L20 75 L15 70 L10 65 L15 60 L20 55 L25 50 L20 45 L25 40 L20 35 L15 30 L10 25 L15 20 L20 15 L25 10 Z"
      fill="#e0f2fe"
      stroke="#0369a1"
      strokeWidth="0.8"
    />

    <line x1="10" y1="25" x2="85" y2="25" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
    <line x1="35" y1="10" x2="35" y2="25" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
    <line x1="55" y1="10" x2="55" y2="25" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="25" y1="40" x2="70" y2="40" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="45" y1="25" x2="45" y2="40" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="20" y1="55" x2="85" y2="55" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
    <line x1="35" y1="40" x2="35" y2="55" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="60" y1="40" x2="60" y2="55" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="73" y1="80" x2="80" y2="85" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="15" y1="80" x2="74" y2="80" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="25" y1="55" x2="25" y2="75" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="25" y1="55" x2="25" y2="80" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="37" y1="55" x2="37" y2="80" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="53" y1="55" x2="53" y2="80" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
    <line x1="73" y1="55" x2="73" y2="80" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />


    <line x1="35" y1="80" x2="35" y2="91" stroke="#64798b" strokeWidth="0.4" strokeDasharray="3,2" />

    <line x1="55" y1="95" x2="55" y2="80" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

    <text x="30" y="17" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="25" dy="0">
        Upper West
      </tspan>
    </text>
    <text x="45" y="16" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="45" dy="0">
        Upper East
      </tspan>
    </text>
    <text x="70" y="16" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="70" dy="0">
        North East
      </tspan>
    </text>

    <text x="30" y="31" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="30" dy="0">
        Savannah
      </tspan>
    </text>

    <text x="65" y="31" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="65" dy="0">
        Northern
      </tspan>
    </text>

    <text x="30" y="45" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="30" dy="0">
        Bono
      </tspan>
    </text>

    <text x="45" y="45" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="45" dy="0">
        Bono East
      </tspan>
    </text>

    <text x="55" y="45" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="65" dy="0">
        Oti
      </tspan>
    </text>

    <text x="20" y="62" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="20" dy="0">
        Western
      </tspan>
      <tspan x="20" dy="3">
        North
      </tspan>
    </text>
    <text x="30" y="62" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="30" dy="0">
        Ahafo
      </tspan>
    </text>
    <text x="45" y="62" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="45" dy="0">
        Ashanti
      </tspan>
    </text>
    <text x="65" y="62" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="65" dy="0">
        Eastern
      </tspan>
    </text>
    <text x="80" y="76" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="80" dy="0">
        Volta
      </tspan>
    </text>

    <text x="20" y="85" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="20" dy="0">
        Western
      </tspan>
    </text>

    <text x="40" y="85" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="40" dy="0">
        Central
      </tspan>
    </text>

    <text x="60" y="85" fontSize="1.8" fill="#374151" fontWeight="bold" textAnchor="middle">
      <tspan x="60" dy="0">
        Greater
      </tspan>
      <tspan x="60" dy="3">
        Accra
      </tspan>
    </text>

    {/* Render markers */}
    {hotspots
      .filter(hotspot =>
        hotspot.coordinates &&
        typeof hotspot.coordinates.x === "number" &&
        typeof hotspot.coordinates.y === "number"
      )
      .map((hotspot) => (
        <g
          key={hotspot.id}
          onClick={() => onMarkerClick?.(hotspot)}
          style={{ cursor: "pointer" }}
        >
          {/* Minimal pulsing effect (very subtle) */}
          <circle
            cx={hotspot?.coordinates?.x}
            cy={hotspot?.coordinates?.y}
            r={2.5}
            fill={hotspot?.color}
            opacity={0.10}
          >
            <animate
              attributeName="r"
              values="2.5;3.2;2.5"
              dur="2.5s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              values="0.10;0.05;0.10"
              dur="2.5s"
              repeatCount="indefinite"
            />
          </circle>
          {/* Main marker */}
          <circle
            cx={hotspot?.coordinates?.x}
            cy={hotspot?.coordinates?.y}
            r={2}
            fill={hotspot?.color}
            stroke="#fff"
            strokeWidth={0.5}
          />
          {/* Tooltip (SVG title) */}
          <title>
            {hotspot?.disease} - {hotspot?.city} ({hotspot?.cases} cases)
          </title>
        </g>
      ))}
  </svg>
);

export const Coordinates = [
        {
            name: "UW",
            coordinates: [25, 20]
        },
        {
            name: "UE",
            coordinates: [45, 20]
        },
        {
            name: "NE",
            coordinates: [70, 20]
        },
        {
            name: "SA",
            coordinates: [30, 35]
        },
        {
            name: "NO",
            coordinates: [65, 35]
        },
        {
            name: "BO",
            coordinates: [30, 49]
        },
        {
            name: "BE",
            coordinates: [45, 49]
        },
        {
            name: "OT",
            coordinates: [67, 49]
        },
        {
            name: "WN",
            coordinates: [20, 69]
        },
        {
            name: "AH",
            coordinates: [30, 66]
        },
        {
            name: "AS",
            coordinates: [45, 66]
        },
        {
            name: "ET",
            coordinates: [65, 66]
        },
        {
            name: "VO",
            coordinates: [80, 80]
        },
        {
            name: "WE",
            coordinates: [27, 85]
        },
        {
            name: "CE",
            coordinates: [47, 86]
        },
        {
            name: "GA",
            coordinates: [63, 91]
        }
]
