import { useEffect, useState } from "react"
import { API_V1_URL } from "../config"
import { authenticate, authenticatedRequest } from "../services/authFetch"
import { tokenStore } from "../services/tokenStore"
import { JWTToken } from "../types/token"


export const useAuth = () => {

  const loginURL = API_V1_URL + 'auth/token/'
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | undefined>(undefined)
  const [token, setToken] = useState<JWTToken | undefined>()
  const [error, setError] = useState<string | undefined>(undefined)
  const store = tokenStore

  const getInitials = async () => {
    const accessToken = store.getAccessToken()
    const refreshToken = store.getRefreshToken()
    if (accessToken !== null && refreshToken !== null) {
      setToken({
        accessToken: accessToken,
        refreshToken: refreshToken
      })
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      authenticatedRequest("GET", "users/me",).then(_ => setIsAuthenticated(true)).catch(_ => setIsAuthenticated(false))
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const data = await authenticate(
        loginURL, username, password
      )
      setToken({
        accessToken: data.accessToken,
        refreshToken: data.refreshToken
      })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'An unknown error occurred')
    }
  }

  const logout = () => {
    setToken(undefined)
  }
  useEffect(() => {
    if (token !== undefined) {
      if (store.getAccessToken() !== token.accessToken) {
        store.setAccessToken(token.accessToken)
      }
      if (store.getRefreshToken() !== token.refreshToken) {
        store.setRefreshToken(token.refreshToken)
      }
      setIsAuthenticated(true)
    }

  }, [token, store, setIsAuthenticated])

  useEffect(() => {
    getInitials()
  }, [])

  return {
    login,
    error,
    logout,
    isAuthenticated
  }
}