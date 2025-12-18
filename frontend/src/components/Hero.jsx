import React, { useEffect, useState } from 'react'

const slides = [
  {
    title: 'BUILD YOUR FUTURE.<br>INVEST SMARTER.',
    slogan: 'Your Legacy Is Our Priority.',
    img: 'assets/1.jpeg'
  },
  {
    title: 'MAXIMIZE YOUR<br>GROWTH POTENTIAL.',
    slogan: 'Precision Planning for Maximum Prosperity.',
    img: 'assets/2.jpeg'
  },
  {
    title: 'SECURE YOUR<br>RETIREMENT FREEDOM.',
    slogan: 'Securing Your Today. Growing Your Tomorrow.',
    img: 'assets/3.jpg'
  }
]

export default function Hero() {
  const [active, setActive] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setActive((a) => (a + 1) % slides.length), 5000)
    return () => clearInterval(id)
  }, [])

  return (
    <section className="relative hero-gradient text-white overflow-hidden min-h-[500px]">
      <div className="container mx-auto px-4 flex flex-col md:flex-row items-center">
        <div className="w-full md:w-1/2 py-16 md:py-24 z-10">
          {slides.map((s, i) => (
            <div key={i}
                 style={{ display: active === i ? 'block' : 'none' }}
                 className="absolute md:static inset-x-4 md:inset-x-0 md:pl-12 z-30">
              <h1 className="text-4xl md:text-6xl font-black leading-tight" dangerouslySetInnerHTML={{ __html: s.title }} />
              <p className="text-lg md:text-xl mt-4 opacity-90 font-light italic">{s.slogan}</p>
              <button className="mt-8 bg-white text-blue-700 px-8 py-3 rounded font-bold hover:bg-gray-100 transition shadow-lg">Get Started</button>
            </div>
          ))}
        </div>

        <div className="w-full md:w-1/2 relative h-80 md:h-[500px] flex items-end justify-center">
          {slides.map((s, i) => (
            <img key={i}
                 src={s.img}
                 alt={`slide-${i}`}
                 style={{ display: active === i ? 'block' : 'none' }}
                 className="absolute object-cover object-right h-full w-full mask-gradient"
            />
          ))}

          {/* decorative rings removed */}
        </div>
      </div>

      <div className="absolute bottom-8 left-1/2 md:left-4 transform -translate-x-1/2 md:translate-x-0 flex space-x-3 z-20">
        {slides.map((_, i) => (
          <button key={i} onClick={() => setActive(i)}
                  className={`${active === i ? 'w-10 bg-white' : 'w-2 bg-white/40'} h-2 rounded-full transition-all duration-300`} />
        ))}
      </div>
    </section>
  )
}
