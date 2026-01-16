import { useState, useCallback } from 'react'
import ChatInterface from './components/ChatInterface'
import ProfilePanel from './components/ProfilePanel'
import { useChat } from './hooks/useChat'

function App() {
  const [showProfile, setShowProfile] = useState(false)
  const { messages, isLoading, toolCalls, sendMessage } = useChat()

  const toggleProfile = useCallback(() => {
    setShowProfile(prev => !prev)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>Economic Decision Advisor</h1>
          <p className="subtitle">AI-powered financial guidance using real-time economic data</p>
        </div>
        <button className="profile-toggle" onClick={toggleProfile}>
          {showProfile ? 'Hide Profile' : 'My Profile'}
        </button>
      </header>

      <main className="app-main">
        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          toolCalls={toolCalls}
          onSendMessage={sendMessage}
        />

        {showProfile && (
          <ProfilePanel onClose={toggleProfile} />
        )}
      </main>

      <footer className="app-footer">
        <p>
          Data sources: FRED (Federal Reserve), Financial News APIs, Exchange Rate Services
        </p>
        <p className="disclaimer">
          This advisor provides educational information only, not professional financial advice.
        </p>
      </footer>
    </div>
  )
}

export default App
