import { authenticatedRequest } from "../../../services/authFetch"
import { AnalyzedFile } from "../types/analyzedFile"
const filesURL = "history"

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
    status: res.status.toLowerCase(),
    userId: res.user_id,
  }
}

export const pollFiles = async (files: AnalyzedFile[]) => {
  const preparedBody = {ids: files.map(file => file.id)}
  const res = await authenticatedRequest(
    "POST", filesURL, JSON.stringify(preparedBody)
  )
  return (await res).map(convertResponseToAnalyzedFile)
}