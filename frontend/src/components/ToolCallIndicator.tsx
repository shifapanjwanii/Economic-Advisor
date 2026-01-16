import { ToolCall } from '../hooks/useChat'

interface ToolCallIndicatorProps {
  toolCalls: ToolCall[]
}

const TOOL_DESCRIPTIONS: Record<string, string> = {
  get_fred_data: 'Federal Reserve Economic Data',
  get_inflation_rate: 'Inflation Rate (CPI)',
  get_interest_rate: 'Interest Rates',
  get_unemployment_rate: 'Unemployment Data',
  get_financial_news: 'Financial News',
  get_exchange_rate: 'Exchange Rates',
  get_purchasing_power: 'Purchasing Power Analysis',
}

const TOOL_ICONS: Record<string, string> = {
  get_fred_data: 'chart',
  get_inflation_rate: 'trending-up',
  get_interest_rate: 'percent',
  get_unemployment_rate: 'users',
  get_financial_news: 'newspaper',
  get_exchange_rate: 'globe',
  get_purchasing_power: 'wallet',
}

function ToolCallIndicator({ toolCalls }: ToolCallIndicatorProps) {
  if (toolCalls.length === 0) return null

  return (
    <div className="tool-calls-panel">
      <div className="tool-calls-header">
        <span className="tool-calls-icon">i</span>
        <span>Data sources consulted:</span>
      </div>
      <div className="tool-calls-list">
        {toolCalls.map((tool, index) => (
          <div key={index} className="tool-call-item">
            <span className={`tool-icon ${TOOL_ICONS[tool.name] || 'data'}`}>
              {getToolIcon(tool.name)}
            </span>
            <span className="tool-name">
              {TOOL_DESCRIPTIONS[tool.name] || tool.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function getToolIcon(toolName: string): string {
  const icons: Record<string, string> = {
    get_fred_data: '📊',
    get_inflation_rate: '📈',
    get_interest_rate: '💹',
    get_unemployment_rate: '👥',
    get_financial_news: '📰',
    get_exchange_rate: '🌍',
    get_purchasing_power: '💰',
  }
  return icons[toolName] || '📋'
}

export default ToolCallIndicator
