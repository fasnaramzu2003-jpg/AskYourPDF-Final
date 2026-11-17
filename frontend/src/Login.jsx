
import { useState } from 'react';
import './App.css';
import { FiFileText } from 'react-icons/fi';

function Login({ onLogin }) {
  const [isLoginMode, setIsLoginMode] = useState(true); // Toggle between Login and Signup
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    // Point directly to your live Render backend
    const backendUrl = import.meta.env.VITE_API_URL;
    const endpoint = isLoginMode ? '/api/token/' : '/api/register/';
    const body = { username, password };

    try {
      const res = await fetch(`${backendUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (res.ok) {
        if (isLoginMode) {
          // If login is successful, save tokens and enter app
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('refresh_token', data.refresh);
          onLogin(); 
        } else {
          // If signup is successful, switch to login mode
          setSuccess('Account created! Please login.');
          setIsLoginMode(true);
          setPassword(''); // Clear password for safety
        }
      } else {
        setError(data.detail || data.error || 'Authentication failed');
      }
    } catch (err) {
      setError('Server error. Is the backend awake? (Wait 50s and try again)');
    }
    setLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <FiFileText color="#2563eb" size={40} style={{ marginBottom: '10px' }} />
          <h2>{isLoginMode ? 'Welcome Back' : 'Create an Account'}</h2>
          <p>{isLoginMode ? 'Login to analyze your documents' : 'Sign up to start using AskYourPDF'}</p>
        </div>

        {error && <div className="login-error">{error}</div>}
        {success && <div className="login-success">{success}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <label>Username</label>
            <input 
              type="text" 
              placeholder="Enter your username" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              required
            />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input 
              type="password" 
              placeholder="••••••••" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required
            />
          </div>
          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? 'Processing...' : (isLoginMode ? 'Login' : 'Sign Up')}
          </button>
        </form>
        
        <div className="login-footer">
          {isLoginMode ? "Don't have an account? " : "Already have an account? "}
          <button 
            type="button"
            className="toggle-btn"
            onClick={() => { setIsLoginMode(!isLoginMode); setError(''); setSuccess(''); }}
          >
            {isLoginMode ? 'Sign up' : 'Login'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Login;
