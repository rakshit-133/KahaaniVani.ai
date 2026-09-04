import { useState, useRef } from 'react';
import EmotionCard from './EmotionCard';
import AudioPlayer from './AudioPlayer';
import { analyzeText, synthesizeTextStream } from '../api';
import './StudioPanel.css';

const GENDER_OPTIONS = [
  { value: 'female', label: 'Female' },
  { value: 'male',   label: 'Male'   },
];

const FEMALE_VOICES = [
  { value: 'Laura', label: 'Laura (Standard)' },
  { value: 'Lea', label: 'Lea (Young/Warm)' },
  { value: 'Barbara', label: 'Barbara (Mature/Firm)' },
  { value: 'Emily', label: 'Emily (Soft)' }
];

const MALE_VOICES = [
  { value: 'Jon', label: 'Jon (Standard)' },
  { value: 'Gary', label: 'Gary (Deep/Warm)' },
  { value: 'Rick', label: 'Rick (Commanding)' },
  { value: 'Ryan', label: 'Ryan (Youthful)' }
];

const SAMPLE_TEXT = `The morning light filtered through the curtains as Maya sat alone at her kitchen table. She wrapped her hands around the warm mug, letting the steam curl upward like a slow exhale.

"I can't believe you're actually leaving," she whispered, more to herself than anyone else.

Outside, a car horn blared. Somewhere down the hall, a door clicked shut. And then silence — the kind that has weight to it.`;

export default function StudioPanel({ toast }) {
  const [text, setText]           = useState('');
  const [gender, setGender]       = useState('female');
  const [voiceActor, setVoiceActor] = useState('Laura');

  const [analyzeState, setAnalyzeState] = useState('idle'); // idle | loading | done | error
  const [synthState, setSynthState]     = useState('idle');

  const [emotionChunks, setEmotionChunks]   = useState([]);
  const [audioChunks, setAudioChunks]       = useState([]);
  const [combinedAudio, setCombinedAudio]   = useState('');
  const [showAudio, setShowAudio]           = useState(false);

  const resultsRef = useRef(null);
  const audioRef   = useRef(null);

  const charCount = text.length;
  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;

  // ── Analyze ────────────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast.error('Please enter some text first.');
      return;
    }
    if (text.length > 500) {
      toast.error('Character limit exceeded (500 max).');
      return;
    }
    setAnalyzeState('loading');
    setEmotionChunks([]);
    setAudioChunks([]);
    setCombinedAudio('');
    setShowAudio(false);

    const toastId = toast.loading('Analyzing emotions…');
    try {
      const data = await analyzeText(text.trim());
      setEmotionChunks(data.chunks);
      setAnalyzeState('done');
      toast.removeToast?.(toastId);
      toast.success(`Found ${data.chunks.length} chunk${data.chunks.length !== 1 ? 's' : ''} 🎭`);
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setAnalyzeState('error');
      toast.removeToast?.(toastId);
      toast.error(`Analysis failed: ${err.message}`);
    }
  };

  // ── Synthesize ─────────────────────────────────────────────────────────
  const handleSynthesize = async () => {
    if (!text.trim()) {
      toast.error('Please enter some text first.');
      return;
    }
    if (text.length > 500) {
      toast.error('Character limit exceeded (500 max).');
      return;
    }
    setSynthState('loading');
    setAudioChunks([]);
    
    // Preserve existing analysis but clear out previous audio so we can update in place
    if (emotionChunks.length > 0) {
      setEmotionChunks(prev => prev.map(c => ({ ...c, audio_b64: undefined, voice_description: undefined })));
    } else {
      setEmotionChunks([]);
    }
    
    setCombinedAudio('');
    setShowAudio(true); // show section immediately

    const toastId = toast.loading('Generating speech — this may take a minute…');
    try {
      await synthesizeTextStream(
        text.trim(), 
        gender, 
        voiceActor,
        (chunk) => {
          // append new chunk audio
          setAudioChunks(prev => [...prev, chunk]);
          
          setEmotionChunks(prev => {
            // Find the first chunk with matching text that hasn't received audio yet
            const idx = prev.findIndex(c => c.text === chunk.text && !c.audio_b64);
            if (idx !== -1) {
              const next = [...prev];
              next[idx] = chunk;
              return next;
            }
            // If not found (e.g. didn't analyze first), append it
            return [...prev, chunk];
          });
          
          // ensure analyze phase UI switches over
          setAnalyzeState('done');
        },
        (combined) => {
          setCombinedAudio(combined || '');
          setSynthState('done');
          toast.removeToast?.(toastId);
          toast.success('Finished generating! 🔊');
        }
      );
      
      setTimeout(() => {
        audioRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setSynthState('error');
      toast.removeToast?.(toastId);
      toast.error(`Synthesis failed: ${err.message}`);
    }
  };

  // ── Play All ───────────────────────────────────────────────────────────
  const playAllRef   = useRef(null);
  const playingAllRef= useRef(false);
  const [playingAll, setPlayingAll] = useState(false);

  const handlePlayAll = () => {
    if (playingAll) {
      playingAllRef.current = false;
      setPlayingAll(false);
      return;
    }

    const audios = document.querySelectorAll('.audio-player audio');
    if (!audios.length) return;

    playingAllRef.current = true;
    setPlayingAll(true);

    let idx = 0;
    const playNext = () => {
      if (!playingAllRef.current || idx >= audios.length) {
        setPlayingAll(false);
        playingAllRef.current = false;
        return;
      }
      const audio = audios[idx];
      // trigger play button click to sync waveform state
      const btn = audio.closest('.audio-player')?.querySelector('[id^="play-chunk"]');
      if (btn) btn.click();
      audio.onended = () => { idx++; playNext(); };
    };
    playNext();
  };

  return (
    <section className="studio" id="studio">
      <div className="studio__header">
        <div className="studio__header-text">
          <h2 className="studio__title">
            <span className="gradient-text">Emotion Studio</span>
          </h2>
          <p className="studio__subtitle">
            Enter your story below. The AI will parse each sentence, detect its emotion, and synthesize a uniquely voiced performance.
          </p>
        </div>
      </div>

      <div className="studio__layout">
        {/* ── Left: Input Panel ─────────────────────────────────────── */}
        <div className="studio__input-panel">
          <div className="input-panel glass">
            {/* Text area */}
            <div className="input-panel__field">
              <label className="form-label" htmlFor="story-input">Your Story</label>
              <textarea
                id="story-input"
                className="form-textarea input-panel__textarea"
                value={text}
                onChange={e => setText(e.target.value)}
                placeholder="Write your story, narration, or dialogue here (up to 500 chars)..."
                rows={10}
                maxLength={500}
              />
              <div className="input-panel__meta">
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setText(SAMPLE_TEXT)}
                  id="load-sample-btn"
                >
                  Load sample
                </button>
                <span className={`input-panel__counter mono ${charCount > 500 ? 'text-error' : ''}`}>
                  {wordCount} words · {charCount}/500 chars
                </span>
              </div>
            </div>

            <hr className="divider" />

            {/* Voice Config */}
            <div className="input-panel__voice-config">
              <p className="voice-config__heading">Voice Configuration</p>

              <div className="voice-config__grid">
                {/* Gender dropdown */}
                <div className="voice-config__field">
                  <label className="form-label" htmlFor="gender-select">Speaker Gender</label>
                  <div className="select-wrapper">
                    <select
                      id="gender-select"
                      className="form-select"
                      value={gender}
                      onChange={e => {
                        const newGender = e.target.value;
                        setGender(newGender);
                        setVoiceActor(newGender === 'female' ? 'Laura' : 'Jon');
                      }}
                    >
                      {GENDER_OPTIONS.map(o => (
                        <option key={o.value} value={o.value}>{o.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Voice Actor dropdown */}
                <div className="voice-config__field">
                  <label className="form-label" htmlFor="voice-select">Voice Actor</label>
                  <div className="select-wrapper">
                    <select
                      id="voice-select"
                      className="form-select"
                      value={voiceActor}
                      onChange={e => setVoiceActor(e.target.value)}
                    >
                      {(gender === 'female' ? FEMALE_VOICES : MALE_VOICES).map(o => (
                        <option key={o.value} value={o.value}>{o.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <hr className="divider" />

            {/* Action Buttons */}
            <div className="input-panel__actions">
              <button
                id="analyze-btn"
                className={`btn btn-secondary input-panel__btn ${analyzeState === 'loading' ? 'btn--loading' : ''}`}
                onClick={handleAnalyze}
                disabled={analyzeState === 'loading' || synthState === 'loading'}
              >
                {analyzeState === 'loading' ? (
                  <>
                    <svg className="btn-spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                      <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                    </svg>
                    Analyzing…
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                    Analyze Emotions
                  </>
                )}
              </button>

              <button
                id="synthesize-btn"
                className={`btn btn-primary input-panel__btn ${synthState === 'loading' ? 'btn--loading' : ''}`}
                onClick={handleSynthesize}
                disabled={analyzeState === 'loading' || synthState === 'loading'}
              >
                {synthState === 'loading' ? (
                  <>
                    <svg className="btn-spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                      <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                    </svg>
                    Generating…
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                      <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
                      <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                    </svg>
                    Generate Speech
                  </>
                )}
              </button>
            </div>

            {/* Pipeline status strip */}
            <PipelineStatus analyzeState={analyzeState} synthState={synthState} />
          </div>
        </div>

        {/* ── Right: Emotion Results ─────────────────────────────────── */}
        <div className="studio__results-panel" ref={resultsRef}>
          {emotionChunks.length === 0 && analyzeState !== 'loading' && (
            <div className="results-empty glass">
              <div className="results-empty__icon">🎭</div>
              <p className="results-empty__title">Emotion analysis will appear here</p>
              <p className="results-empty__sub">Click "Analyze Emotions" to see how your text is read</p>
            </div>
          )}

          {analyzeState === 'loading' && emotionChunks.length === 0 && (
            <div className="results-loading">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="skeleton glass" style={{ animationDelay: `${i * 0.1}s` }} />
              ))}
            </div>
          )}

          {emotionChunks.length > 0 && (
            <div className="results-grid">
              <div className="results-grid__header">
                <h3 className="results-grid__title">
                  Emotion Analysis
                  <span className="results-grid__count">{emotionChunks.length}</span>
                </h3>
              </div>
              <div className="results-grid__cards">
                {emotionChunks.map((chunk, i) => (
                  <EmotionCard key={i} chunk={chunk} index={i} animate />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Audio Results Section ─────────────────────────────────────── */}
      {showAudio && audioChunks.length > 0 && (
        <div className="audio-section animate-fade-up" ref={audioRef}>
          <div className="audio-section__header">
            <div>
              <h3 className="audio-section__title">
                <span className="gradient-text">Generated Audio</span>
              </h3>
              <p className="audio-section__sub">
                {audioChunks.length} expressive segment{audioChunks.length !== 1 ? 's' : ''} — each voiced to match its emotion
              </p>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                id="play-all-btn"
                className={`btn ${playingAll ? 'btn-accent' : 'btn-primary'}`}
                onClick={handlePlayAll}
              >
              {playingAll ? (
                <>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>
                  </svg>
                  Stop
                </>
              ) : (
                <>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  Play All
                </>
              )}
            </button>
            {combinedAudio && (
              <a
                href={`data:audio/wav;base64,${combinedAudio}`}
                download="KahaaniVani_Full_Story.wav"
                className="btn btn-secondary"
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '6px'}}>
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Download Full Audio
              </a>
            )}
            </div>
          </div>

          <div className="audio-grid">
            {audioChunks.map((chunk, i) => (
              <AudioPlayer key={i} chunk={chunk} index={i} animate />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

// ── Pipeline Status ───────────────────────────────────────────────────────
function PipelineStep({ label, state }) {
  const icon = state === 'done'    ? '✓'
             : state === 'loading' ? '◌'
             : state === 'error'   ? '✗'
             : '·';

  return (
    <div className={`pipeline-step pipeline-step--${state}`}>
      <span className="pipeline-step__icon">{icon}</span>
      <span className="pipeline-step__label">{label}</span>
    </div>
  );
}

function PipelineStatus({ analyzeState, synthState }) {
  const steps = [
    { label: 'Chunking',    state: analyzeState === 'idle' ? 'idle' : analyzeState === 'loading' ? 'loading' : 'done' },
    { label: 'Emotion AI',  state: analyzeState === 'idle' ? 'idle' : analyzeState === 'loading' ? 'loading' : 'done' },
    { label: 'VAD Blend',   state: analyzeState === 'idle' ? 'idle' : analyzeState !== 'done'    ? 'idle'    : 'done' },
    { label: 'Voice Direction', state: synthState === 'loading' ? 'loading' : synthState === 'done' ? 'done' : 'idle' },
    { label: 'Parler TTS',  state: synthState === 'loading' ? 'loading' : synthState === 'done' ? 'done' : 'idle' },
  ];

  return (
    <div className="pipeline-status">
      {steps.map((s, i) => (
        <div key={i} className="pipeline-status__step-wrap">
          <PipelineStep label={s.label} state={s.state} />
          {i < steps.length - 1 && <div className="pipeline-status__arrow">›</div>}
        </div>
      ))}
    </div>
  );
}
