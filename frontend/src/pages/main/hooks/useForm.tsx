import { skipToken, useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { sendFile } from "../services/postFiles"
import { AnalyzedFile } from "../types/analyzedFile"
import { pollFiles } from "../services/pollFiles"

export const useForm = () => {
  const client = useQueryClient()
  const [files, setFiles] = useState<File[]>([])
  const [filesToPoll, setFilesToPoll] = useState<AnalyzedFile[] | undefined>()
  const { data: pollingFiles, status: pollingStatus, error: pollingError } = useQuery<AnalyzedFile[]>({
    queryKey: ["files", filesToPoll],
    queryFn: filesToPoll
      ? () => {
        console.log(filesToPoll)
        return pollFiles(filesToPoll)
      }
      : skipToken,
    refetchOnMount: false,
    refetchInterval: (queryData) => {
      if (queryData.state.data === undefined) return false
      if (queryData.state.data !== undefined && queryData.state.data.map(file => file.status).filter(status => status === 'processing' || status === 'created').length > 0)
        return 5000
      return false
    }
  })
  const addFiles = (file: File[]) => {
    setFiles(prev => [...prev, ...file])

  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((el, i) => i !== index))
  }

  const clear = () => {
    setFiles([])
  }
  const sendFileMutation = useMutation<AnalyzedFile, Error, File>({
    mutationFn: async (file) =>
      await sendFile(file),
    onSuccess: (data) => {
      setFilesToPoll(prev => prev ? [...prev, data] : [data])
    },
    onError: (e) => console.error(e)
  })

  const sendAllFiles = () => {
    files.forEach((file) => sendFileMutation.mutate(file))
    client.invalidateQueries({ queryKey: ['files'] })

  }

  return {
    files,
    addFiles,
    removeFile,
    clear,
    sendFile: sendFileMutation.mutate,
    sendAllFiles,
    pollingFiles,
    pollingStatus,
    pollingError
  }
}
