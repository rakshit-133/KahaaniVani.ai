const EMOTION_COLORS = {
  joy:           "#c8860a",
  excitement:    "#c8860a",
  admiration:    "#c8860a",
  love:          "#6b1a1a",
  gratitude:     "#6b1a1a",
  sadness:       "#3d5a7a",
  grief:         "#2c3e6b",
  remorse:       "#4a3060",
  fear:          "#4a3060",
  nervousness:   "#5a4030",
  anger:         "#8b1a1a",
  disgust:       "#4a5a30",
  neutral:       "#7a5c3a",
  curiosity:     "#2a5a5a",
  surprise:      "#7a4a20",
}

function VadBar({ label, value, fullLabel }) {
  const pct = Math.round(((value + 1) / 2) * 100)
  const isPositive = value >= 0
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-mono text-[#7a5c3a] w-20 shrink-0">{fullLabel}</span>
      <div className="flex-1 h-1 bg-[#e0cba8] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${pct}%`,
            background: isPositive
              ? "linear-gradient(90deg, #c8860a, #d4a017)"
              : "linear-gradient(90deg, #6b1a1a, #8b2a2a)",
          }}
        />
      </div>
      <span className="text-xs font-mono text-[#7a5c3a] w-10 text-right">{value}</span>
    </div>
  )
}

export default function EmotionCard({ chunk, index }) {
  const color = EMOTION_COLORS[chunk.emotion_label] || "#7a5c3a"

  return (
    <div
      className="border rounded-sm p-5 space-y-4"
      style={{
        borderColor: "#e0cba8",
        background: "linear-gradient(135deg, #f9f2e3 0%, #f2e8d5 100%)",
        boxShadow: "2px 2px 8px rgba(28,15,0,0.08)",
      }}
    >
      {/* Sentence number + text */}
      <div className="flex gap-3">
        <span
          className="font-playfair text-2xl font-black shrink-0 leading-none"
          style={{ color: "#e0cba8" }}
        >
          {String(index + 1).padStart(2, "0")}
        </span>
        <p className="font-baskerville text-sm leading-relaxed text-[#1c0f00] italic">
          "{chunk.text}"
        </p>
      </div>

      {/* Emotion badges */}
      <div className="flex items-center gap-2 flex-wrap">
        <span
          className="px-2.5 py-1 text-xs font-mono uppercase tracking-widest rounded-sm"
          style={{ background: color + "18", color, border: `1px solid ${color}40` }}
        >
          {chunk.emotion_label}
        </span>
        <span className="text-xs text-[#7a5c3a]">
          {Math.round(chunk.emotion_score * 100)}% confidence
        </span>
        {chunk.second_emotion_label && (
          <>
            <span className="text-[#c8860a] text-xs">·</span>
            <span className="text-xs text-[#7a5c3a] italic">
              with {chunk.second_emotion_label} ({Math.round(chunk.second_emotion_score * 100)}%)
            </span>
          </>
        )}
      </div>

      {/* VAD bars */}
      <div className="space-y-1.5 border-t border-[#e0cba8] pt-3">
        <VadBar label="V" fullLabel="Valence" value={chunk.vad.v} />
        <VadBar label="A" fullLabel="Arousal" value={chunk.vad.a} />
        <VadBar label="D" fullLabel="Dominance" value={chunk.vad.d} />
      </div>

      {/* Voice description */}
      {chunk.voice_description && (
        <div
          className="border-l-2 pl-3 py-1"
          style={{ borderColor: "#c8860a" }}
        >
          <p className="text-xs text-[#7a5c3a] font-baskerville italic leading-relaxed">
            {chunk.voice_description}
          </p>
        </div>
      )}
    </div>
  )
}