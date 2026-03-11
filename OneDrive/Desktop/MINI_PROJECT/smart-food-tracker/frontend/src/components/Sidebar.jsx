import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Home, User, LogOut, LayoutDashboard, Upload, History } from 'lucide-react';

const Sidebar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="flex flex-col h-screen w-64 bg-gray-900 text-white p-4 space-y-4">
      <div className="text-2xl font-bold mb-8">Smart Food Tracker</div>
      <Link to="/dashboard" className="flex items-center space-x-2 p-2 hover:bg-gray-800 rounded">
        <LayoutDashboard size={20} />
        <span>Dashboard</span>
      </Link>
      <Link to="/upload" className="flex items-center space-x-2 p-2 hover:bg-gray-800 rounded">
        <Upload size={20} />
        <span>Analyze Food</span>
      </Link>
      <Link to="/history" className="flex items-center space-x-2 p-2 hover:bg-gray-800 rounded">
        <History size={20} />
        <span>Food History</span>
      </Link>
      <Link to="/profile" className="flex items-center space-x-2 p-2 hover:bg-gray-800 rounded">
        <User size={20} />
        <span>Profile</span>
      </Link>
      <button onClick={handleLogout} className="flex items-center space-x-2 p-2 hover:bg-gray-800 rounded mt-auto">
        <LogOut size={20} />
        <span>Logout</span>
      </button>
    </div>
  );
};

export default Sidebar;
