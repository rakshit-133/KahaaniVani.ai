import { useEffect, useRef, useState } from "react"

// Each letter definition — char, and its cutout pool of variants
const TITLE_CHARS = "KahaaniVani.AI"

// Cutout paper styles — mix of white, grey, sepia, dark
const PAPER_STYLES = [
  { bg: "#f5f5f0", color: "#111", shadow: "rgba(0,0,0,0.5)" },
  { bg: "#e8e0d0", color: "#1a0e00", shadow: "rgba(0,0,0,0.45)" },
  { bg: "#2a2a28", color: "#f0ead8", shadow: "rgba(0,0,0,0.6)" },
  { bg: "#c8b89a", color: "#1a0e00", shadow: "rgba(0,0,0,0.4)" },
  { bg: "#111110", color: "#f0f0ec", shadow: "rgba(0,0,0,0.7)" },
  { bg: "#e0d5bc", color: "#2a1800", shadow: "rgba(0,0,0,0.35)" },
  { bg: "#f0ede4", color: "#333", shadow: "rgba(0,0,0,0.4)" },
  { bg: "#3a3530", color: "#f0e8d0", shadow: "rgba(0,0,0,0.55)" },
]

const FONTS = [
  "'Playfair Display', serif",
  "'Libre Baskerville', serif",
  "'Oswald', sans-serif",
  "'Abril Fatface', cursive",
  "'UnifrakturMaguntia', cursive",
  "'DM Sans', sans-serif",
  "Georgia, serif",
  "Impact, sans-serif",
]

const WEIGHTS = ["400", "700", "900"]

function randomFrom(arr) {
  return arr[Math.floor(Math.random() * arr.length)]
}

function randomBetween(min, max) {
  return min + Math.random() * (max - min)
}

function generateCutout() {
  const paper = randomFrom(PAPER_STYLES)
  return {
    bg: paper.bg,
    color: paper.color,
    shadow: paper.shadow,
    font: randomFrom(FONTS),
    weight: randomFrom(WEIGHTS),
    rotation: randomBetween(-12, 12),
    scale: randomBetween(0.85, 1.15),
    italic: Math.random() > 0.6,
  }
}

// Build initial cutout state for each character
function buildInitialState() {
  return TITLE_CHARS.split("").map(char => ({
    char,
    cutout: generateCutout(),
    visible: false,
    settled: false,
  }))
}

export default function Intro({ onComplete }) {
  const [letters, setLetters] = useState(buildInitialState())
  const [phase, setPhase] = useState("hidden") // hidden | slamming | cycling | settling | fading
  const [introOpacity, setIntroOpacity] = useState(1)
  const audioRef = useRef(null)

  useEffect(() => {
    // Play sound
    audioRef.current = new Audio("/intro_sound.mp3")
    audioRef.current.volume = 0.9
    audioRef.current.play().catch(() => {})

    // Phase 1 — slam letters in one by one
    setPhase("slamming")
    const chars = TITLE_CHARS.split("")
    let slammed = 0

    const slamInterval = setInterval(() => {
      if (slammed >= chars.length) {
        clearInterval(slamInterval)
        setPhase("cycling")
        startCycling()
        return
      }
      const idx = slammed
      setLetters(prev => prev.map((l, i) =>
        i === idx ? { ...l, visible: true, cutout: generateCutout() } : l
      ))
      slammed++
    }, 120)

    return () => clearInterval(slamInterval)
  }, [])

  function startCycling() {
    let cycles = 0
    const maxCycles = 20

    const cycleInterval = setInterval(() => {
      setLetters(prev => prev.map(l => ({
        ...l,
        cutout: generateCutout(),
      })))

      cycles++
      if (cycles >= maxCycles) {
        clearInterval(cycleInterval)
        settle()
      }
    }, 80)
  }

  function settle() {
    setPhase("settling")

    // Each letter settles to a final clean cutout with less rotation
    setLetters(prev => prev.map(l => ({
      ...l,
      settled: true,
      cutout: {
        ...generateCutout(),
        rotation: randomBetween(-4, 4),
        scale: randomBetween(0.95, 1.05),
      },
    })))

    // Wait, then fade out
    setTimeout(() => {
      setPhase("fading")
      let op = 1
      const fadeInterval = setInterval(() => {
        op -= 0.04
        setIntroOpacity(Math.max(0, op))
        if (op <= 0) {
          clearInterval(fadeInterval)
          onComplete()
        }
      }, 35)
    }, 2200)
  }

  return (
    <div
      className="fixed inset-0 flex flex-col items-center justify-center z-50 overflow-hidden"
      style={{
        background: `radial-gradient(ellipse at center, #0f0802 0%, ${`var(--intro-bg)`} 75%)`,
        opacity: introOpacity,
      }}
    >
      {/* Grain texture overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E")`,
          opacity: 0.4,
        }}
      />

      {/* Top label */}
      <div
        className="flex items-center gap-3 mb-12 transition-all duration-1000"
        style={{ opacity: phase === "hidden" ? 0 : 0.7 }}
      >
        <div className="h-px w-16" style={{ background: "#d4a017" }} />
        <span
          style={{
            color: "#d4a017",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "11px",
            letterSpacing: "0.4em",
            textTransform: "uppercase",
          }}
        >
          An Emotion–Aware Voice Experience
        </span>
        <div className="h-px w-16" style={{ background: "#d4a017" }} />
      </div>

      {/* Letters container */}
      <div className="flex items-center justify-center flex-wrap gap-2 px-8 max-w-5xl">
        {letters.map((letter, i) => (
          <LetterCutout
            key={i}
            letter={letter}
            phase={phase}
          />
        ))}
      </div>

      {/* Bottom tagline */}
      <div
        className="mt-12 transition-all duration-1000"
        style={{ opacity: phase === "settling" || phase === "fading" ? 1 : 0 }}
      >
        <p
          style={{
            fontFamily: "'Tiro Devanagari', serif",
            color: "#c8860a",
            fontSize: "16px",
            letterSpacing: "0.2em",
            textAlign: "center",
          }}
        >
          जहाँ शब्द बोलते हैं
        </p>
      </div>
    </div>
  )
}

function LetterCutout({ letter, phase }) {
  const { char, cutout, visible, settled } = letter

  if (!visible) return (
    <div style={{ width: char === "." ? "24px" : "72px", height: "90px" }} />
  )

  const isDot = char === "."
  const fontSize = isDot ? "32px" : char === char.toUpperCase() && char !== char.toLowerCase() ? "72px" : "64px"

  return (
    <div
      style={{
        transform: `rotate(${cutout.rotation}deg) scale(${visible ? cutout.scale : 0})`,
        transition: settled
          ? "transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)"
          : phase === "slamming"
          ? "transform 0.15s cubic-bezier(0.34, 1.56, 0.64, 1)"
          : "transform 0.05s ease",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        background: cutout.bg,
        color: cutout.color,
        padding: isDot ? "4px 6px" : "6px 12px",
        minWidth: isDot ? "28px" : "60px",
        boxShadow: `3px 3px 10px ${cutout.shadow}, -1px -1px 4px rgba(0,0,0,0.2)`,
        // Torn edge effect using clip-path
        clipPath: "polygon(1% 2%, 98% 0%, 99% 97%, 2% 99%)",
      }}
    >
      <span
        style={{
          fontFamily: cutout.font,
          fontWeight: cutout.weight,
          fontSize,
          fontStyle: cutout.italic ? "italic" : "normal",
          lineHeight: 1,
          userSelect: "none",
        }}
      >
        {char}
      </span>
    </div>
  )
}