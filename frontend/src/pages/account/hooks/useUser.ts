import { useQuery } from "@tanstack/react-query"
import { fetchUserData } from "../services/fetchUserData"

export const useUser = () => {
  const { data, status, refetch } = useQuery({
    queryKey: ['user'],
    queryFn: () => fetchUserData(),
  })

  return {
    user: data,
    userStatus: status,
    refetchUser: refetch
  }
}