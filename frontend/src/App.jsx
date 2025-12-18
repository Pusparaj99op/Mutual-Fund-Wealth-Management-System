import React from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import Features from './components/Features'

export default function App() {
  return (
    <div className="min-h-screen bg-white text-gray-800">
      <Header />
      <main>
        <Hero />
        <Features />

        <div className="fixed bottom-6 right-6 z-50">
          <a href="#" className="w-14 h-14 bg-green-500 rounded-full flex items-center justify-center text-white text-2xl shadow-2xl hover:bg-green-600 transition hover:scale-110">
            <i className="fab fa-whatsapp"></i>
          </a>
        </div>
      </main>
    </div>
  )
}
