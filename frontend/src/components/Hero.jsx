import './Hero.css';

export default function Hero({ onScrollToStudio }) {
  return (
    <section className="hero" id="hero">
      {/* Warm Ambient orbs */}
      <div className="hero__orb hero__orb--warm-1" aria-hidden="true" />
      <div className="hero__orb hero__orb--warm-2" aria-hidden="true" />

      <div className="hero__content">
        <h1 className="hero__main-title animate-fade-up" style={{ animationDelay: '0ms' }}>
          KahaaniVani<span className="hero__main-title-dot">.ai</span>
        </h1>

        <h2 className="hero__title animate-fade-up" style={{ animationDelay: '80ms' }}>
          <span className="hero__title-line">Where words</span>
          <span className="hero__title-gradient">carry emotion</span>
        </h2>

        <p className="hero__subtitle animate-fade-up" style={{ animationDelay: '160ms' }}>
          Transform your text into expressive, emotionally-aware speech.
          <br />Each sentence is understood, felt, and voiced — exactly as it was written to be heard.
        </p>

        <div className="hero__features animate-fade-up" style={{ animationDelay: '240ms' }}>
          {FEATURES.map(f => (
            <div key={f.label} className="hero__feature glass glass-hover">
              <span className="hero__feature-icon">{f.icon}</span>
              <span>{f.label}</span>
            </div>
          ))}
        </div>

        <button
          id="hero-start-btn"
          className="btn btn-primary hero__cta animate-fade-up"
          style={{ animationDelay: '320ms' }}
          onClick={onScrollToStudio}
        >
          Open Studio
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
        </button>
      </div>

      {/* Scroll arrow */}
      <button className="hero__scroll-cue" onClick={onScrollToStudio} aria-label="Scroll to studio">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
    </section>
  );
}

const FEATURES = [
  { icon: '🧠', label: '28-class Emotion AI' },
  { icon: '🎭', label: 'VAD Blending' },
  { icon: '🔊', label: 'Parler-TTS Neural' },
  { icon: '✨', label: 'Gemini Direction' },
];
