/* eslint-disable @typescript-eslint/no-explicit-any */
import { authenticatedRequest } from "../../../services/authFetch"
import { AnalyzedFile, AnalyzedFileResult, IsolationForestResult } from "../types/analyzedFile"

const filesURL = "forward"

const convertIsolationForest = (resIsolationForest: any): IsolationForestResult | undefined => {
  if (resIsolationForest !== null) {
    return {
      anomalyScores: resIsolationForest.anomaly_scores,
      anomalies: resIsolationForest.anomalies,
    }
  }
}

const convertResult = (resResult: any): AnalyzedFileResult | undefined => {
  if (resResult !== null)
    return {
      isolationForest: convertIsolationForest(resResult.isolation_forest),
    }
}

const convertResponseToAnalyzedFile = (res: any): AnalyzedFile => {
  return {
    id: res.id,
    createdAt: res.created_at,
    updatedAt: res.updated_at,
    isDeleted: res.deleted,
    deletedAt: res.deleted_at,
    fileUrl: res.file_url,
    result: convertResult(res.result),
    error: res.error,
    status: res.status.toLowerCase(),
    userId: res.user_id,
  }
}

export const sendFile = async (file: File): Promise<AnalyzedFile> => {
  const formData = new FormData()
  formData.append(
    "pcap", file, file.name
  )
  const res = await authenticatedRequest(
    "POST",
    filesURL,
    formData
  )
  return convertResponseToAnalyzedFile(res)
}