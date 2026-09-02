import { getEmotionStyle } from '../emotionColors';
import './EmotionCard.css';

const VAD_LABELS = { v: 'Valence', a: 'Arousal', d: 'Dominance' };

function VADBar({ label, value }) {
  // value is -1 to 1, map to 0–100%
  const pct = ((value + 1) / 2) * 100;
  const isPositive = value >= 0;

  return (
    <div className="vad-bar">
      <div className="vad-bar__header">
        <span className="vad-bar__label">{label}</span>
        <span className="vad-bar__value" style={{ color: isPositive ? '#4ade80' : '#f87171' }}>
          {value > 0 ? '+' : ''}{value.toFixed(2)}
        </span>
      </div>
      <div className="vad-bar__track">
        <div
          className="vad-bar__fill"
          style={{ '--pct': `${pct}%`, '--color': isPositive ? '#4ade80' : '#f87171' }}
        />
        <div className="vad-bar__midline" />
      </div>
    </div>
  );
}

function EmotionBadge({ label, score, secondary }) {
  const style = getEmotionStyle(label);
  return (
    <span
      className={`emotion-badge ${secondary ? 'emotion-badge--secondary' : ''}`}
      style={{
        background: style.bg,
        borderColor: style.border,
        color: style.text,
      }}
    >
      {label}
      <span className="emotion-badge__score">{(score * 100).toFixed(0)}%</span>
    </span>
  );
}

export default function EmotionCard({ chunk, index, animate }) {
  const primaryStyle = getEmotionStyle(chunk.emotion_label);
  const delay = `${index * 80}ms`;

  return (
    <div
      className={`emotion-card glass glass-hover ${animate ? 'emotion-card--animate' : ''}`}
      style={{ animationDelay: delay }}
    >
      {/* Chunk index */}
      <div className="emotion-card__index">
        <span className="emotion-card__index-num">#{index + 1}</span>
      </div>

      {/* Text */}
      <p className="emotion-card__text">"{chunk.text}"</p>

      {/* Emotion badges */}
      <div className="emotion-card__badges">
        <EmotionBadge label={chunk.emotion_label} score={chunk.emotion_score} />
        {chunk.second_emotion_label && chunk.second_emotion_score > 0.05 && (
          <EmotionBadge label={chunk.second_emotion_label} score={chunk.second_emotion_score} secondary />
        )}
      </div>

      {/* Primary confidence bar */}
      <div className="emotion-card__confidence">
        <div className="emotion-card__confidence-track">
          <div
            className="emotion-card__confidence-fill"
            style={{
              '--w': `${chunk.emotion_score * 100}%`,
              '--color': primaryStyle.text,
              '--glow': primaryStyle.border,
            }}
          />
        </div>
        <span className="emotion-card__confidence-label">
          {(chunk.emotion_score * 100).toFixed(1)}% confidence
        </span>
      </div>

      {/* VAD */}
      {chunk.vad && (
        <div className="emotion-card__vad">
          <p className="emotion-card__vad-title">VAD Profile</p>
          <div className="emotion-card__vad-bars">
            {Object.entries(VAD_LABELS).map(([key, lbl]) => (
              <VADBar key={key} label={lbl} value={chunk.vad[key]} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
