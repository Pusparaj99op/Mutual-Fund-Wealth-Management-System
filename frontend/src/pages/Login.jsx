import React, { useState } from 'react'
import './login.css'

export default function Login({ onClose }) {
  const [mode, setMode] = useState('login') // 'login' or 'register'
  const [visible, setVisible] = useState(false)

  React.useEffect(() => {
    // mount animation
    const t = setTimeout(() => setVisible(true), 10)
    return () => clearTimeout(t)
  }, [])

  const requestClose = () => {
    // play exit animation then call parent onClose
    setVisible(false)
    setTimeout(() => { if (onClose) onClose() }, 220)
  }

  const stop = (e) => e.stopPropagation()

  return (
    <div className={`wrapper ${visible ? 'visible' : ''}`} onClick={requestClose}>
      {mode === 'login' ? (
        <form onSubmit={(e) => e.preventDefault()} className={`form-card ${visible ? 'visible' : ''}`} onClick={stop}>
          <button type="button" aria-label="Close" className="login-close" onClick={requestClose}>✕</button>
          <h1>Login</h1>
          <div className="input-box">
            <input type="text" placeholder="Username" required />
            <i className='bx bxs-user'></i>
          </div>
          <div className="input-box">
            <input type="password" placeholder="Password" required />
            <i className='bx bxs-lock-alt'></i>
          </div>
          <div className="remember-forgot">
            <label><input type="checkbox" />Remember Me</label>
            <a href="#">Forgot Password</a>
          </div>
          <button type="submit" className="btn">Login</button>
          <div className="register-link">
            <p>Dont have an account? <button type="button" className="link-btn" onClick={() => setMode('register')}>Register</button></p>
          </div>
        </form>
      ) : (
        <form onSubmit={(e) => e.preventDefault()} className={`register-form form-card ${visible ? 'visible' : ''}`} onClick={stop}>
          <button type="button" aria-label="Close" className="login-close" onClick={requestClose}>✕</button>
          <h1>Create Account</h1>

          <div className="name-row">
            <div className="input-box">
              <input type="text" placeholder="First Name" required />
            </div>
            <div className="input-box">
              <input type="text" placeholder="Middle Name" />
            </div>
            <div className="input-box">
              <input type="text" placeholder="Last Name" required />
            </div>
          </div>

          <div className="two-col">
            <div className="input-box">
              <input type="tel" placeholder="Phone Number" required inputMode="tel" />
            </div>
            <div className="input-box">
              <input type="text" placeholder="PAN Number" required maxLength={10} />
            </div>
          </div>

          <div className="two-col">
            <div className="input-box">
              <input type="email" placeholder="Email ID" required />
            </div>
            <div className="input-box">
              <input type="text" placeholder="Username" required />
            </div>
          </div>

          <div className="two-col">
            <div className="input-box">
              <input type="password" placeholder="Password" required />
            </div>
            <div className="input-box">
              <input type="password" placeholder="Confirm Password" required />
            </div>
          </div>

          <div className="two-col">
            <div className="input-box">
              <input type="password" placeholder="4-digit PIN" required inputMode="numeric" maxLength={4} pattern="\\d{4}" />
            </div>
            <div className="input-box">
              <input type="password" placeholder="Confirm PIN" required inputMode="numeric" maxLength={4} pattern="\\d{4}" />
            </div>
          </div>

          <button type="submit" className="btn">Register</button>
          <div className="register-link">
            <p>Already have an account? <button type="button" className="link-btn" onClick={() => setMode('login')}>Login</button></p>
          </div>
        </form>
      )}
    </div>
  )
}
