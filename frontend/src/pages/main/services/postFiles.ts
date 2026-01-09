import { authenticatedRequest } from "../../../services/authFetch"
import { AnalyzedFile } from "../types/analyzedFile"

const filesURL = "forward"

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const convertResponseToAnalyzedFile = (res: any): AnalyzedFile => {
  return {
    id: res.id,
    createdAt: res.created_at,
    updatedAt: res.updated_at,
    isDeleted: res.deleted,
    deletedAt: res.deleted_at,
    fileUrl: res.file_url,
    result: res.result,
    error: res.error,
    status: res.status.lowerCase(),
    userId: res.user_id,
  }
}

export const sendFile = async (file: File): Promise<AnalyzedFile> => {
  const formData = new FormData()
  formData.append(
    "pcap", file, file.name
  )
  console.log(formData)
  const res = await authenticatedRequest(
    "POST",
    filesURL,
    formData
  )
  return convertResponseToAnalyzedFile(await res.json())
}