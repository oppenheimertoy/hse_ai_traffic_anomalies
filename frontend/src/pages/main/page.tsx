import { Box } from "@chakra-ui/react"
import { FileInputForm } from "./fileInputForm"
import { ContentContainer } from "./contentContainer"
import { useForm } from "./hooks/useForm"

export const Page: React.FC = () => {
  const { files, addFiles, removeFile, clear, sendAllFiles, pollingFiles, pollingStatus, pollingError } = useForm()
  return (
    <Box>
      <FileInputForm
        sendAllFiles={sendAllFiles}
        addFiles={addFiles}
        files={files}
        clear={clear}
        removeFile={removeFile}
      />

      <ContentContainer
        pollingError={pollingError}
        pollingItems={pollingFiles ?? []}
        pollingStatus={pollingStatus}
      />
    </Box>
  )
}