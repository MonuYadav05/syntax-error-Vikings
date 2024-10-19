import { BrowserRouter, Route, Routes } from "react-router-dom";
import { useEffect } from "react"; // Import useEffect hook
import LedDetection from "./Pages/LedDetection";
import FaceDetection from "./Pages/FaceDetection";
import { neonCursor } from "https://unpkg.com/threejs-toys@0.0.8/build/threejs-toys.module.cdn.min.js";
import "./App.css";

function App() {
  useEffect(() => {
    // Initialize neonCursor when the component mounts
    neonCursor({
      el: document.getElementById("app"),
      shaderPoints: 16,
      curvePoints: 80,
      curveLerp: 0.5,
      radius1: 5,
      radius2: 30,
      velocityTreshold: 10,
      sleepRadiusX: 100,
      sleepRadiusY: 100,
      sleepTimeCoefX: 0.0025,
      sleepTimeCoefY: 0.0025,
    });
  }, []); // The empty array ensures the effect only runs once (on mount)

  return (
    <div id="app" className="w-screen h-screen overflow-hidden">
      <div id="hero" className="flex justify-center items-center h-full">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LedDetection />} />
            <Route path="/face-detection" element={<FaceDetection />} />
          </Routes>
        </BrowserRouter>
      </div>
    </div>
  );
}

export default App;
