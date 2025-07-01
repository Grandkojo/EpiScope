// import { Search, User } from "lucide-react"

// const UserHeader = () => {
//   return (
//     <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center relative">
//       {/* Left: Title */}
//       <div className="flex items-center min-w-0">
//         <h2 className="text-lg font-semibold text-gray-900 whitespace-nowrap">User Dashboard</h2>
//       </div>
//       {/* Center: Search */}
//       <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[320px]">
//         <div className="relative">
//           <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
//           <input
//             type="text"
//             placeholder="Search your health data..."
//             className="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full transition-all text-gray-900"
//           />
//         </div>
//       </div>
//       {/* Right: User Icon */}
//       <div className="flex items-center space-x-4 ml-auto">
//         <button className="bg-red-400 rounded-full p-2 border border-red-400">
//           <User className="h-5 w-5 text-gray-900" />
//         </button>
//       </div>
//     </header>
//   )
// }

// export default UserHeader 

import { useState, useRef, useEffect } from "react";
import { Search, User, Settings, LogOut } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import { useQuery } from "@tanstack/react-query";
import { useCrossPageNotifications } from "../hooks/use-cross-page-notifications";
import api from "../api";

const UserHeader = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();
  const { showOnNextPage } = useCrossPageNotifications()
  // Move useQuery to the top level of the component
  const { data: userProfile, isLoading, error } = useQuery({
    queryKey: ["userProfile"],
    queryFn: async () => {
      const response = await api.get("user/profile");
      return response.data;
    },
    enabled: !!ACCESS_TOKEN,
  });

  const handleProfile = () => {
    setIsOpen(!isOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.removeItem(REFRESH_TOKEN);
    showOnNextPage({
      type: "success",
      title: "Logout successful",
      message: "You have been logged out successfully",
      duration: 3000,
    },
    "/login",
  )
  };

  const handleSettings = () => {
    setIsOpen(false);
    navigate('/users/settings/');
  }

  // Close dropdown if clicked outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 flex items-center relative">
      {/* Left: Title */}
      <div className="flex items-center min-w-0">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white whitespace-nowrap">
          User Dashboard
        </h2>
      </div>

      {/* Center: Search */}
      <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[320px]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search your health data..."
            className="pl-10 pr-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-full transition-all text-gray-900 dark:text-white"
          />
        </div>
      </div>

      {/* Right: User Icon + Dropdown */}
      <div className="flex items-center  ml-auto relative" ref={dropdownRef}>
        <button
          onClick={handleProfile}
          className="bg-white rounded-full p-2 border border-blue-600 hover:ring-2 ring-offset-1 ring-blue-500 transition"
        >
          <User className="h-5 w-5 text-black" />
        </button>

        {isOpen && (
          <div className="absolute right-0 top-14 w-64 bg-white dark:bg-gray-900 rounded-lg shadow-xl border dark:border-gray-700 z-50">
            <div className="p-4 border-b dark:border-gray-700">
              {isLoading ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Loading profile...</p>
              ) : error ? (
                <p className="text-sm text-red-500 dark:text-red-400">Error loading profile</p>
              ) : (
                <>
                  <p className="text-sm font-medium text-gray-800 dark:text-white">
                    {userProfile?.username || "User"}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {userProfile?.email || "user@example.com"}
                  </p>
                </>
              )}
            </div>

            <div className="p-2">
              <button
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                onClick={() => handleSettings()}
              >
                <Settings className="w-4 h-4 mr-2"/>
                Settings
              </button>
              <button
                onClick={() => handleLogout()}
                className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 cursor-pointer dark:hover:bg-red-900 rounded"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default UserHeader;

