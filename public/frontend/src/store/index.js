import { configureStore, createSlice } from '@reduxjs/toolkit'

const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  loading: false
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginSuccess: (state, action) => {
      state.user = action.payload.user
      state.token = action.payload.access_token
      state.isAuthenticated = true
      localStorage.setItem('token', action.payload.access_token)
    },
    logout: (state) => {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    }
  }
})

export const { loginSuccess, logout, setLoading } = authSlice.actions

export const store = configureStore({
  reducer: {
    auth: authSlice.reducer
  }
})
