// на фронте будет применяться только jwt по очевидным причинам
export type JWTToken = {
  accessToken: string
  refreshToken: string
}