import React, { useState } from 'react';
import { interviewApi } from '../services/api';
import { Bot, PlayCircle, Cpu, Layers, Sparkles, Sliders } from 'lucide-react';

const ROLE_PRESETS = [
  {
    role: "Java Backend Developer",
    techStack: "Java 17, Spring Boot, PostgreSQL, Docker, Microservices",
    icon: "☕",
    badge: "Most Popular"
  },
  {
    role: "Frontend React Engineer",
    techStack: "React.js, JavaScript, TypeScript, CSS3, REST APIs, Redux",
    icon: "⚛️",
    badge: "High Demand"
  },
  {
    role: "Full Stack Engineer",
    techStack: "Java Spring Boot, React.js, PostgreSQL, Node.js, REST",
    icon: "🌐",
    badge: "Versatile"
  },
  {
    role: "DevOps & Cloud Engineer",
    techStack: "Docker, Kubernetes, AWS, Terraform, CI/CD, Linux",
    icon: "☁️",
    badge: "Infrastructure"
  }
];

export default function SessionSetupPage({ onSessionStarted }) {
  const [role, setRole] = useState(ROLE_PRESETS[0].role);
  const [techStack, setTechStack] = useState(ROLE_PRESETS[0].techStack);
  const [experienceLevel, setExperienceLevel] = useState("Fresher / Entry Level");
  const [maxQuestions, setMaxQuestions] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const selectPreset = (preset) => {
    setRole(preset.role);
    setTechStack(preset.techStack);
  };

  const handleStart = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await interviewApi.startSession({
        role,
        techStack,
        experienceLevel,
        maxQuestions
      });
      if (onSessionStarted) {
        onSessionStarted(res.data);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to initialize session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ textAlign: 'center', marginBottom: '36px' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 16px',
          borderRadius: '20px',
          background: 'rgba(99, 102, 241, 0.15)',
          color: '#818cf8',
          fontSize: '0.85rem',
          fontWeight: 600,
          marginBottom: '12px'
        }}>
          <Sparkles size={16} /> Configure Multi-Agent Interview Simulation
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '8px' }}>
          Select Role & Technical Focus
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          Our AI Agents will dynamically generate realistic questions, evaluate your technical depth, and deliver follow-up probes.
        </p>
      </div>

      {error && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.15)',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          color: '#fda4af',
          padding: '14px 20px',
          borderRadius: '12px',
          marginBottom: '24px'
        }}>
          {error}
        </div>
      )}

      {/* Preset Role Selector Grid */}
      <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-muted)' }}>
        Quick Role Presets
      </h3>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '32px'
      }}>
        {ROLE_PRESETS.map((preset, idx) => {
          const isSelected = role === preset.role;
          return (
            <div
              key={idx}
              onClick={() => selectPreset(preset)}
              className={`glass-panel ${isSelected ? 'glass-panel-glow' : ''}`}
              style={{
                padding: '20px',
                cursor: 'pointer',
                borderColor: isSelected ? 'var(--primary)' : 'var(--border-glass)',
                background: isSelected ? 'rgba(99, 102, 241, 0.12)' : 'var(--bg-card)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '1.5rem' }}>{preset.icon}</span>
                <span className="badge-pill badge-indigo" style={{ fontSize: '0.65rem' }}>{preset.badge}</span>
              </div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '4px' }}>{preset.role}</h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                {preset.techStack}
              </p>
            </div>
          );
        })}
      </div>

      {/* Customization Form */}
      <form onSubmit={handleStart} className="glass-panel" style={{ padding: '32px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px', color: 'var(--text-muted)' }}>
              Target Job Title / Role
            </label>
            <input
              type="text"
              required
              className="input-glass"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Java Spring Boot Developer"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px', color: 'var(--text-muted)' }}>
              Experience Level
            </label>
            <select
              className="input-glass"
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              style={{ background: '#0f172a' }}
            >
              <option value="Fresher / Entry Level">Fresher / Entry Level (0-1 yrs)</option>
              <option value="Junior">Junior Software Engineer (1-3 yrs)</option>
              <option value="Mid-Level">Mid-Level Engineer (3-5 yrs)</option>
              <option value="Senior Lead">Senior Lead (5+ yrs)</option>
            </select>
          </div>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px', color: 'var(--text-muted)' }}>
            Tech Stack & Specific Focus Topics (Comma separated)
          </label>
          <input
            type="text"
            required
            className="input-glass"
            value={techStack}
            onChange={(e) => setTechStack(e.target.value)}
            placeholder="e.g. Java 17, Spring Boot, PostgreSQL, JWT Security, Microservices"
          />
        </div>

        <div style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              Number of Technical Questions
            </label>
            <span style={{ fontWeight: 700, color: 'var(--primary)' }}>{maxQuestions} Questions</span>
          </div>
          <input
            type="range"
            min="3"
            max="10"
            step="1"
            value={maxQuestions}
            onChange={(e) => setMaxQuestions(parseInt(e.target.value))}
            style={{ width: '100%', accentColor: 'var(--primary)', cursor: 'pointer' }}
          />
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={loading}
          style={{ width: '100%', justifyContent: 'center', padding: '16px', fontSize: '1.05rem' }}
        >
          {loading ? 'Initializing AI Agents & Graph State...' : 'Launch Interactive Interview Room'} <PlayCircle size={20} />
        </button>
      </form>
    </div>
  );
}
