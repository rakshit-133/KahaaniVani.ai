import { useRef, useEffect, useState } from 'react';
import Hero from './components/Hero';
import StudioPanel from './components/StudioPanel';
import Toast from './components/Toast';
import Splash from './components/Splash';
import { useToast } from './hooks/useToast';
import { checkHealth } from './api';
import './App.css';

export default function App() {
  const studioRef = useRef(null);
  const { toasts, toast, removeToast } = useToast();
  const [backendStatus, setBackendStatus] = useState('checking'); // checking | ok | offline
  const [showSplash, setShowSplash] = useState(true);

  // Check backend health on mount
  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus('ok'))
      .catch(() => {
        setBackendStatus('offline');
        toast.error('Backend is offline. Start the FastAPI server on port 8000.', 0);
      });
      
    // Unmount splash after animation finishes (2.8s)
    const splashTimer = setTimeout(() => setShowSplash(false), 2800);
    return () => clearTimeout(splashTimer);
  }, []);

  const scrollToStudio = () => {
    studioRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // Pass removeToast to toast object so StudioPanel can dismiss loading toasts
  const toastWithRemove = { ...toast, removeToast };

  return (
    <>
      {showSplash && <Splash />}

      {/* Navbar */}
      <nav className={`navbar ${showSplash ? 'navbar--hidden' : 'animate-fade-in'}`} style={{ animationDelay: '2.4s' }}>
        <div className="navbar__inner">
          <div className="navbar__brand">
            <span className="navbar__logo">🎙️</span>
            <span className="navbar__name">KahaaniVani<span className="navbar__dot">.ai</span></span>
          </div>
          <div className="navbar__right">
            <span className={`navbar__status navbar__status--${backendStatus}`}>
              <span className="navbar__status-dot" />
              {backendStatus === 'checking' ? 'Connecting…'
                : backendStatus === 'ok'    ? 'System Online'
                : 'System Offline'}
            </span>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className={showSplash ? 'navbar--hidden' : 'animate-fade-in'} style={{ animationDelay: '2.5s' }}>
        <Hero onScrollToStudio={scrollToStudio} />

        {/* Divider */}
        <div className="section-divider">
          <div className="section-divider__line" />
          <span className="section-divider__label">Studio</span>
          <div className="section-divider__line" />
        </div>

        <div ref={studioRef}>
          <StudioPanel toast={toastWithRemove} />
        </div>
      </main>

      {/* Footer */}
      <footer className={`footer ${showSplash ? 'navbar--hidden' : 'animate-fade-in'}`} style={{ animationDelay: '2.5s' }}>
        <p>KahaaniVani.ai — Emotion-Aware Neural TTS · Built with Parler-TTS + Gemini + DistilBERT</p>
      </footer>

      {/* Toasts */}
      <Toast toasts={toasts} onRemove={removeToast} />
    </>
  );
}
