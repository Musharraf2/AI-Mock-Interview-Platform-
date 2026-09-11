import React, { useEffect, useState } from 'react';
import { analyticsApi, interviewApi } from '../services/api';
import { PlayCircle, Award, CheckCircle, Clock, ArrowRight, BarChart3, ShieldCheck } from 'lucide-react';

export default function DashboardPage({ onStartNew, onViewReport }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await analyticsApi.getDashboardMetrics();
      setMetrics(res.data);
    } catch (err) {
      console.error("Dashboard error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div style={{ color: 'var(--primary)', fontWeight: 600 }}>Loading Candidate Performance Dashboard...</div>
      </div>
    );
  }

  const { total_sessions, completed_sessions, average_score, session_history, user_profile } = metrics || {};

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px' }}>
      {/* Top Banner Header */}
      <div className="glass-panel" style={{
        padding: '32px',
        borderRadius: '24px',
        marginBottom: '32px',
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1))',
        border: '1px solid rgba(99, 102, 241, 0.25)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '24px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span className="badge-pill badge-emerald">Fresher Candidate Profile</span>
            <span className="badge-pill badge-indigo">{user_profile?.targetRole || 'Software Engineer'}</span>
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '8px' }}>
            Welcome back, {user_profile?.fullName || 'Candidate'} 👋
          </h1>
          <p style={{ color: 'var(--text-muted)', maxWidth: '600px' }}>
            Practice real technical interviews simulated by multi-agent AI. Track your score progression and master system architecture.
          </p>
        </div>
        <button onClick={onStartNew} className="btn-primary" style={{ padding: '16px 28px', fontSize: '1rem' }}>
          <PlayCircle size={20} /> Start New Mock Session
        </button>
      </div>

      {/* Metrics Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px',
        marginBottom: '36px'
      }}>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600 }}>Total Interviews</span>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Clock size={20} color="#818cf8" />
            </div>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800 }}>{total_sessions || 0}</div>
          <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>Simulated sessions</span>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600 }}>Completed</span>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CheckCircle size={20} color="#34d399" />
            </div>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800 }}>{completed_sessions || 0}</div>
          <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>Evaluated reports</span>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600 }}>Average Score</span>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(139, 92, 246, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Award size={20} color="#c084fc" />
            </div>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: average_score >= 75 ? '#34d399' : '#f59e0b' }}>
            {average_score ? `${average_score}/100` : 'N/A'}
          </div>
          <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>Weighted average</span>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600 }}>AI Engine</span>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(236, 72, 153, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ShieldCheck size={20} color="#f472b6" />
            </div>
          </div>
          <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>Multi-Agent System</div>
          <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>Adaptive LLM Pipeline</span>
        </div>
      </div>

      {/* Recent Sessions List Table */}
      <div className="glass-panel" style={{ padding: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={20} color="#818cf8" /> Past Interview Sessions
          </h3>
        </div>

        {!session_history || session_history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <p style={{ marginBottom: '16px' }}>No mock interview sessions recorded yet.</p>
            <button onClick={onStartNew} className="btn-secondary">Start Your First Interview</button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-glass)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  <th style={{ padding: '12px 16px' }}>Session Role</th>
                  <th style={{ padding: '12px 16px' }}>Tech Stack</th>
                  <th style={{ padding: '12px 16px' }}>Status & Questions</th>
                  <th style={{ padding: '12px 16px' }}>Score</th>
                  <th style={{ padding: '12px 16px' }}>Date</th>
                  <th style={{ padding: '12px 16px', textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {session_history.map((s) => {
                  const isCompleted = s.status === 'COMPLETED';
                  const isEndedEarly = s.status === 'ENDED_EARLY';
                  const maxQ = s.max_questions || 5;
                  const answered = s.answered_count || (isCompleted ? maxQ : 0);

                  return (
                    <tr key={s.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', transition: 'background 0.2s' }}>
                      <td style={{ padding: '16px', fontWeight: 600 }}>{s.role}</td>
                      <td style={{ padding: '16px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{s.tech_stack}</td>
                      <td style={{ padding: '16px' }}>
                        {isCompleted ? (
                          <span className="badge-pill badge-emerald">
                            Completed ({answered}/{maxQ} Given)
                          </span>
                        ) : isEndedEarly ? (
                          <span className="badge-pill badge-purple">
                            Ended Early ({answered}/{maxQ} Given)
                          </span>
                        ) : (
                          <span className="badge-pill badge-indigo">
                            In Progress ({answered}/{maxQ} Given)
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '16px', fontWeight: 700, color: s.score >= 75 ? '#34d399' : '#818cf8' }}>
                        {s.has_report || isCompleted || isEndedEarly ? `${s.score || 0}/100` : `${answered}/${maxQ} Given`}
                      </td>
                      <td style={{ padding: '16px', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                        {new Date(s.created_at).toLocaleDateString()}
                      </td>
                      <td style={{ padding: '16px', textAlign: 'right' }}>
                        <button 
                          onClick={() => onViewReport(s.id)}
                          className="btn-secondary" 
                          style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                        >
                          View Report <ArrowRight size={14} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
