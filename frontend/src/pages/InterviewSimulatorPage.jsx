import React, { useState, useEffect } from 'react';
import { interviewApi } from '../services/api';
import { Bot, Mic, MicOff, Send, CheckCircle2, AlertCircle, ArrowRight, Award, Sparkles, Volume2, VolumeX, Square, LogOut, BookOpen, ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';

export default function InterviewSimulatorPage({ initialData, onComplete }) {
  const [session, setSession] = useState(initialData?.session || null);
  const [currentQuestion, setCurrentQuestion] = useState(initialData?.current_question || null);
  const [candidateAnswer, setCandidateAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showDeepDive, setShowDeepDive] = useState(false);
  const [lastEvaluation, setLastEvaluation] = useState(null);
  const [showEvaluationModal, setShowEvaluationModal] = useState(false);
  const [error, setError] = useState('');

  // Speech Recognition setup if browser supports it
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = 'en-US';

      rec.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setCandidateAnswer((prev) => (prev ? prev + ' ' + transcript : transcript));
      };

      rec.onerror = (err) => {
        console.error("Speech recognition error:", err);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      setRecognition(rec);
    }
  }, []);

  const toggleSpeechToText = () => {
    if (!recognition) {
      alert("Speech recognition is not natively supported in this browser version. You can type your response!");
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  const handleTextToSpeech = (text) => {
    if ('speechSynthesis' in window) {
      if (isSpeaking || window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      } else {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);
        window.speechSynthesis.speak(utterance);
        setIsSpeaking(true);
      }
    }
  };

  const handleEndEarly = async () => {
    if (window.confirm("End this interview early? We will evaluate your answered questions and generate your scorecard now.")) {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      setLoading(true);
      try {
        await interviewApi.endSession(session.id);
        if (onComplete) {
          onComplete(session.id);
        }
      } catch (err) {
        console.error("Error ending session:", err);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSubmitAnswer = async () => {
    if (!candidateAnswer.trim()) {
      setError("Please provide an answer before submitting.");
      return;
    }

    if (isListening && recognition) {
      recognition.stop();
      setIsListening(false);
    }

    setLoading(true);
    setError('');

    try {
      const res = await interviewApi.submitAnswer({
        sessionId: session.id,
        questionId: currentQuestion.id,
        answerText: candidateAnswer
      });

      const { evaluation, next_question, is_complete, final_report } = res.data;

      setLastEvaluation(evaluation);
      setShowEvaluationModal(true);

      if (is_complete) {
        setTimeout(() => {
          if (onComplete) onComplete(session.id);
        }, 3000);
      } else if (next_question) {
        setCurrentQuestion(next_question);
        setCandidateAnswer('');
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Error evaluating response');
    } finally {
      setLoading(false);
    }
  };

  if (!session || !currentQuestion) {
    return (
      <div style={{ textAlign: 'center', padding: '60px' }}>
        <p>No active interview session found.</p>
      </div>
    );
  }

  const qNum = currentQuestion.questionNumber || session.currentQuestionNumber;
  const maxQ = session.maxQuestions;

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>
      {/* Top Header & Session Progress */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="badge-pill badge-indigo">{session.role}</span>
            <span className="badge-pill badge-purple">{session.experienceLevel}</span>
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Technical Interview Simulation Room</h2>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Question Progress</span>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--primary)' }}>
              {qNum} of {maxQ}
            </div>
          </div>
          <button
            onClick={handleEndEarly}
            className="btn-secondary"
            style={{ padding: '10px 16px', fontSize: '0.85rem', color: 'var(--rose)', borderColor: 'rgba(244, 63, 94, 0.3)' }}
            title="End test early and generate scorecard for answered questions"
          >
            <Square size={16} /> End & Get Report
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{
        width: '100%',
        height: '6px',
        background: 'rgba(255, 255, 255, 0.08)',
        borderRadius: '3px',
        marginBottom: '32px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${(qNum / maxQ) * 100}%`,
          height: '100%',
          background: 'linear-gradient(90deg, var(--primary), var(--purple))',
          transition: 'width 0.4s ease'
        }} />
      </div>

      {/* Main Split Interface */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Left Column: AI Interviewer & Question Display */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
              <div className="audio-pulse" style={{
                width: '52px',
                height: '52px',
                borderRadius: '16px',
                background: 'linear-gradient(135deg, var(--primary), var(--purple))',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 20px var(--primary-glow)'
              }}>
                <Bot size={30} color="white" />
              </div>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Senior AI Interviewer</h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  Interactive AI System
                </span>
              </div>
              <button
                onClick={() => handleTextToSpeech(currentQuestion.questionText)}
                className={isSpeaking ? "btn-primary" : "btn-secondary"}
                style={{
                  marginLeft: 'auto',
                  padding: '8px 14px',
                  fontSize: '0.8rem',
                  background: isSpeaking ? 'rgba(139, 92, 246, 0.2)' : undefined,
                  borderColor: isSpeaking ? 'var(--purple)' : undefined
                }}
                title={isSpeaking ? "Mute audio" : "Read question out loud"}
              >
                {isSpeaking ? <VolumeX size={16} /> : <Volume2 size={16} />}
                {isSpeaking ? 'Mute' : 'Read'}
              </button>
            </div>

            <div style={{
              background: 'rgba(10, 15, 26, 0.6)',
              border: '1px solid var(--border-glass)',
              borderRadius: '14px',
              padding: '20px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span className="badge-pill badge-emerald">{currentQuestion.topic}</span>
                {currentQuestion.isFollowup && (
                  <span className="badge-pill badge-purple">Adaptive Probe</span>
                )}
              </div>

              <p style={{ fontSize: '1.1rem', fontWeight: 600, lineHeight: 1.6, color: '#f8fafc', marginBottom: '14px' }}>
                "{currentQuestion.questionText}"
              </p>

              {currentQuestion.focusArea && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '10px' }}>
                  Target Assessment: <strong style={{ color: 'var(--text-muted)' }}>{currentQuestion.focusArea}</strong>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Candidate Response & Voice Input */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Your Technical Answer</h3>

              {/* Dictation Toggle */}
              <button
                type="button"
                onClick={toggleSpeechToText}
                className={isListening ? 'btn-primary' : 'btn-secondary'}
                style={{
                  padding: '6px 14px',
                  fontSize: '0.8rem',
                  background: isListening ? 'rgba(244, 63, 94, 0.2)' : undefined,
                  borderColor: isListening ? 'var(--rose)' : undefined,
                  color: isListening ? 'var(--rose)' : undefined
                }}
              >
                {isListening ? <MicOff size={14} /> : <Mic size={14} />}
                {isListening ? 'Recording...' : 'Speech-to-Text'}
              </button>
            </div>

            {error && (
              <div style={{
                background: 'rgba(244, 63, 94, 0.15)',
                color: '#fda4af',
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                marginBottom: '12px'
              }}>
                {error}
              </div>
            )}

            <textarea
              className="input-glass"
              rows={9}
              placeholder="Structure your answer clearly. Mention technical concepts, design decisions, code patterns, or production trade-offs..."
              value={candidateAnswer}
              onChange={(e) => setCandidateAnswer(e.target.value)}
              style={{
                resize: 'vertical',
                flexGrow: 1,
                fontSize: '0.95rem',
                lineHeight: 1.5,
                fontFamily: 'inherit'
              }}
            />

            <button
              onClick={handleSubmitAnswer}
              className="btn-primary"
              disabled={loading}
              style={{ marginTop: '16px', justifyContent: 'center', padding: '14px' }}
            >
              {loading ? 'Evaluating with LangGraph Agent...' : 'Submit Answer for Evaluation'} <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Real-time Evaluation Modal / Feedback */}
      {showEvaluationModal && lastEvaluation && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(5, 8, 15, 0.88)',
          backdropFilter: 'blur(14px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 200,
          padding: '24px',
          overflowY: 'auto'
        }}>
          <div className="glass-panel glass-panel-glow" style={{
            maxWidth: '750px',
            width: '100%',
            padding: '32px',
            maxHeight: '90vh',
            overflowY: 'auto',
            border: '1px solid rgba(99, 102, 241, 0.3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Award size={28} color="#34d399" />
                <h3 style={{ fontSize: '1.35rem', fontWeight: 800 }}>Real-Time AI Evaluation</h3>
              </div>
              <span className="badge-pill badge-emerald" style={{ fontSize: '1rem', padding: '6px 16px', fontWeight: 800 }}>
                SCORE: {lastEvaluation.overall_question_score || lastEvaluation.technical_score || 0}/10
              </span>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <p style={{ fontSize: '0.95rem', color: 'var(--text-main)', marginBottom: '16px', lineHeight: 1.6, background: 'rgba(255,255,255,0.03)', padding: '14px', borderRadius: '10px', borderLeft: '4px solid var(--primary)' }}>
                {lastEvaluation.feedback_summary}
              </p>

              {/* Ideal / Reference Solution */}
              {lastEvaluation.ideal_answer && (
                <div style={{
                  marginBottom: '20px',
                  background: 'rgba(52, 211, 153, 0.06)',
                  border: '1px solid rgba(52, 211, 153, 0.25)',
                  borderRadius: '12px',
                  padding: '18px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                    <Sparkles size={20} color="#34d399" />
                    <span style={{ fontSize: '0.95rem', fontWeight: 800, color: '#34d399' }}>
                      Ideal Technical Reference Answer (10/10 Standard)
                    </span>
                  </div>
                  <p style={{ fontSize: '0.92rem', color: 'var(--text-main)', lineHeight: 1.6, whiteSpace: 'pre-wrap', margin: 0 }}>
                    {lastEvaluation.ideal_answer}
                  </p>
                </div>
              )}

              {/* Strengths & Improvements */}
              <div style={{ display: 'grid', gridTemplateColumns: lastEvaluation.strengths?.length && lastEvaluation.improvements?.length ? '1fr 1fr' : '1fr', gap: '16px', marginBottom: '20px' }}>
                {lastEvaluation.strengths && lastEvaluation.strengths.length > 0 && (
                  <div style={{ background: 'rgba(255,255,255,0.02)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#34d399', display: 'block', marginBottom: '8px' }}>
                      ✓ Key Strengths:
                    </span>
                    <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: 'var(--text-main)', margin: 0 }}>
                      {lastEvaluation.strengths.map((str, idx) => (
                        <li key={idx} style={{ marginBottom: '4px' }}>{str}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {lastEvaluation.improvements && lastEvaluation.improvements.length > 0 && (
                  <div style={{ background: 'rgba(255,255,255,0.02)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#818cf8', display: 'block', marginBottom: '8px' }}>
                      💡 Areas to Deepen:
                    </span>
                    <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                      {lastEvaluation.improvements.map((imp, idx) => (
                        <li key={idx} style={{ marginBottom: '4px' }}>{imp}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Deep Dive / In-Depth Explanation Expandable Option */}
              {lastEvaluation.in_depth_explanation && (
                <div style={{ marginBottom: '20px' }}>
                  <button
                    onClick={() => setShowDeepDive(!showDeepDive)}
                    className="btn-secondary"
                    style={{
                      width: '100%',
                      justify: 'space-between',
                      padding: '12px 18px',
                      background: 'rgba(99, 102, 241, 0.1)',
                      borderColor: 'rgba(99, 102, 241, 0.3)',
                      color: '#a5b4fc'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700 }}>
                      <BookOpen size={18} color="#818cf8" /> Explain In-Depth (Deep Dive)
                    </div>
                    {showDeepDive ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </button>

                  {showDeepDive && (
                    <div style={{
                      marginTop: '12px',
                      padding: '20px',
                      background: 'rgba(15, 23, 42, 0.8)',
                      border: '1px solid rgba(129, 140, 248, 0.3)',
                      borderRadius: '12px',
                      fontSize: '0.9rem',
                      lineHeight: 1.65,
                      color: 'var(--text-main)',
                      whiteSpace: 'pre-wrap'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#818cf8', fontWeight: 800 }}>
                        <HelpCircle size={18} /> Detailed Concept Breakdown & Best Practices
                      </div>
                      {lastEvaluation.in_depth_explanation}
                    </div>
                  )}
                </div>
              )}
            </div>

            <button
              onClick={() => {
                setShowEvaluationModal(false);
                setShowDeepDive(false);
              }}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '14px' }}
            >
              Continue to Next Question <ArrowRight size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
