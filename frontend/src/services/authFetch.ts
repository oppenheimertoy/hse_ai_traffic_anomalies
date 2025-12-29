import { API_V1_URL } from "../config"
import { UnauthorizedError } from "../errors/auth"
import { tokenStore } from "./tokenStore"

export const authenticatedRequest = async (
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' = "GET",
  url: URL | string,

  body: BodyInit | undefined = undefined,

) => {

  if (body !== undefined && method === 'GET') throw "no body in get method request"

  const store = tokenStore
  const authToken = store.getAccessToken()

  if (authToken === null || authToken.length === 0) throw "no token provided"
  try {
    const headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + authToken,
    }
    const res = await fetch(new URL(url, API_V1_URL), {
      method: method,
      body: body,
      headers: headers
    })
    if (res.status >= 400) throw await new Error("request failed") as UnauthorizedError
    return await res.json()
  } catch (error) {
    if (error) {
      const refreshToken = store.getRefreshToken()
      if (refreshToken === null || refreshToken.length === 0) throw new Error("auth was revoked") as UnauthorizedError
      const headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + authToken,
        "Refresh-Token": "Bearer " + refreshToken,
      }
      const res = await fetch(new URL(url, API_V1_URL), {
        method: method,
        body: body,
        headers: headers
      })
      if (res.status >= 400) throw await new Error("refresh failed") as UnauthorizedError
      console.log(res)
      store.setAccessToken(res.headers.get("X-Access-Token")!)
      store.setRefreshToken(res.headers.get("x-refresh-token")!)
      return (await res.json())
    }
  }
}

export const authenticate = async (
  url: URL | string,
  username: string,
  password: string
) => {
  const body = new URLSearchParams()
  body.set('username', username)
  body.set('password', password)
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body
  })
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || "Login failed")
  }
  const data = await response.json()
  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token
  }
}