import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Aneesh from "./pages/Aneesh";
import Bassam from "./pages/Bassam";
import Sathvika from "./pages/Sathvika";
import Navbar from "./components/Navbar";
import DataProvider from "./context/DataProvider";

export default function App() {
  return (
    <DataProvider>
      <Router>
        <div className="min-h-screen bg-slate-100">
          <Navbar />
          <div className="container mx-auto p-4">
            <Routes>
              <Route path="/bassam" element={<Bassam />} />
              <Route path="/aneesh" element={<Aneesh />} />
              <Route path="/sathvika" element={<Sathvika />} />
            </Routes>
          </div>
        </div>
      </Router>
    </DataProvider>
  );
}