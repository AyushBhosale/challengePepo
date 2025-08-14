import { useState, useEffect } from "react";
import axios from "axios";

function VideoForm() {
  const [prompt, setPrompt] = useState("");
  const [videoUrl, setVideoUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentQuote, setCurrentQuote] = useState("");

  const quotes = [
    "Good things take time — so does this video.",
    "Imagining the Scene..",
    "Rome wasnt Built in a Day, and but this video will.",
    "Just Like a fine wine, this video needs time to age.",
    "Hold on we are cooking",
    "We are building this Pixel by pixel, frame by frame… ",
    "I wish I was this slow.",
    "Video generation in progress… grab a snack!",
  ];

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setVideoUrl(null);

    try {
      const response = await axios.post(
        "http://localhost:8000/generate-video",
        { prompt, width: 480, height: 480, n_seconds: 5 },
        { responseType: "blob" }
      );
      const url = URL.createObjectURL(response.data);
      setVideoUrl(url);
    } catch (err) {
      console.error(err);
      alert("Failed to generate video");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white p-6">
      <form
        onSubmit={handleSubmit}
        className="bg-gray-800 p-6 rounded-xl shadow-lg w-full max-w-md space-y-4"
      >
        <h1 className="text-2xl font-bold text-center">🎥 AI Video Generator</h1>

        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter video prompt..."
          className="w-full p-3 rounded-lg border border-gray-700 bg-gray-900 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 transition-colors duration-200 py-3 rounded-lg font-semibold disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Video"}
        </button>
      </form>

      {loading && currentQuote && (
        <p className="mt-6 text-center text-gray-300 italic animate-pulse">
          {currentQuote}
        </p>
      )}

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

export default VideoForm;
