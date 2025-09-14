import React from 'react';
import { Sun, Leaf, TreePine } from "lucide-react";

const Home: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="fixed top-0 left-0 w-full flex items-center justify-center px-10 py-4 bg-white/20 backdrop-blur-sm z-50">
        <div className="flex items-center space-x-6">
          <div className="logo h-14">
            <img src="/logo.png" alt="Logo" className="h-full object-contain" />
          </div>
          <nav className="flex space-x-6">
            <a href="#actual" className="text-emerald-900 text-base font-medium hover:text-emerald-700">Actual</a>
            <a href="#help" className="text-emerald-900 text-base font-medium hover:text-emerald-700">Help</a>
            <a href="/login" className="text-emerald-900 text-base font-medium hover:text-emerald-700">Connection</a>
            <a href="/register" className="text-emerald-900 text-base font-medium hover:text-emerald-700">Inscription</a>
            <a href="#contact" className="text-emerald-900 text-base font-medium hover:text-emerald-700">Contact</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section
        className="relative flex flex-col items-center justify-start text-center pt-40 w-full"
        style={{
          height: "100vh",
          backgroundImage: 'url("/mainback.png")',
          backgroundSize: "cover", 
          backgroundRepeat: "no-repeat",
          backgroundPosition: "center",
        }}
      >
        {/* Overlay */}
        <div className="absolute inset-0 bg-white/40" />

        <div className="relative z-10 px-4">
          <h2 className="text-5xl md:text-6xl font-bold text-emerald-900 mb-6 leading-tight">
            Votre partenaire pour<br />
            la surveillance<br />
            environnementale.
          </h2>
          <p className="text-lg text-gray-800 max-w-2xl mx-auto mb-8">
            La jeune numérique forestière apporte une approche innovante, comprenant gérer et protéger
            les forêts durables face aux défis environnementaux.
          </p>
          <div className="flex justify-center space-x-6">
            <button className="bg-emerald-600 text-white py-3 px-8 rounded-lg hover:bg-emerald-700 transition text-lg">
              Learn
            </button>
            <button className="bg-transparent border border-emerald-600 text-emerald-600 py-3 px-8 rounded-lg hover:bg-emerald-100 transition text-lg">
              Contact
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-10 bg-white">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-16">
          {/* Feature 1 */}
          <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-6 bg-emerald-100 rounded-full flex items-center justify-center">
          <Sun className="w-8 h-8 text-emerald-600" />
          </div>
          <h2 className="text-xl font-semibold text-emerald-800 mb-3">Climate Change</h2>
          <p className="text-gray-600 text-base">
             Science, impacts, and solutions related to climate change, including global transition to renewable energy sources.
          </p>
          </div>

          {/* Feature 2 */}
          <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-6 bg-emerald-100 rounded-full flex items-center justify-center">
          <Leaf className="w-8 h-8 text-emerald-600" />
          </div>
          <h2 className="text-xl font-semibold text-emerald-800 mb-3">Sustainable Living</h2>
          <p className="text-gray-600 text-base">
               Provide information in areas such as sustainable practices in everyday life choices.
          </p>
          </div>

          {/* Feature 3 */}
          <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-6 bg-emerald-100 rounded-full flex items-center justify-center">
          <TreePine className="w-8 h-8 text-emerald-600" />
          </div>
          <h2 className="text-xl font-semibold text-emerald-800 mb-3">Deforestation</h2>
           <p className="text-gray-600 text-base">
              Discussion of deforestation on ecosystems, climate, and biodiversity, as well as reforestation efforts.
           </p>
          </div>
        </div>
      </section>
      {/* New Image Section */}
      <section className="relative w-full">
        <img 
          src="/backsection.png" 
          alt="Background Section" 
          className="w-full h-auto object-cover" 
        />
      </section>
      {/* Purpose Section */}
      <section className="py-20 px-10 bg-white">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          
          {/* Left: Video/Image placeholder */}
          <div className="relative w-full h-64 md:h-80 bg-gray-300 flex items-center justify-center rounded-xl shadow-lg">
            <button className="w-16 h-16 flex items-center justify-center bg-white rounded-full shadow-md hover:scale-105 transition">
              <svg className="w-8 h-8 text-emerald-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </button>
          </div>

          {/* Right: Text content */}
          <div>
            <span className="text-emerald-600 font-semibold uppercase">Purpose</span>
            <h2 className="text-3xl md:text-4xl font-bold text-emerald-900 mt-2 mb-6">
              Creating a Lasting Alliance for a Greener Future
            </h2>
            <p className="text-gray-600 mb-6">
              We are passionate advocates for environmental awareness and sustainable solutions, 
              committed to engaging our partners and communities to make a positive change for our planet.
            </p>

            <ul className="space-y-4 text-gray-700">
              <li className="flex items-start space-x-3">
                <span className="text-emerald-600">✔</span>
                <p><strong>Our Mission:</strong> Explain the mission of your website, which may be to raise awareness, educate, or inspire people to make positive changes.</p>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-emerald-600">✔</span>
                <p><strong>Our Values:</strong> Outline the principles and values that guide your work, such as sustainability, scientific accuracy, inclusivity, and the preservation of wildlife.</p>
              </li>
            </ul>

            <button className="mt-8 bg-emerald-600 text-white py-3 px-6 rounded-lg hover:bg-emerald-700 transition">
              Learn More →
            </button>
          </div>
        </div>
      </section>
            {/* Contact Section */}
      <section id="contact" className="py-20 px-10 bg-gray-50">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

          {/* Left: Illustration / Image */}
          <div className="relative w-full h-64 md:h-80 bg-gray-200 flex items-center justify-center rounded-xl shadow-lg overflow-hidden">
  <img 
    src="/contact-illustration.jpg" 
    alt="Contact Illustration" 
    className="w-full h-full object-cover"
  />
</div>


          {/* Right: Contact Form */}
          <div>
            <span className="text-emerald-600 font-semibold uppercase">Contact</span>
            <h2 className="text-3xl md:text-4xl font-bold text-emerald-900 mt-2 mb-6">
              Get in Touch With Us
            </h2>
            <p className="text-gray-600 mb-6">
              Have questions, suggestions, or want to collaborate?  
              Fill out the form below and our team will get back to you as soon as possible.
            </p>

            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input
                  type="text"
                  placeholder="Your full name"
                  className="mt-1 w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  placeholder="Your email address"
                  className="mt-1 w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Message</label>
                <textarea
                  placeholder="Write your message..."
                  rows={4}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                ></textarea>
              </div>

              <button
                type="submit"
                className="bg-emerald-600 text-white px-6 py-3 rounded-lg hover:bg-emerald-700 transition"
              >
                Send Message →
              </button>
            </form>
          </div>
        </div>
      </section>
             {/* Help Section */}
      <section id="help" className="py-20 px-10 bg-white">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

          {/* Left: Illustration / Video */}
          <div className="relative w-full h-64 md:h-80 bg-gray-200 flex items-center justify-center rounded-xl shadow-lg overflow-hidden">
  <img 
    src="./help-illustration.jpg" 
    alt="Help Illustration" 
    className="w-full h-full object-contain rounded-xl"
  />
</div>


          {/* Right: Help Content */}
          <div>
            <span className="text-emerald-600 font-semibold uppercase">Help</span>
            <h2 className="text-3xl md:text-4xl font-bold text-emerald-900 mt-2 mb-6">
              How Can We Assist You?
            </h2>
            <p className="text-gray-600 mb-6">
              Find answers to common questions, explore our documentation, 
              or reach out directly to our support team for guidance.
            </p>

            <ul className="space-y-4 text-gray-700">
              <li className="flex items-start space-x-3">
                <span className="text-emerald-600">✔</span>
                <p>Step-by-step guides to get started with our platform.</p>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-emerald-600">✔</span>
                <p>FAQs to resolve common issues quickly.</p>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-emerald-600">✔</span>
                <p>Direct support available via chat or email.</p>
              </li>
            </ul>

            <button className="mt-8 bg-emerald-600 text-white py-3 px-6 rounded-lg hover:bg-emerald-700 transition">
              Visit Help Center →
            </button>
          </div>
        </div>
      </section>

      {/* Actual Section */}
      <section id="actual" className="py-20 px-10 bg-gray-50">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

          {/* Left: News / Illustration */}
          <div className="relative w-full h-64 md:h-80 bg-gray-200 flex items-center justify-center rounded-xl shadow-lg">
            <img 
              src="/actual-illustration.jpg" 
              alt="Actual News Illustration" 
              className="w-full h-full object-cover rounded-xl"
            />
          </div>

          {/* Right: News Content */}
          <div>
            <span className="text-emerald-600 font-semibold uppercase">Actual</span>
            <h2 className="text-3xl md:text-4xl font-bold text-emerald-900 mt-2 mb-6">
              Latest News & Updates
            </h2>
            <p className="text-gray-600 mb-6">
              Stay informed about our latest initiatives, research findings, 
              and community events that support sustainability and environmental awareness.
            </p>

            <ul className="space-y-4 text-gray-700">
              <li className="flex items-start space-x-3">
                <span className="text-emerald-600">✔</span>
                <p>Breaking updates on environmental policies.</p>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-emerald-600">✔</span>
                <p>Insights into our ongoing projects and partnerships.</p>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-emerald-600">✔</span>
                <p>Opportunities to engage with our initiatives.</p>
              </li>
            </ul>

            <button className="mt-8 bg-emerald-600 text-white py-3 px-6 rounded-lg hover:bg-emerald-700 transition">
              Read More →
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-emerald-900 text-white py-6">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-sm">© 2025 Forest Digital Twin. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;