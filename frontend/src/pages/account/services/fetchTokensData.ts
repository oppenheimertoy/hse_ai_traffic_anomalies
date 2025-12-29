import { authenticatedRequest } from "../../../services/authFetch"
import { Token } from "../types/token"

const tokensURL = "users/tokens"

const convertResponseToTokens = (res: any): Token[] => {
  return res.map((t: any) => ({
    id: t.id,
    token: t.token,
    expiresAt: t.expires_at as Date,
    userId: t.user_id,
    createdAt: t.created_at as Date,
    updatedAt: t.updated_at as Date,
    isDeleted: t.deleted,
    deletedAt: t.deleted_at as Date | undefined
  }))
}

export const fetchTokensData = async () => {
  const data = await authenticatedRequest("GET", tokensURL,)
  const target = convertResponseToTokens(data)
  console.log(target)
  return target
}