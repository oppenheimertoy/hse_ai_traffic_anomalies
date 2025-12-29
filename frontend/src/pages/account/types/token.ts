import { Base } from "../../../types/base"

export type Token = Base & {
  expiresAt: Date
  userId: string
  token: string
}