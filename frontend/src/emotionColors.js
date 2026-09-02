// Maps emotion labels to display colors
export const EMOTION_COLORS = {
  // Positive warm
  admiration:    { bg: 'rgba(251,191,36,0.15)',  border: 'rgba(251,191,36,0.4)',  text: '#fbbf24' },
  amusement:     { bg: 'rgba(251,191,36,0.12)',  border: 'rgba(251,191,36,0.35)', text: '#fcd34d' },
  approval:      { bg: 'rgba(34,197,94,0.12)',   border: 'rgba(34,197,94,0.35)',  text: '#4ade80' },
  caring:        { bg: 'rgba(236,72,153,0.12)',  border: 'rgba(236,72,153,0.35)', text: '#f472b6' },
  desire:        { bg: 'rgba(239,68,68,0.12)',   border: 'rgba(239,68,68,0.35)',  text: '#f87171' },
  excitement:    { bg: 'rgba(245,158,11,0.15)',  border: 'rgba(245,158,11,0.4)',  text: '#fbbf24' },
  gratitude:     { bg: 'rgba(34,197,94,0.12)',   border: 'rgba(34,197,94,0.35)',  text: '#86efac' },
  joy:           { bg: 'rgba(234,179,8,0.15)',   border: 'rgba(234,179,8,0.4)',   text: '#fde047' },
  love:          { bg: 'rgba(236,72,153,0.15)',  border: 'rgba(236,72,153,0.4)',  text: '#fb7185' },
  optimism:      { bg: 'rgba(16,185,129,0.12)',  border: 'rgba(16,185,129,0.35)', text: '#34d399' },
  pride:         { bg: 'rgba(139,92,246,0.15)',  border: 'rgba(139,92,246,0.4)',  text: '#a78bfa' },
  relief:        { bg: 'rgba(20,184,166,0.12)',  border: 'rgba(20,184,166,0.35)', text: '#2dd4bf' },
  // Negative cool
  anger:         { bg: 'rgba(239,68,68,0.15)',   border: 'rgba(239,68,68,0.45)',  text: '#f87171' },
  annoyance:     { bg: 'rgba(239,68,68,0.10)',   border: 'rgba(239,68,68,0.3)',   text: '#fca5a5' },
  disappointment:{ bg: 'rgba(100,116,139,0.15)', border: 'rgba(100,116,139,0.4)', text: '#94a3b8' },
  disapproval:   { bg: 'rgba(100,116,139,0.12)', border: 'rgba(100,116,139,0.35)',text: '#94a3b8' },
  disgust:       { bg: 'rgba(132,204,22,0.10)',  border: 'rgba(132,204,22,0.3)',  text: '#a3e635' },
  embarrassment: { bg: 'rgba(236,72,153,0.10)',  border: 'rgba(236,72,153,0.3)',  text: '#f9a8d4' },
  fear:          { bg: 'rgba(139,92,246,0.12)',  border: 'rgba(139,92,246,0.35)', text: '#c4b5fd' },
  grief:         { bg: 'rgba(71,85,105,0.15)',   border: 'rgba(71,85,105,0.4)',   text: '#94a3b8' },
  nervousness:   { bg: 'rgba(245,158,11,0.10)',  border: 'rgba(245,158,11,0.3)',  text: '#fcd34d' },
  remorse:       { bg: 'rgba(100,116,139,0.12)', border: 'rgba(100,116,139,0.35)',text: '#cbd5e1' },
  sadness:       { bg: 'rgba(59,130,246,0.12)',  border: 'rgba(59,130,246,0.35)', text: '#93c5fd' },
  // Neutral/cognitive
  confusion:     { bg: 'rgba(168,85,247,0.12)',  border: 'rgba(168,85,247,0.35)', text: '#d8b4fe' },
  curiosity:     { bg: 'rgba(6,182,212,0.12)',   border: 'rgba(6,182,212,0.35)',  text: '#22d3ee' },
  neutral:       { bg: 'rgba(113,113,122,0.12)', border: 'rgba(113,113,122,0.35)',text: '#a1a1aa' },
  realization:   { bg: 'rgba(6,182,212,0.10)',   border: 'rgba(6,182,212,0.3)',   text: '#67e8f9' },
  surprise:      { bg: 'rgba(245,158,11,0.12)',  border: 'rgba(245,158,11,0.35)', text: '#fde68a' },
};

export function getEmotionStyle(label) {
  return EMOTION_COLORS[label] ?? EMOTION_COLORS.neutral;
}
