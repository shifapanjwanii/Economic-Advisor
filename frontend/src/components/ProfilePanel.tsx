import { useState, FormEvent } from 'react'

interface ProfilePanelProps {
  onClose: () => void
}

interface ProfileData {
  income_range: string
  debt_level: string
  savings: string
  risk_tolerance: string
  financial_goals: string
}

const API_BASE = '/api/v1'

function ProfilePanel({ onClose }: ProfilePanelProps) {
  const [profile, setProfile] = useState<ProfileData>({
    income_range: '',
    debt_level: '',
    savings: '',
    risk_tolerance: 'Moderate',
    financial_goals: '',
  })
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setMessage('')

    try {
      const userId = localStorage.getItem('economic_advisor_user_id') || 'anonymous'
      const response = await fetch(`${API_BASE}/profile/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          profile,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to update profile')
      }

      setMessage('Profile updated successfully! The advisor will now personalize recommendations.')
    } catch (error) {
      setMessage('Failed to update profile. Please ensure the backend is running.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="profile-panel">
      <div className="profile-header">
        <h2>My Financial Profile</h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      <p className="profile-description">
        Help the advisor give you personalized recommendations by sharing some
        information about your financial situation. All information is stored
        locally with your conversation.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="income">Income Range</label>
          <select
            id="income"
            value={profile.income_range}
            onChange={(e) => setProfile({ ...profile, income_range: e.target.value })}
          >
            <option value="">Prefer not to say</option>
            <option value="Under $30,000">Under $30,000</option>
            <option value="$30,000 - $50,000">$30,000 - $50,000</option>
            <option value="$50,000 - $75,000">$50,000 - $75,000</option>
            <option value="$75,000 - $100,000">$75,000 - $100,000</option>
            <option value="$100,000 - $150,000">$100,000 - $150,000</option>
            <option value="Over $150,000">Over $150,000</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="debt">Debt Level</label>
          <select
            id="debt"
            value={profile.debt_level}
            onChange={(e) => setProfile({ ...profile, debt_level: e.target.value })}
          >
            <option value="">Prefer not to say</option>
            <option value="No debt">No debt</option>
            <option value="Low (under $10,000)">Low (under $10,000)</option>
            <option value="Moderate ($10,000 - $50,000)">Moderate ($10,000 - $50,000)</option>
            <option value="High ($50,000 - $100,000)">High ($50,000 - $100,000)</option>
            <option value="Very High (over $100,000)">Very High (over $100,000)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="savings">Emergency Fund / Savings</label>
          <select
            id="savings"
            value={profile.savings}
            onChange={(e) => setProfile({ ...profile, savings: e.target.value })}
          >
            <option value="">Prefer not to say</option>
            <option value="Less than 1 month expenses">Less than 1 month expenses</option>
            <option value="1-3 months expenses">1-3 months expenses</option>
            <option value="3-6 months expenses">3-6 months expenses</option>
            <option value="6-12 months expenses">6-12 months expenses</option>
            <option value="Over 12 months expenses">Over 12 months expenses</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="risk">Risk Tolerance</label>
          <select
            id="risk"
            value={profile.risk_tolerance}
            onChange={(e) => setProfile({ ...profile, risk_tolerance: e.target.value })}
          >
            <option value="Conservative">Conservative - Preserve capital, minimize risk</option>
            <option value="Moderate">Moderate - Balance growth and stability</option>
            <option value="Aggressive">Aggressive - Maximize growth, accept higher risk</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="goals">Financial Goals</label>
          <textarea
            id="goals"
            value={profile.financial_goals}
            onChange={(e) => setProfile({ ...profile, financial_goals: e.target.value })}
            placeholder="e.g., Pay off student loans, save for house down payment, build retirement fund..."
            rows={3}
          />
        </div>

        {message && (
          <div className={`message-banner ${message.includes('Failed') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}

        <button type="submit" className="save-button" disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  )
}

export default ProfilePanel
