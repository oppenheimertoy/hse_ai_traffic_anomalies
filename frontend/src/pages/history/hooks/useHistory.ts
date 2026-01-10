import { useQuery } from "@tanstack/react-query"

import { AnalyzedFile } from "../types/analyzedFile"
import { pollFiles } from '../service/pollItems'

export const useHistory = () => {


  const { data: pollingFiles, status: pollingStatus, error: pollingError } = useQuery<AnalyzedFile[]>({
    queryKey: ["files"],
    queryFn: () => pollFiles(),
    refetchInterval: () => {
      return 5000
    }
  })


  return {

    pollingFiles,
    pollingStatus,
    pollingError
  }
}
