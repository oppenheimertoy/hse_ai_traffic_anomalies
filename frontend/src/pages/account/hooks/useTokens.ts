import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { fetchTokensData } from "../services/fetchTokensData"
import { createTokenRequest } from "../services/createTokenRequest"
import { Token } from "../types/token"

export const useTokens = () => {
  const client = useQueryClient()
  const createToken = useMutation<Token, Error, Date>({
    mutationFn: async (expires_at) => await createTokenRequest(expires_at)
    , onSuccess: () => client.invalidateQueries({ queryKey: ['tokens'] })
  })

  const { data, status, refetch } = useQuery({
    queryKey: ['tokens'],
    queryFn: () => fetchTokensData()
  })

  return {
    tokens: data,
    tokensStatus: status,
    refetchTokens: refetch,
    create: createToken.mutate
  }
}