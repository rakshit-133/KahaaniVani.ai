import { useState, useRef } from "react"
import EmotionCard from "./EmotionCard"
import AudioPlayer from "./AudioPlayer"

const API = "http://localhost:8000"
const AGE_RANGES = ["0-5", "6-10", "11-17", "18-25", "26-40", "41-60", "61+"]

export default function MainUI() {
  const [text, setText] = useState("")
  const [gender, setGender] = useState("female")
  const [ageRange, setAgeRange] = useState("26-40")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [chunks, setChunks] = useState([])
  const textareaRef = useRef(null)

  async function handleGenerate() {
    if (!text.trim() || loading) return
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

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleGenerate()
    }
  }

  return (
    <div
      className="min-h-screen"
      style={{
        background: "linear-gradient(160deg, #f5edd8 0%, #ede0c4 40%, #e4d4b0 100%)",
      }}
    >
      {/* Header */}
      <header
        className="px-8 py-5 flex items-center justify-between"
        style={{ borderBottom: "1px solid #d8c9a8" }}
      >
        <div className="flex items-center gap-3">
          <div
            style={{
              background: "#1a0e00",
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span style={{ fontFamily: "'Tiro Devanagari', serif", color: "#d4a017", fontSize: "18px" }}>
              क
            </span>
          </div>
          <span
            style={{
              fontFamily: "'Playfair Display', serif",
              fontWeight: 900,
              fontSize: "20px",
              color: "#1a0e00",
              letterSpacing: "-0.02em",
            }}
          >
            Kahaani<span style={{ color: "#6b1a1a" }}>Vani</span>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontWeight: 400, fontSize: "13px", color: "#c8860a", marginLeft: "3px" }}>.AI</span>
          </span>
        </div>
        <span
          style={{
            fontFamily: "'Tiro Devanagari', serif",
            color: "#7a5c3a",
            fontSize: "13px",
            letterSpacing: "0.05em",
          }}
        >
          जहाँ शब्द बोलते हैं
        </span>
      </header>

      {/* Main content */}
      <main className="flex flex-col items-center px-6 pt-16 pb-20">

        {/* Hero */}
        <div className="text-center mb-12 max-w-2xl">
          <h1
            style={{
              fontFamily: "'Playfair Display', serif",
              fontWeight: 900,
              fontSize: "clamp(2.5rem, 5vw, 4rem)",
              color: "#1a0e00",
              lineHeight: 1.1,
              marginBottom: "16px",
            }}
          >
            Give your story a voice
          </h1>
          <p
            style={{
              fontFamily: "'Libre Baskerville', serif",
              fontStyle: "italic",
              color: "#7a5c3a",
              fontSize: "clamp(0.9rem, 1.5vw, 1.1rem)",
              lineHeight: 1.6,
            }}
          >
            Paste any passage. The system reads its emotion, shapes a voice, and speaks it back to you.
          </p>
        </div>

        {/* Controls — gender + age */}
        <div
          className="w-full max-w-2xl flex items-center gap-3 mb-4 flex-wrap"
        >
          {/* Gender selector */}
          <div className="flex items-center gap-1 bg-white bg-opacity-60 rounded-full p-1" style={{ border: "1px solid #d8c9a8" }}>
            {["female", "male"].map(g => (
              <button
                key={g}
                onClick={() => setGender(g)}
                style={{
                  padding: "6px 18px",
                  borderRadius: "9999px",
                  fontSize: "13px",
                  fontFamily: "'DM Sans', sans-serif",
                  fontWeight: gender === g ? 600 : 400,
                  background: gender === g ? "#6b1a1a" : "transparent",
                  color: gender === g ? "#f5edd8" : "#7a5c3a",
                  border: "none",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                {g === "female" ? "♀ Female" : "♂ Male"}
              </button>
            ))}
          </div>

          {/* Age range selector */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {AGE_RANGES.map(r => (
              <button
                key={r}
                onClick={() => setAgeRange(r)}
                style={{
                  padding: "6px 14px",
                  borderRadius: "9999px",
                  fontSize: "12px",
                  fontFamily: "'DM Sans', sans-serif",
                  fontWeight: ageRange === r ? 600 : 400,
                  background: ageRange === r ? "#c8860a" : "rgba(255,255,255,0.6)",
                  color: ageRange === r ? "#1a0e00" : "#7a5c3a",
                  border: `1px solid ${ageRange === r ? "#c8860a" : "#d8c9a8"}`,
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        {/* ChatGPT-style input bar */}
        <div
          className="w-full max-w-2xl"
          style={{
            background: "rgba(255,255,255,0.85)",
            borderRadius: "20px",
            border: "1px solid #d8c9a8",
            boxShadow: "0 4px 24px rgba(28,15,0,0.1), 0 1px 4px rgba(28,15,0,0.06)",
            padding: "12px 16px",
            display: "flex",
            alignItems: "flex-end",
            gap: "12px",
          }}
        >
          <textarea
            ref={textareaRef}
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Paste a passage from a novel, a letter, a poem… anything with feeling. Press Enter to generate."
            rows={3}
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              resize: "none",
              fontFamily: "'Libre Baskerville', serif",
              fontSize: "15px",
              lineHeight: 1.6,
              color: "#1a0e00",
              placeholder: "#b0a090",
            }}
          />

          {/* Send button */}
          <button
            onClick={handleGenerate}
            disabled={loading || !text.trim()}
            style={{
              width: "44px",
              height: "44px",
              borderRadius: "12px",
              background: loading || !text.trim() ? "#d8c9a8" : "#1a0e00",
              border: "none",
              cursor: loading || !text.trim() ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
              transition: "all 0.2s",
            }}
          >
            {loading ? (
              <svg className="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="#f5edd8" strokeWidth="4"/>
                <path className="opacity-75" fill="#f5edd8" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f5edd8" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="19" x2="12" y2="5"/>
                <polyline points="5 12 12 5 19 12"/>
              </svg>
            )}
          </button>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="mt-10 text-center space-y-2">
            <p
              style={{
                fontFamily: "'Tiro Devanagari', serif",
                color: "#c8860a",
                fontSize: "28px",
                animation: "pulse 2s infinite",
              }}
            >
              🎙
            </p>
            <p style={{ fontFamily: "'Libre Baskerville', serif", fontStyle: "italic", color: "#7a5c3a", fontSize: "14px" }}>
              Reading the emotion, shaping the voice…
            </p>
            <p style={{ fontFamily: "'DM Sans', sans-serif", color: "#b0a080", fontSize: "12px" }}>
              ~2 minutes per sentence on CPU · please wait
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            className="w-full max-w-2xl mt-6 px-5 py-4 rounded-2xl"
            style={{ background: "#fdf0f0", border: "1px solid #d4a0a0", color: "#6b1a1a" }}
          >
            <p style={{ fontFamily: "'Libre Baskerville', serif", fontStyle: "italic", fontSize: "14px" }}>
              {error}
            </p>
          </div>
        )}

        {/* Results */}
        {chunks.length > 0 && !loading && (
          <div className="w-full max-w-2xl mt-12 space-y-6">
            {/* Divider */}
            <div className="flex items-center gap-4">
              <div className="h-px flex-1" style={{ background: "#d8c9a8" }} />
              <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "11px", letterSpacing: "0.3em", color: "#7a5c3a", textTransform: "uppercase" }}>
                Results
              </span>
              <div className="h-px flex-1" style={{ background: "#d8c9a8" }} />
            </div>

            <AudioPlayer chunks={chunks} />

            <div className="space-y-4">
              {chunks.map((chunk, i) => (
                <EmotionCard key={i} chunk={chunk} index={i} />
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center py-8" style={{ borderTop: "1px solid #d8c9a8" }}>
        <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "12px", color: "#b0a080", letterSpacing: "0.2em" }}>
          KAHAANIVANI.AI · Emotion-Aware Voice Synthesis
        </p>
      </footer>
    </div>
  )
}