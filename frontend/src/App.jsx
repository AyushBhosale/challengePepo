import { useState, useEffect } from "react";
import axios from "axios";

function VideoApp() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [videoUrl, setVideoUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentQuote, setCurrentQuote] = useState("");

  const quotes = [
    "Good things take time — so does this video.",
    "Imagining the scene...",
    "Rome wasn’t built in a day, but this video might be.",
    "Just like fine wine, this video needs time to age.",
    "Hold on... we’re cooking something good.",
    "Building pixel by pixel, frame by frame…",
    "I wish I was this slow.",
    "Video generation in progress… grab a snack!",
  ];

  // Change quotes while loading
  useEffect(() => {
    if (loading) {
      setCurrentQuote(quotes[Math.floor(Math.random() * quotes.length)]);
      const interval = setInterval(() => {
        setCurrentQuote(quotes[Math.floor(Math.random() * quotes.length)]);
      }, 2000);
      return () => clearInterval(interval);
    } else {
      setCurrentQuote("");
    }
  }, [loading]);

  // Upload file
  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return alert("Select a file first");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      await axios.post("https://pepo-backend-latest.onrender.com/upload_doc", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("File uploaded successfully!");
    } catch (err) {
      console.error(err);
      alert("File upload failed");
    }
  };

  // Generate video
  const handlePromptSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return alert("Enter a prompt first");

    setLoading(true);
    setVideoUrl(null);

    try {
      const res = await axios.post(
        "https://pepo-backend-latest.onrender.com/generate-video1",
        { prompt, width: 480, height: 480, n_seconds: 5 },
        { responseType: "blob" }
      );
      const url = URL.createObjectURL(res.data);
      setVideoUrl(url);
    } catch (err) {
      console.error(err);
      alert("Video generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white p-6 space-y-8">
      {/* File Upload Form */}
      <form
        onSubmit={handleFileUpload}
        className="bg-gray-800 p-6 rounded-xl shadow-lg w-full max-w-md space-y-4"
      >
        <h2 className="text-xl font-bold text-center">📂 Upload Document</h2>
        <input
          type="file"
          onChange={(e) => setSelectedFile(e.target.files[0])}
          className="w-full p-3 rounded-lg border border-gray-700 bg-gray-900 text-white"
        />
        <button
          type="submit"
          className="w-full bg-green-600 hover:bg-green-700 transition-colors duration-200 py-3 rounded-lg font-semibold"
        >
          Upload File
        </button>
      </form>

      {/* Video Generation Form */}
      <form
        onSubmit={handlePromptSubmit}
        className="bg-gray-800 p-6 rounded-xl shadow-lg w-full max-w-md space-y-4"
      >
        <h1 className="text-2xl font-bold text-center">🎥 AI Video Generator</h1>
        <input
          type="text"
          placeholder="Enter prompt..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full p-3 rounded-lg border border-gray-700 bg-gray-900 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 transition-colors duration-200 py-3 rounded-lg font-semibold disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Video"}
        </button>

        {loading && currentQuote && (
          <p className="mt-4 text-center text-gray-300 italic animate-pulse">
            {currentQuote}
          </p>
        )}
      </form>

      {/* Show generated video */}
      {videoUrl && (
        <div className="mt-8">
          <video
            width="480"
            height="480"
            controls
            className="rounded-lg shadow-lg border border-gray-700"
          >
            <source src={videoUrl} type="video/mp4" />
          </video>
        </div>
      )}
    </div>
  );
}

export default VideoApp;
