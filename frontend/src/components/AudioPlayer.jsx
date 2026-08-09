import { useRef, useState, useEffect } from "react"

function formatTime(s) {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, "0")}`
}

export default function AudioPlayer({ chunks }) {
  const audioRef = useRef(null)
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const [currentChunk, setCurrentChunk] = useState(0)
  const [url, setUrl] = useState(null)
  const boundaries = useRef([])

  useEffect(() => {
    if (!chunks.length) return

    async function build() {
      const ctx = new (window.AudioContext || window.webkitAudioContext)()
      const buffers = []

      for (const chunk of chunks) {
        const bytes = atob(chunk.audio_b64)
        const arr = new Uint8Array(bytes.length)
        for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i)
        const decoded = await ctx.decodeAudioData(arr.buffer)
        buffers.push(decoded)
      }

      const sr = buffers[0].sampleRate
      const gap = Math.floor(sr * 0.3)
      const total = buffers.reduce((s, b) => s + b.length + gap, 0)
      const combined = ctx.createBuffer(1, total, sr)
      const out = combined.getChannelData(0)
      let offset = 0
      const bounds = []

      for (let i = 0; i < buffers.length; i++) {
        const start = offset / sr
        out.set(buffers[i].getChannelData(0), offset)
        const end = (offset + buffers[i].length) / sr
        bounds.push({ start, end, index: i })
        offset += buffers[i].length + gap
      }

      boundaries.current = bounds

      const wav = encodeWav(out, sr)
      const blob = new Blob([wav], { type: "audio/wav" })
      setUrl(URL.createObjectURL(blob))
    }

    build()
  }, [chunks])

  function encodeWav(samples, sr) {
    const buf = new ArrayBuffer(44 + samples.length * 2)
    const view = new DataView(buf)
    const ws = (o, s) => { for (let i = 0; i < s.length; i++) view.setUint8(o + i, s.charCodeAt(i)) }
    ws(0, "RIFF"); view.setUint32(4, 36 + samples.length * 2, true)
    ws(8, "WAVE"); ws(12, "fmt ")
    view.setUint32(16, 16, true); view.setUint16(20, 1, true)
    view.setUint16(22, 1, true); view.setUint32(24, sr, true)
    view.setUint32(28, sr * 2, true); view.setUint16(32, 2, true)
    view.setUint16(34, 16, true); ws(36, "data")
    view.setUint32(40, samples.length * 2, true)
    let o = 44
    for (let i = 0; i < samples.length; i++) {
      const s = Math.max(-1, Math.min(1, samples[i]))
      view.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7FFF, true); o += 2
    }
    return buf
  }

  function onTimeUpdate() {
    const el = audioRef.current
    if (!el) return
    setProgress(el.currentTime)
    const t = el.currentTime
    const found = boundaries.current.find(b => t >= b.start && t < b.end)
    if (found) setCurrentChunk(found.index)
  }

  function togglePlay() {
    const el = audioRef.current
    if (!el) return
    playing ? el.pause() : el.play()
    setPlaying(!playing)
  }

  function seek(e) {
    const el = audioRef.current
    if (!el || !duration) return
    const rect = e.currentTarget.getBoundingClientRect()
    el.currentTime = ((e.clientX - rect.left) / rect.width) * duration
  }

  function jumpTo(idx) {
    const el = audioRef.current
    const b = boundaries.current[idx]
    if (!el || !b) return
    el.currentTime = b.start
    setCurrentChunk(idx)
    el.play()
    setPlaying(true)
  }

  if (!url) return null

  const pct = duration > 0 ? (progress / duration) * 100 : 0

  return (
    <div
      className="rounded-sm border p-5 space-y-4"
      style={{
        borderColor: "#e0cba8",
        background: "linear-gradient(135deg, #f9f2e3 0%, #f2e8d5 100%)",
        boxShadow: "2px 2px 8px rgba(28,15,0,0.08)",
      }}
    >
      <audio
        ref={audioRef}
        src={url}
        onTimeUpdate={onTimeUpdate}
        onLoadedMetadata={() => setDuration(audioRef.current?.duration || 0)}
        onEnded={() => setPlaying(false)}
      />

      <div className="flex items-center gap-2 mb-1">
        <div className="h-px flex-1 bg-[#e0cba8]" />
        <span className="text-xs tracking-widest uppercase text-[#7a5c3a] font-mono">
          Audio Playback
        </span>
        <div className="h-px flex-1 bg-[#e0cba8]" />
      </div>

      {/* Progress bar */}
      <div
        className="h-8 rounded-sm overflow-hidden cursor-pointer relative flex items-center px-3"
        style={{ background: "#e8dcc8" }}
        onClick={seek}
      >
        <div
          className="absolute left-0 top-0 h-full transition-all"
          style={{
            width: `${pct}%`,
            background: "linear-gradient(90deg, #6b1a1a, #c8860a)",
            opacity: 0.3,
          }}
        />
        {boundaries.current.map((b, i) => (
          <div
            key={i}
            className="absolute top-0 w-px h-full opacity-30"
            style={{ left: `${(b.start / duration) * 100}%`, background: "#1c0f00" }}
          />
        ))}
        <span className="relative text-xs font-mono text-[#7a5c3a]">
          {formatTime(progress)} / {formatTime(duration)}
        </span>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        <button
          onClick={togglePlay}
          className="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:scale-105"
          style={{ background: "#6b1a1a", color: "#f2e8d5" }}
        >
          {playing ? (
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
              <rect x="1" y="1" width="4" height="10" rx="1"/>
              <rect x="7" y="1" width="4" height="10" rx="1"/>
            </svg>
          ) : (
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
              <path d="M2 1l9 5-9 5z"/>
            </svg>
          )}
        </button>
        <span className="text-xs text-[#7a5c3a] font-mono">
          Sentence {currentChunk + 1} of {chunks.length}
        </span>
      </div>

      {/* Chunk jump buttons */}
      <div className="flex flex-wrap gap-1.5">
        {chunks.map((_, i) => (
          <button
            key={i}
            onClick={() => jumpTo(i)}
            className="w-7 h-7 rounded-sm text-xs font-mono transition-all"
            style={{
              background: currentChunk === i ? "#6b1a1a" : "#e0cba8",
              color: currentChunk === i ? "#f2e8d5" : "#7a5c3a",
            }}
          >
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  )
}