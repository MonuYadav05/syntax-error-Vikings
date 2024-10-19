import React, { useState, useEffect } from 'react';

const FaceDetection = () => {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [status, setStatus] = useState('');
  const [recognizedName, setRecognizedName] = useState(''); // State for recognized name

  const toggleCamera = async () => {
    try {
      const response = await fetch('http://localhost:5000/toggle_camera', {
        method: 'POST',
      });
      const data = await response.json();
      setIsCameraActive(data.camera_active);
      setStatus(data.message);
    } catch (error) {
      console.error('Error toggling camera:', error);
      setStatus('Error toggling camera.');
    }
  };

  useEffect(() => {
    const startRecognition = async () => {
      if (isCameraActive) {
        try {
          const response = await fetch('http://localhost:5000/recognize', {
            method: 'POST',
          });
          const data = await response.json();
          setStatus(data.message);
          if (data.recognized_names) {
            setRecognizedName(data.recognized_names); // Set recognized name
          }
        } catch (error) {
          console.error('Fetch error:', error);
          setStatus('Error starting recognition.');
        }
      }
    };

    if (isCameraActive) {
      startRecognition(); // Start recognition when camera is active
      const interval = setInterval(startRecognition, 1000); // Check every second
      return () => clearInterval(interval); // Cleanup
    }
  }, [isCameraActive]);

  return (
    <div className="flex flex-col items-center justify-center p-5 bg-gray-100 rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-4">Face Recognition Attendance System</h1>
      <button
        onClick={toggleCamera}
        className={`px-4 py-2 text-white font-semibold rounded-lg transition duration-300 ${isCameraActive ? 'bg-red-500 hover:bg-red-700' : 'bg-blue-500 hover:bg-blue-700'}`}
      >
        {isCameraActive ? 'Stop Camera' : 'Start Camera'}
      </button>
      <p className="text-lg text-gray-700">{status}</p>
      {recognizedName && (
        <p className="text-lg text-green-700 mt-2">Attendance marked for: {recognizedName}</p>
      )}
      {isCameraActive && (
        <div className="mt-4">
          <img src="http://localhost:5000/video_feed" alt="Live Video Feed" className="rounded-lg shadow-lg" />
        </div>
      )}
    </div>
  );
};

export default FaceDetection;
