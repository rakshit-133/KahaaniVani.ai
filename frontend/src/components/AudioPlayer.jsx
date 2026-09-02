import { useRef, useState, useEffect } from 'react';
import { getEmotionStyle } from '../emotionColors';
import './AudioPlayer.css';

function WaveformBars({ playing }) {
  const BAR_COUNT = 28;
  return (
    <div className={`waveform ${playing ? 'waveform--playing' : 'waveform--idle'}`} aria-hidden="true">
      {Array.from({ length: BAR_COUNT }).map((_, i) => (
        <div
          key={i}
          className="waveform__bar"
          style={{ '--i': i, '--bars': BAR_COUNT }}
        />
      ))}
    </div>
  );
}

export default function AudioPlayer({ chunk, index, animate }) {
  const audioRef = useRef(null);
  const [playing, setPlaying]   = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const emotionStyle = getEmotionStyle(chunk.emotion_label);

  // Build audio src from base64
  const audioSrc = `data:audio/wav;base64,${chunk.audio_b64}`;

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onTimeUpdate = () => {
      setProgress(audio.duration ? (audio.currentTime / audio.duration) * 100 : 0);
    };
    const onLoadedMetadata = () => setDuration(audio.duration);
    const onEnded = () => { setPlaying(false); setProgress(0); };

    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('loadedmetadata', onLoadedMetadata);
    audio.addEventListener('ended', onEnded);
    return () => {
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('loadedmetadata', onLoadedMetadata);
      audio.removeEventListener('ended', onEnded);
    };
  }, []);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
      setPlaying(false);
    } else {
      audio.play();
      setPlaying(true);
    }
  };

  const handleSeek = (e) => {
    const audio = audioRef.current;
    if (!audio || !audio.duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const pct = x / rect.width;
    audio.currentTime = pct * audio.duration;
  };

  const handleDownload = () => {
    const a = document.createElement('a');
    a.href = audioSrc;
    a.download = `chunk-${index + 1}-${chunk.emotion_label}.wav`;
    a.click();
  };

  const formatTime = (s) => {
    if (!s || isNaN(s)) return '0:00';
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  return (
    <div
      className={`audio-player glass glass-hover ${animate ? 'audio-player--animate' : ''}`}
      style={{ animationDelay: `${index * 90}ms` }}
    >
      <audio ref={audioRef} src={audioSrc} preload="metadata" />

      {/* Header */}
      <div className="audio-player__header">
        <div className="audio-player__meta">
          <span className="audio-player__index mono">#{index + 1}</span>
          <span
            className="audio-player__emotion-tag"
            style={{
              background: emotionStyle.bg,
              borderColor: emotionStyle.border,
              color: emotionStyle.text,
            }}
          >
            {chunk.emotion_label}
          </span>
          {chunk.second_emotion_label && chunk.second_emotion_score > 0.05 && (
            <span
              className="audio-player__emotion-tag audio-player__emotion-tag--secondary"
              style={{
                background: getEmotionStyle(chunk.second_emotion_label).bg,
                borderColor: getEmotionStyle(chunk.second_emotion_label).border,
                color: getEmotionStyle(chunk.second_emotion_label).text,
              }}
            >
              {chunk.second_emotion_label}
            </span>
          )}
        </div>
        <button
          id={`download-chunk-${index}`}
          className="btn btn-ghost btn-icon"
          onClick={handleDownload}
          title="Download WAV"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
        </button>
      </div>

      {/* Text */}
      <p className="audio-player__text">"{chunk.text}"</p>

      {/* Voice description */}
      {chunk.voice_description && (
        <div className="audio-player__description">
          <span className="audio-player__description-label">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><path d="m8 3 4 4 4-4"/><path d="M12 7v10"/>
            </svg>
            Voice direction
          </span>
          <p className="audio-player__description-text">{chunk.voice_description}</p>
        </div>
      )}

      {/* Waveform + Controls */}
      <div className="audio-player__controls">
        {/* Play button */}
        <button
          id={`play-chunk-${index}`}
          className={`audio-player__play ${playing ? 'audio-player__play--playing' : ''}`}
          onClick={togglePlay}
          aria-label={playing ? 'Pause' : 'Play'}
        >
          {playing ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
          )}
        </button>

        {/* Waveform */}
        <WaveformBars playing={playing} />

        {/* Time */}
        <span className="audio-player__time mono">
          {formatTime(duration)}
        </span>
      </div>

      {/* Seek bar */}
      <div className="audio-player__seekbar" onClick={handleSeek} role="slider" aria-label="Seek">
        <div className="audio-player__seekbar-track">
          <div
            className="audio-player__seekbar-fill"
            style={{ width: `${progress}%`, '--color': emotionStyle.text }}
          />
          <div
            className="audio-player__seekbar-thumb"
            style={{ left: `${progress}%`, '--color': emotionStyle.text }}
          />
        </div>
      </div>
    </div>
  );
}
