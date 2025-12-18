import React, { useState } from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import Features from './components/Features'
import Login from './pages/Login'

export default function App() {
  const [showLogin, setShowLogin] = useState(false)
  const containerClass = `min-h-screen ${showLogin ? '' : 'bg-white'} text-gray-800`

  React.useEffect(() => {
    // Prevent background scroll when the login/register overlay is open
    if (showLogin) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [showLogin])

  return (
    <div className={containerClass}>
      <Header onLogin={() => setShowLogin(true)} />
      <main>
        {showLogin ? (
          <Login onClose={() => setShowLogin(false)} />
        ) : (
          <>
            <Hero />
            <Features />

            <div className="fixed bottom-6 right-6 z-50">
              <a href="#" className="w-14 h-14 bg-green-500 rounded-full flex items-center justify-center text-white text-2xl shadow-2xl hover:bg-green-600 transition hover:scale-110">
                <i className="fab fa-whatsapp"></i>
              </a>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
