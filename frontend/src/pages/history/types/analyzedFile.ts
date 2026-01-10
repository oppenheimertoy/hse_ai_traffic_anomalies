import { Base } from "../../../types/base"

type AnalyzedFileStatus = "created" | "processing" | "done" | "error"

export type AnalyzedFile = Base & {
  userId: string
  fileUrl: string
  result: object
  error: string
  status: AnalyzedFileStatus
}