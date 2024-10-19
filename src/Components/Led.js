import React, { useEffect, useState } from "react";

const Led = ({ isOn, color, intensity }) => {
  // State to manage the animation
  const [isAnimating, setIsAnimating] = useState(false);

  // Effect to handle the animation class based on isOn state
  useEffect(() => {
    if (isOn) {
      setIsAnimating(true);
      const timer = setTimeout(() => {
        setIsAnimating(false);
      }, 200); // Animation duration

      return () => clearTimeout(timer);
    }
  }, [isOn]);

  // Style for the LED light based on props
  const ledStyle = {
    backgroundColor: isOn ? color : "gray",
    opacity: isOn ? intensity : 0.3, // Adjust opacity based on intensity
    boxShadow: isOn
      ? `0 0 250px ${color}, 0 0 105px ${color}, 0 0 101px ${color}`
      : "none", // Dynamic box shadow color
  };

  return (
    <div className="flex flex-col w-32 items-center">
      <div
        className={`w-20 h-20 transition duration-300 ease-in-out rounded-full relative ${
          isAnimating ? "animate-pulse" : ""
        }`} // Bulb shape with rounded bottom and pulse animation
        style={ledStyle}
      />
      <p className="mt-2 text-lg font-semibold">
        {isOn ? "LED is ON" : "LED is OFF"}
      </p>
      <p className="text-sm">Color: {color}</p>
      <p className="text-sm">Intensity: {intensity * 100}%</p>
    </div>
  );
};

export default Led;
