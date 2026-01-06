import { Box } from "@chakra-ui/react"
import { FileInputForm } from "./fileInputForm"
import { ContentContainer } from "./contentContainer"

export const Page: React.FC = () => {
  return (
    <Box>
      <FileInputForm />
      <ContentContainer/>
    </Box>
  )
}