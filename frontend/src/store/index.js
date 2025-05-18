// src/store/index.js
import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    csrfToken: null,
  },
  mutations: {
    setUser(state, user) {
      state.user = user
    },
    setCsrfToken(state, token) {
      state.csrfToken = token
    },
  },
  actions: {
    async fetchCsrfToken({ commit }) {
      const response = await fetch('/api/auth/csrf-token', {
        credentials: 'include',
      })
      const data = await response.json()
      commit('setCsrfToken', data.csrf_token)
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.user,
  },
})