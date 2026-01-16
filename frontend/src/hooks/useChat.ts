import { useState, useCallback, useEffect } from 'react'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface ToolCall {
  name: string
  arguments: Record<string, unknown>
}

const API_BASE = '/api/v1'

// Generate or get user ID from localStorage
const getUserId = (): string => {
  let userId = localStorage.getItem('economic_advisor_user_id')
  if (!userId) {
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    localStorage.setItem('economic_advisor_user_id', userId)
  }
  return userId
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([])
  const [userId] = useState(getUserId)

  // Add welcome message on mount
  useEffect(() => {
    const welcomeMessage: Message = {
      id: 'welcome',
      role: 'assistant',
      content: `Hello! I'm your Economic Decision Advisor. I can help you understand how current economic conditions affect your financial decisions.

**Try asking me about:**
- "Is now a good time to save or pay down debt?"
- "How does current inflation affect my purchasing power?"
- "What recent economic news should influence my spending?"

I'll analyze real-time data from the Federal Reserve, financial news, and currency markets to give you personalized guidance.`,
      timestamp: new Date(),
    }
    setMessages([welcomeMessage])
  }, [])

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return

    // Add user message
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setToolCalls([])

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          message: content,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      // Add assistant response
      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMessage])

      // Update tool calls for transparency
      if (data.tool_calls && data.tool_calls.length > 0) {
        setToolCalls(data.tool_calls)
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please make sure the backend server is running and try again.',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }, [userId, isLoading])

  return {
    messages,
    isLoading,
    toolCalls,
    sendMessage,
    userId,
  }
}
