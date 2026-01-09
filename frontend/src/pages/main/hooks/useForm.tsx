import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { sendFile } from "../services/postFiles"
import { AnalyzedFile } from "../types/analyzedFile"

export const useForm = () => {
  const client = useQueryClient()
  const [files, setFiles] = useState<File[]>([])

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
    onSuccess: () => client.invalidateQueries({ queryKey: ["files"] })
  })
  return {
    files,
    addFiles,
    removeFile,
    clear,
    sendFile: sendFileMutation.mutate,
  }
}
