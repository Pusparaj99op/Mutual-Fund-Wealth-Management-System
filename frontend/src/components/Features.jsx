import React from 'react'

export default function Features(){
  return (
    <section className="py-16 bg-white shadow-inner">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-10">
          <div className="group cursor-pointer">
            <div className="w-12 h-12 flex items-center justify-center mb-4 transition-transform group-hover:translate-y-[-5px]">
              <i className="far fa-lightbulb text-4xl text-yellow-500"></i>
            </div>
            <h4 className="font-bold text-gray-900 mb-1">Explore Funds</h4>
            <p className="text-xs text-gray-500 leading-relaxed">Curated selection funds and plans for you</p>
          </div>

          <div className="group cursor-pointer">
            <div className="w-12 h-12 flex items-center justify-center mb-4 transition-transform group-hover:translate-y-[-5px]">
              <i className="fas fa-calculator text-4xl text-blue-900"></i>
            </div>
            <h4 className="font-bold text-gray-900 mb-1">Financial Planning</h4>
            <p className="text-xs text-gray-500 leading-relaxed">Set goals of tools to help you with your investments</p>
          </div>

          <div className="group cursor-pointer">
            <div className="w-12 h-12 flex items-center justify-center mb-4 transition-transform group-hover:translate-y-[-5px]">
              <i className="far fa-calendar-check text-4xl text-blue-600"></i>
            </div>
            <h4 className="font-bold text-gray-900 mb-1">Register Mandate</h4>
            <p className="text-xs text-gray-500 leading-relaxed">Set goals for recurring deposit investments</p>
          </div>

          <div className="group cursor-pointer">
            <div className="w-12 h-12 flex items-center justify-center mb-4 transition-transform group-hover:translate-y-[-5px]">
              <i className="fas fa-chart-line text-4xl text-blue-400"></i>
            </div>
            <h4 className="font-bold text-gray-900 mb-1">Track Performance</h4>
            <p className="text-xs text-gray-500 leading-relaxed">For hassle free recurring deposits</p>
          </div>

          <div className="group cursor-pointer">
            <div className="w-12 h-12 flex items-center justify-center mb-4 transition-transform group-hover:translate-y-[-5px]">
              <i className="fas fa-play-circle text-4xl text-blue-800"></i>
            </div>
            <h4 className="font-bold text-gray-900 mb-1">Starter Hub</h4>
            <p className="text-xs text-gray-500 leading-relaxed">Everything your Guides & webinars FAQS</p>
          </div>

          <div className="group cursor-pointer">
            <div className="w-12 h-12 flex items-center justify-center mb-4 transition-transform group-hover:translate-y-[-5px]">
              <i className="fas fa-headset text-4xl text-gray-700"></i>
            </div>
            <h4 className="font-bold text-gray-900 mb-1">Support Center</h4>
            <p className="text-xs text-gray-500 leading-relaxed">Get help & your Get help & FAQs</p>
          </div>
        </div>
      </div>
    </section>
  )
}
