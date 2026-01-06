import { authenticatedRequest } from "../../../services/authFetch"
import { Token } from "../types/token"

const tokensURL = "users/tokens"

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const convertResponseToTokens = (res: any): Token => {
  return {
    id: res.id,
    token: res.token,
    expiresAt: res.expired_at,
    userId: res.user_id,
    createdAt: res.created_at,
    updatedAt: res.updated_at,
    isDeleted: res.deleted,
    deletedAt: res.deleted_at
  }
}


export const createTokenRequest = async (expiresAt: Date) => {
  const data = await authenticatedRequest(
    "POST",
    tokensURL,
    JSON.stringify({
      expires_at: expiresAt.toISOString()
    })
  )
  return convertResponseToTokens(data)
}