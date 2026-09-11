import React from 'react';
import { Bot, User, LogOut, LayoutDashboard, PlayCircle, Award } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ activeTab, setActiveTab }) {
  const { user, logout } = useAuth();

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      borderBottom: '1px solid var(--border-glass)',
      background: 'rgba(9, 13, 22, 0.85)',
      backdropFilter: 'blur(12px)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      {/* Brand Logo */}
      <div 
        onClick={() => setActiveTab('dashboard')} 
        style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
      >
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, var(--primary), var(--purple))',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px var(--primary-glow)'
        }}>
          <Bot size={24} color="white" />
        </div>
        <div>
          <span style={{ fontSize: '1.25rem', fontWeight: 800, background: 'linear-gradient(90deg, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            IntervAI
          </span>
          <span className="badge-pill badge-indigo" style={{ marginLeft: '8px', fontSize: '0.65rem' }}>
            LangGraph + Gemini
          </span>
        </div>
      </div>

      {/* Navigation Tabs */}
      {user && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={activeTab === 'dashboard' ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '8px 16px', fontSize: '0.9rem' }}
          >
            <LayoutDashboard size={16} /> Dashboard
          </button>
          <button 
            onClick={() => setActiveTab('setup')}
            className={activeTab === 'setup' ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '8px 16px', fontSize: '0.9rem' }}
          >
            <PlayCircle size={16} /> Start Mock Interview
          </button>
        </div>
      )}

      {/* Right User Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid var(--border-glass)'
              }}>
                <User size={18} color="#818cf8" />
              </div>
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{user.fullName}</span>
            </div>
            <button 
              onClick={logout} 
              className="btn-secondary" 
              style={{ padding: '8px 12px', fontSize: '0.85rem', color: 'var(--rose)' }}
            >
              <LogOut size={16} /> Logout
            </button>
          </div>
        ) : (
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Empowered by Spring Boot & Multi-Agent AI
          </span>
        )}
      </div>
    </nav>
  );
}
