import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Activity, PieChart } from 'lucide-react';
import { foodService } from '../services/api';

const data = [
  { name: 'Mon', calories: 2100 },
  { name: 'Tue', calories: 1800 },
  { name: 'Wed', calories: 2400 },
  { name: 'Thu', calories: 2200 },
  { name: 'Fri', calories: 2000 },
  { name: 'Sat', calories: 2500 },
  { name: 'Sun', calories: 1900 },
];

const Dashboard = () => {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Fetch food history
    foodService.getUserHistory().then(res => setHistory(res.data));
  }, []);

  return (
    <div className="p-8 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-8">Your Nutrition Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md flex items-center space-x-4">
          <div className="bg-blue-100 p-3 rounded-full text-blue-600">
            <Activity size={24} />
          </div>
          <div>
            <div className="text-gray-500">Today's Calories</div>
            <div className="text-2xl font-bold">1,850 kcal</div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md flex items-center space-x-4">
          <div className="bg-green-100 p-3 rounded-full text-green-600">
            <TrendingUp size={24} />
          </div>
          <div>
            <div className="text-gray-500">Average Calorie Intake</div>
            <div className="text-2xl font-bold">2,100 kcal</div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md flex items-center space-x-4">
          <div className="bg-purple-100 p-3 rounded-full text-purple-600">
            <PieChart size={24} />
          </div>
          <div>
            <div className="text-gray-500">Protein Intake</div>
            <div className="text-2xl font-bold">85g</div>
          </div>
        </div>
      </div>

      <div className="bg-white p-8 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-bold mb-4">Weekly Calorie Intake</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="calories" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">Recent Food History</h2>
        <div className="space-y-4">
          {history.length > 0 ? history.map((item, index) => (
            <div key={index} className="flex items-center justify-between border-b pb-2">
              <div>
                <div className="font-bold">{item.food_name}</div>
                <div className="text-sm text-gray-500">{item.cooking_method}</div>
              </div>
              <div className="text-blue-600 font-bold">{item.nutrition.calories} kcal</div>
            </div>
          )) : (
            <div className="text-gray-500">No recent activity. Start by analyzing a food image!</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
