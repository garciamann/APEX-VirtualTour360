import React from "react";
import "aframe";

const VirtualTour = ({ imageUrl }) => (
  <div style={{ width: "100%", height: "600px" }}>
    <a-scene>
      <a-sky src={imageUrl} rotation="0 -90 0"></a-sky>
      <a-camera></a-camera>
    </a-scene>
  </div>
);

export default VirtualTour;
