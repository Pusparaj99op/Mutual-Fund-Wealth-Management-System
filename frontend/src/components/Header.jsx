import React from 'react'

export default function Header({ onLogin }) {
  return (
    <header className="bg-white border-b sticky top-0 z-50">
      <div className="container mx-auto px-4 flex items-center justify-between h-20">
        <div className="flex items-center space-x-2">
          <div className="w-9 h-9 bg-blue-900 flex items-center justify-center rounded-tr-xl rounded-bl-xl">
            <a href="#" aria-label="Home">
              <img src="assets/logo.svg" alt="Federal Wealth logo" className="w-8 h-8 object-cover rounded-tr-xl rounded-bl-xl" />
            </a>
          </div>
          <span className="text-xl font-extrabold tracking-tighter text-blue-900">Federal Wealth Management System</span>
        </div>

        <nav className="hidden lg:flex items-center space-x-6 text-sm font-semibold text-gray-600">
          <a href="#" className="hover:text-blue-600 transition">Investment Solutions</a>
          <a href="#" className="hover:text-blue-600 transition">Planning Tools</a>
          <a href="#" className="hover:text-blue-600 transition">Client Services</a>
          <a href="#" className="bg-blue-50 text-blue-700 px-4 py-2 rounded-md hover:bg-blue-100">About Us</a>
        </nav>

        <div className="flex items-center space-x-3">
          <button className="p-2 text-gray-400 hover:text-blue-600 hidden md:block"><i className="fas fa-search"></i></button>
          <button className="hidden md:block border border-blue-600 text-blue-600 px-5 py-2 rounded-md text-sm font-bold hover:bg-blue-50 transition">Open Account</button>
          <button onClick={() => onLogin && onLogin()} className="bg-blue-600 text-white px-6 py-2 rounded-md text-sm font-bold hover:bg-blue-700 shadow-md transition">Login</button>
        </div>
      </div>

      <div className="lg:hidden bg-white border-t p-4 space-y-4">
        <a href="#" className="block font-medium">Investment Solutions</a>
        <a href="#" className="block font-medium">Planning Tools</a>
        <a href="#" className="block font-medium">Client Services</a>
        <hr />
        <button className="w-full border border-blue-600 text-blue-600 py-2 rounded">Open Account</button>
      </div>
    </header>
  )
}
