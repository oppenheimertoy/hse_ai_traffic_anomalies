import { useState } from "react"

export const useForm = () => {
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

  return {
    files,
    addFiles,
    removeFile,
    clear,
  }
}