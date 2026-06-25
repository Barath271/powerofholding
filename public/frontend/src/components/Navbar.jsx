import { Link, useNavigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { logout } from '../store'
import api from '../services/api'

const Navbar = () => {
  const { isAuthenticated, user } = useSelector(state => state.auth)
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout')
    } catch (err) {
      console.error(err)
    } finally {
      dispatch(logout())
      navigate('/')
    }
  }

  return (
    <nav className="bg-gray-900 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">Power Of Holding</Link>
        <div className="flex gap-6">
          {!isAuthenticated ? (
            <>
              <Link to="/" className="hover:text-blue-400">Home</Link>
              <Link to="/login" className="hover:text-blue-400">Login</Link>
              <Link to="/register" className="hover:text-blue-400">Register</Link>
            </>
          ) : (
            <>
              <Link to="/" className="hover:text-blue-400">Home</Link>
              <Link to="/videos" className="hover:text-blue-400">Go To Class</Link>
              {user?.role === 'admin' && <Link to="/admin" className="hover:text-blue-400">Admin</Link>}
              <button onClick={handleLogout} className="hover:text-red-400">Logout</button>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navbar
