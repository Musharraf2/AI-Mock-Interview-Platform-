import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import AuthContainer from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import SessionSetupPage from './pages/SessionSetupPage';
import InterviewSimulatorPage from './pages/InterviewSimulatorPage';
import ReportPage from './pages/ReportPage';

function MainApp() {
  const { user, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activeSessionData, setActiveSessionData] = useState(null);
  const [selectedReportId, setSelectedReportId] = useState(null);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'var(--bg-dark)',
        color: 'var(--primary)'
      }}>
        Initializing IntervAI Platform...
      </div>
    );
  }

  if (!user) {
    return (
      <div>
        <Navbar activeTab="login" setActiveTab={() => {}} />
        <AuthContainer onAuthSuccess={() => setActiveTab('dashboard')} />
      </div>
    );
  }

  const handleSessionStarted = (sessionData) => {
    setActiveSessionData(sessionData);
    setActiveTab('simulator');
  };

  const handleInterviewCompleted = (sessionId) => {
    setSelectedReportId(sessionId);
    setActiveTab('report');
  };

  const handleViewReport = (sessionId) => {
    setSelectedReportId(sessionId);
    setActiveTab('report');
  };

  return (
    <div>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main>
        {activeTab === 'dashboard' && (
          <DashboardPage
            onStartNew={() => setActiveTab('setup')}
            onViewReport={handleViewReport}
          />
        )}
        {activeTab === 'setup' && (
          <SessionSetupPage
            onSessionStarted={handleSessionStarted}
          />
        )}
        {activeTab === 'simulator' && (
          <InterviewSimulatorPage
            initialData={activeSessionData}
            onComplete={handleInterviewCompleted}
          />
        )}
        {activeTab === 'report' && (
          <ReportPage
            sessionId={selectedReportId}
            onBackToDashboard={() => setActiveTab('dashboard')}
          />
        )}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
