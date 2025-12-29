import { authenticatedRequest } from "../../../services/authFetch"
import { User } from "../types/user"

const accountURL = "users/me"

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const convertResponseToUser = (res: any): User => {
  return {
    id: res.id,
    username: res.username,
    createdAt: res.created_at,
    updatedAt: res.updated_at,
    isDeleted: res.deleted,
    deletedAt: res.deleted_at
  }
}


export const fetchUserData = async () => {
  const data = await authenticatedRequest("GET", accountURL,)
  const target = convertResponseToUser(data)
  console.log(target)
  return target
}