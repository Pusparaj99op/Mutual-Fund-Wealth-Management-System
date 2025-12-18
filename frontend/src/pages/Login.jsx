import React from 'react'
import './login.css'

export default function Login({ onClose }) {
  return (
    <div className="wrapper">
      <form action="">
        <button type="button" aria-label="Close" className="login-close" onClick={() => onClose && onClose()}>✕</button>
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
          <p>Dont have an account? <a href="#">Register</a></p>
        </div>
      </form>
    </div>
  )
}
