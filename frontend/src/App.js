import React, { useState } from "react";
import axios from "axios";
import VirtualTour from "./components/VirtualTour";

function App() {
  const [file, setFile] = useState(null);
  const [convertedUrl, setConvertedUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const uploadFile = async () => {
    if (!file) return alert("Please select a file first.");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(
        "https://your-backend-url.onrender.com/upload",
        formData
      );
      setConvertedUrl(res.data.url);
    } catch (err) {
      console.error(err);
      alert("Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "40px" }}>
      <h1>🌀 APEX VirtualTour360</h1>
      <input
        type="file"
        accept=".insv,.mp4,.jpg,.jpeg"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={uploadFile} disabled={loading}>
        {loading ? "Processing..." : "Upload & Convert"}
      </button>
      {convertedUrl && (
        <div>
          <h2>Preview:</h2>
          <VirtualTour imageUrl={convertedUrl} />
        </div>
      )}
    </div>
  );
}

export default App;
