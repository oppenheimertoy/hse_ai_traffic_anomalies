import { Base } from "../../../types/base"

type AnalyzedFileStatus = "created" | "processing" | "done" | "error"

export type IsolationForestResult = {
  anomalyScores: number[]
  anomalies: boolean[]
}

export type AnalyzedFileResult = {
  isolationForest?: IsolationForestResult | undefined
}
export type AnalyzedFile = Base & {
  userId: string
  fileUrl: string
  result?: AnalyzedFileResult | undefined
  error?: string | undefined
  status: AnalyzedFileStatus
}