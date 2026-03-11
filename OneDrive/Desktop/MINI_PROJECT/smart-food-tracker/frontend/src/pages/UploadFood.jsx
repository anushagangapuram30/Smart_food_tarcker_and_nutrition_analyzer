import React, { useState } from 'react';
import { Upload, Camera, Trash, Loader2 } from 'lucide-react';
import { foodService } from '../services/api';

const UploadFood = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedImage(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedImage) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedImage);
    try {
      const response = await foodService.uploadImage(formData);
      setAnalysisResult(response.data);
    } catch (error) {
      console.error('Error analyzing image:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setAnalysisResult(null);
  };

  return (
    <div className="p-8 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-8">Analyze Food Image</h1>

      <div className="max-w-4xl mx-auto">
        <div className="bg-white p-8 rounded-lg shadow-md mb-8 flex flex-col items-center">
          {!selectedImage ? (
            <div className="w-full flex flex-col items-center p-12 border-2 border-dashed border-gray-300 rounded-lg">
              <Upload className="text-gray-400 mb-4" size={48} />
              <div className="text-gray-500 mb-4">Click or drag image to upload</div>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
                id="fileInput"
              />
              <label
                htmlFor="fileInput"
                className="bg-blue-600 text-white px-6 py-2 rounded-md cursor-pointer hover:bg-blue-700 transition"
              >
                Choose File
              </label>
            </div>
          ) : (
            <div className="w-full flex flex-col items-center">
              <img
                src={URL.createObjectURL(selectedImage)}
                alt="Selected Food"
                className="max-h-96 rounded-lg mb-4"
              />
              {!analysisResult && (
                <div className="flex space-x-4">
                  <button
                    onClick={handleUpload}
                    disabled={loading}
                    className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition flex items-center space-x-2"
                  >
                    {loading ? <Loader2 className="animate-spin" size={20} /> : <Upload size={20} />}
                    <span>{loading ? 'Analyzing...' : 'Analyze Image'}</span>
                  </button>
                  <button
                    onClick={handleReset}
                    className="bg-red-500 text-white px-6 py-2 rounded-md hover:bg-red-600 transition flex items-center space-x-2"
                  >
                    <Trash size={20} />
                    <span>Clear</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {analysisResult && (
          <div className="bg-white p-8 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-4">{analysisResult.food_name}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-bold text-gray-700 mb-2">Detected Ingredients:</h3>
                <div className="space-y-2">
                  {analysisResult.ingredients.map((ing, index) => (
                    <div key={index} className="flex justify-between border-b pb-1">
                      <span>{ing.name}</span>
                      <span className="text-sm text-gray-500">{Math.round(ing.confidence * 100)}% confidence</span>
                    </div>
                  ))}
                </div>
                <div className="mt-6">
                  <h3 className="font-bold text-gray-700 mb-2">Cooking Method:</h3>
                  <div className="bg-blue-50 text-blue-700 px-4 py-2 rounded-md inline-block">
                    {analysisResult.cooking_method}
                  </div>
                </div>
              </div>
              <div>
                <h3 className="font-bold text-gray-700 mb-2">Nutrition Facts (per serving):</h3>
                <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                  <div className="flex justify-between font-bold text-lg">
                    <span>Calories:</span>
                    <span>{analysisResult.nutrition.calories} kcal</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Protein:</span>
                    <span>{analysisResult.nutrition.protein}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Carbs:</span>
                    <span>{analysisResult.nutrition.carbs}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Fats:</span>
                    <span>{analysisResult.nutrition.fats}g</span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>Fiber:</span>
                    <span>{analysisResult.nutrition.fiber}g</span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>Sugar:</span>
                    <span>{analysisResult.nutrition.sugar}g</span>
                  </div>
                </div>
                <div className="mt-6">
                  <h3 className="font-bold text-gray-700 mb-2">Health Score:</h3>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className={`h-4 rounded-full ${analysisResult.health_score > 7 ? 'bg-green-500' : 'bg-yellow-500'}`}
                      style={{ width: `${analysisResult.health_score * 10}%` }}
                    ></div>
                  </div>
                  <div className="text-right font-bold text-gray-700 mt-1">{analysisResult.health_score}/10</div>
                </div>
              </div>
            </div>
            <div className="mt-8">
              <h3 className="font-bold text-gray-700 mb-2">Diet Recommendations:</h3>
              <ul className="list-disc pl-5 space-y-1">
                {analysisResult.diet_suggestions.map((suggestion, index) => (
                  <li key={index} className="text-gray-600">{suggestion}</li>
                ))}
              </ul>
            </div>
            <div className="mt-8 flex justify-center">
              <button
                onClick={handleReset}
                className="bg-gray-800 text-white px-6 py-2 rounded-md hover:bg-gray-900 transition"
              >
                Analyze Another Image
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadFood;
