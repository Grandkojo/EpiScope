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

const UserHeader = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  const user = {
    name: "Caleb Ghanney",
    email: "caleb@example.com",
  };


  const handleLogout = () => {
    localStorage.clear(); // or remove specific tokens
    navigate("/login");
  };

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
          onClick={() => setIsOpen(!isOpen)}
          className="bg-red-400 rounded-full p-2 border border-red-400 hover:ring-2 ring-offset-1 ring-red-300 transition"
        >
          <User className="h-5 w-5 text-white" />
        </button>

        {isOpen && (
          <div className="absolute right-0 top-14 w-64 bg-white dark:bg-gray-900 rounded-lg shadow-xl border dark:border-gray-700 z-50">
            <div className="p-4 border-b dark:border-gray-700">
              <p className="text-sm font-medium text-gray-800 dark:text-white">
                {user.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {user.email}
              </p>
            </div>

            <div className="p-2">
              <Link
                to="/settings"
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                onClick={() => setIsOpen(false)}
              >
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900 rounded"
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

