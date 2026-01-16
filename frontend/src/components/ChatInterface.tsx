import { useState, useRef, useEffect, FormEvent, KeyboardEvent } from 'react'
import ReactMarkdown from 'react-markdown'
import { Message, ToolCall } from '../hooks/useChat'
import ToolCallIndicator from './ToolCallIndicator'

interface ChatInterfaceProps {
  messages: Message[]
  isLoading: boolean
  toolCalls: ToolCall[]
  onSendMessage: (message: string) => void
}

function ChatInterface({ messages, isLoading, toolCalls, onSendMessage }: ChatInterfaceProps) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`
    }
  }, [input])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const suggestedQuestions = [
    "Is now a good time to save or pay down debt?",
    "How does current inflation affect my purchasing power?",
    "What's the current unemployment rate and what does it mean?",
  ]

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-header">
              <span className="message-role">
                {message.role === 'user' ? 'You' : 'Economic Advisor'}
              </span>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
            <div className="message-content">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant loading">
            <div className="message-header">
              <span className="message-role">Economic Advisor</span>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="loading-text">Analyzing economic data...</span>
            </div>
          </div>
        )}

        {toolCalls.length > 0 && (
          <ToolCallIndicator toolCalls={toolCalls} />
        )}

        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div className="suggested-questions">
          <p className="suggested-label">Suggested questions:</p>
          <div className="suggested-buttons">
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                className="suggested-button"
                onClick={() => onSendMessage(question)}
                disabled={isLoading}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      <form className="input-form" onSubmit={handleSubmit}>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about inflation, interest rates, savings decisions..."
          disabled={isLoading}
          rows={1}
        />
        <button type="submit" disabled={!input.trim() || isLoading}>
          {isLoading ? 'Analyzing...' : 'Send'}
        </button>
      </form>
    </div>
  )
}

export default ChatInterface
