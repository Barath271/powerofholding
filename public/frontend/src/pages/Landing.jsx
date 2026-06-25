import { Link } from 'react-router-dom'
import { useSelector } from 'react-redux'

const Landing = () => {
  const { isAuthenticated } = useSelector(state => state.auth)

  return (
    <div className="min-h-screen bg-gray-50">
      <section className="bg-gradient-to-r from-blue-600 to-purple-700 text-white py-20">
        <div className="container mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6">Power Of Holding</h1>
          <p className="text-xl mb-8">Premium Trading Learning Platform - Master the Art of Holding</p>
          {isAuthenticated ? (
            <Link to="/videos" className="bg-white text-blue-700 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition">
              Go To Class
            </Link>
          ) : (
            <div className="flex gap-4 justify-center">
              <Link to="/register" className="bg-white text-blue-700 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition">
                Get Started
              </Link>
              <Link to="/login" className="border-2 border-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-blue-700 transition">
                Login
              </Link>
            </div>
          )}
        </div>
      </section>

      <section className="py-20">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-lg shadow-lg">
              <h3 className="text-xl font-semibold mb-4">Expert Courses</h3>
              <p className="text-gray-600">Learn from industry professionals with proven track records in trading.</p>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-lg">
              <h3 className="text-xl font-semibold mb-4">Secure Access</h3>
              <p className="text-gray-600">One device login, encrypted streaming, and dynamic watermarks.</p>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-lg">
              <h3 className="text-xl font-semibold mb-4">6-Month Subscription</h3>
              <p className="text-gray-600">Get access to all premium content for 6 months with full support.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Landing
