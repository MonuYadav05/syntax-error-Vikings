import React, { useEffect, useState } from "react";
import Led from "../Components/Led";
import { Link } from "react-router-dom";
import { TypeAnimation } from "react-type-animation";

function LedDetection() {
  const [ledCount, setLedCount] = useState(0);
  const [isCameraOn, setIsCameraOn] = useState(false); // State to track camera status
  const [volume, setVolume] = useState(0);

  const colors = ["green", "red", "blue", "yellow", "Fuchsia"];

  // Function to fetch gesture data from the Flask API
  const fetchGestureData = async () => {
    try {
      const response = await fetch("http://localhost:5000/gesture");
      const data = await response.json();

      setLedCount(data.fingers); // Assuming data.fingers holds the LED count
      setVolume(data.intensity);
    } catch (error) {
      console.error("Error fetching gesture data:", error);
    }
  };

  // Fetch gesture data periodically if the camera is on
  useEffect(() => {
    if (isCameraOn) {
      fetchGestureData(); // Fetch immediately when camera is turned on
      const interval = setInterval(fetchGestureData, 1000); // Fetch every second
      return () => clearInterval(interval); // Cleanup interval on component unmount
    }
  }, [isCameraOn]);

  // Function to toggle the camera
  const toggleCamera = async () => {
    try {
      const response = await fetch(`http://localhost:5000/toggle_camera`, {
        method: "POST",
      });
      const data = await response.json();
      setIsCameraOn(data.camera_active); // Update the camera state based on the response
    } catch (error) {
      console.error("Error toggling camera:", error);
    }
  };

  return (
    <div
      className={`flex flex-col items-center justify-center min-h-screen p-5 text-white`}
    >
      <div>
        <Link
          to={"/face-detection"}
          className="absolute left-20 top-12 rounded-[10px] bg-blue-500 text-white p-2"
        >
          FaceDetection
        </Link>
      </div>

      <div className="flex justify-center">
        {colors.map((color, index) => (
          <Led
            key={color}
            isOn={ledCount > index} // Turn on LED if ledCount > index
            intensity={volume / 100}
            color={color}
          />
        ))}
      </div>
      <br />
      <br />
      <br />
      <br />
      <h1 className="text-3xl font-bold mb-4">Hand Gesture Recognition</h1>
      {isCameraOn && (
        <div className="mb-4 flex justify-center items-center">
          <img
            src="http://localhost:5000/video_feed"
            alt="Live Video Feed"
            className="rounded-lg shadow-lg border-4 w-[50%] border-blue-500"
          />
        </div>
      )}

      <h2 className="text-2xl font-semibold mb-4">
        Number of LEDs to Light Up:{" "}
        <span className="text-blue-600">{ledCount}</span>
      </h2>
      <button
        onClick={toggleCamera}
        className={`px-4 py-2 text-black font-semibold rounded-lg shadow-md transition duration-300 
        ${
          isCameraOn
            ? "bg-red-500 hover:bg-red-600"
            : "bg-green-500 hover:bg-green-600"
        }`}
      >
        {isCameraOn ? "Turn Off Camera" : "Turn On Camera"}
      </button>

      <div className="absolute left-10 bottom-30">
        <TypeAnimation
          sequence={[
            `Monu Yadav\n Milin Sharma\n Hari Om Sharma\n Raj Rabidas`, // All names displayed
            1000, // Wait 1 second after all names are shown
            "", // Start deleting the text
            1000, // Wait before starting to erase
          ]}
          speed={50} // Adjust typing speed
          deletionSpeed={40} // Adjust deletion speed
          wrapper="span" // Element to wrap the text (can be "span", "h1", "div", etc.)
          repeat={Infinity} // Set to loop the animation indefinitely
        />
      </div>
    </div>
  );
}

export default LedDetection;
