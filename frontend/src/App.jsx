import { useState } from "react"

const API = "http://localhost:8000"

const AGE_RANGES = ["0-5", "6-10", "11-17", "18-25", "26-40", "41-60", "61+"]

export default function App() {
  const [text, setText] = useState("")
  const [gender, setGender] = useState("female")
  const [ageRange, setAgeRange] = useState("26-40")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [chunks, setChunks] = useState([])

  async function handleGenerate() {
    if (!text.trim()) return
    setLoading(true)
    setError("")
    setChunks([])

    try {
      const res = await fetch(`${API}/synthesize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, gender, age_range: ageRange }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || "Server error")
      }

      const data = await res.json()
      setChunks(data.chunks)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Emotion-Aware TTS</h1>

      {/* Text input */}
      <div>
        <label className="block text-sm font-medium mb-1">Paste your text</label>
        <textarea
          rows={6}
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Paste a paragraph from a novel or any narrative text..."
          className="w-full border border-gray-300 rounded p-3 text-sm resize-none focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Gender */}
      <div>
        <label className="block text-sm font-medium mb-1">Gender</label>
        <div className="flex gap-3">
          {["female", "male"].map(g => (
            <button
              key={g}
              onClick={() => setGender(g)}
              className={`px-4 py-2 rounded border text-sm capitalize ${
                gender === g
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white border-gray-300"
              }`}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      {/* Age range */}
      <div>
        <label className="block text-sm font-medium mb-1">Age Range</label>
        <div className="flex flex-wrap gap-2">
          {AGE_RANGES.map(range => (
            <button
              key={range}
              onClick={() => setAgeRange(range)}
              className={`px-3 py-1.5 rounded border text-sm ${
                ageRange === range
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white border-gray-300"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Generate button */}
      <button
        onClick={handleGenerate}
        disabled={loading || !text.trim()}
        className="w-full py-3 bg-blue-600 text-white rounded font-medium disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? "Generating... (this takes a while on CPU)" : "Generate Voice"}
      </button>

      {/* Error */}
      {error && (
        <div className="p-3 bg-red-100 border border-red-300 rounded text-sm text-red-700">
          Error: {error}
        </div>
      )}

      {/* Results */}
      {chunks.length > 0 && (
        <div className="space-y-6">
          <h2 className="text-lg font-semibold">Results</h2>
          {chunks.map((chunk, i) => (
            <div key={i} className="border border-gray-200 rounded p-4 space-y-3 bg-white">

              {/* Sentence text */}
              <p className="text-sm text-gray-700">{chunk.text}</p>

              {/* Emotion info */}
              <div className="text-xs text-gray-500 space-y-1">
                <div>
                  Primary emotion:{" "}
                  <span className="font-medium text-gray-800">{chunk.emotion_label}</span>{" "}
                  ({Math.round(chunk.emotion_score * 100)}%)
                </div>
                {chunk.second_emotion_label && (
                  <div>
                    Secondary emotion:{" "}
                    <span className="font-medium text-gray-800">{chunk.second_emotion_label}</span>{" "}
                    ({Math.round(chunk.second_emotion_score * 100)}%)
                  </div>
                )}
                <div>
                  VAD — V: {chunk.vad.v} | A: {chunk.vad.a} | D: {chunk.vad.d}
                </div>
                <div className="italic text-gray-400">"{chunk.voice_description}"</div>
              </div>

              {/* Audio player */}
              <audio
                controls
                src={`data:audio/wav;base64,${chunk.audio_b64}`}
                className="w-full"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}