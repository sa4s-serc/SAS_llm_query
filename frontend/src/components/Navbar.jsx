import { Link, useLocation } from "react-router-dom";
import { dataState } from "../context/DataProvider";

const Navbar = () => {
  const { data, setData } = dataState();
  const location = useLocation();
  
  return (
    <div className="bg-gradient-to-r from-slate-800 to-slate-900 shadow-lg">
      <div className="container mx-auto px-4 py-5">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex gap-6">
            {[
              { path: "/aneesh", label: "Aneesh", range: "1-33" },
              { path: "/sathvika", label: "Sathvika", range: "34-66" },
              { path: "/bassam", label: "Bassam", range: "67-100" }
            ].map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`relative px-3 py-2 text-sm font-medium rounded-md transition-all duration-200 hover:bg-white/10 
                  ${location.pathname === link.path 
                    ? 'text-blue-300' 
                    : 'text-gray-300 hover:text-white'
                  }`}
              >
                <span className="block">{link.label}</span>
                <span className="block text-xs text-gray-400 mt-0.5">
                  Conversations {link.range}
                </span>
                {location.pathname === link.path && (
                  <span className="absolute bottom-0 left-0 h-0.5 w-full bg-blue-400 rounded-full" />
                )}
              </Link>
            ))}
          </div>
          
          <div className="flex items-center gap-3 bg-slate-700/50 px-4 py-2 rounded-lg">
            <span className="text-gray-300 text-sm">Data Source:</span>
            <select 
              value={data} 
              onChange={(e) => setData(e.target.value)}
              className="bg-slate-600 text-white px-3 py-1.5 rounded-md text-sm font-medium 
                border border-slate-500 hover:border-slate-400 focus:outline-none focus:ring-2 
                focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
            >
              <option value="cqwen">CQwen</option>
              <option value="mini">Mini</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navbar;