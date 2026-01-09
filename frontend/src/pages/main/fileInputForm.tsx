import { Text, Box, Button, FileUpload, HStack, Spinner, Separator, VStack } from "@chakra-ui/react"
import { LuDelete, LuFileCog, LuX } from "react-icons/lu"
import { useForm } from "./hooks/useForm"
import { bytesToMegabytes } from "../../utils/fileSize"

export const FileInputForm: React.FC = () => {
  const { files, addFiles, removeFile, clear, sendFile } = useForm()
  const handleFileSend = () => {
    console.log(files)
    sendFile(files[0])
  }
  return <Box
    marginTop={'4'}
    p='4'
    bg='gray.100'
    borderRadius={'xl'}>
    <FileUpload.Root
      bg='white'
      onFileAccept={(details) => addFiles(details.files)}
      allowDrop
      p='4'
      borderRadius={'xl'}
    >
      <FileUpload.HiddenInput />

      <HStack
        width={'1/5'}
        bg='white'
        p='2'
        borderRadius={'xl'}
        justify={'space-between'}
      >
        <Text
          as="h2"
          fontWeight={'bold'}>
          Upload
        </Text>

        <Button
          size={'sm'}
          color={'gray.200'}
          variant={'outline'}
          colorPalette={'red'}
          disabled={files.length === 0}
          _hover={{ 'borderColor': 'red.300' }}
          onClick={clear}
        >
          <LuDelete color='red' />

          <Text color={'black'}>
            Clear
          </Text>
        </Button>
      </HStack>

      <FilesList
        files={files}
        removeFile={removeFile} />

      <FileUpload.Trigger asChild>
        <Button

          color={'gray.200'}
          variant={'outline'}
          size={'sm'}>
          <LuFileCog color='black' />
          <Text color='black'>.pcap</Text>
        </Button>
      </FileUpload.Trigger>
    </FileUpload.Root>

    <Separator p='2' />

    <Button

      variant='outline'
      bg={files.length > 0 ? 'white' : undefined}
      disabled={files.length === 0}
      onClick={handleFileSend}
    >
      <Text>Start</Text>

      {files.length > 0 &&
        <HStack justify={'space-between'}>
          <Separator
            h='20px'

            orientation={'vertical'}>
            <div style={{ color: 'black', width: '1px' }}></div>
          </Separator>

          <Text>
            {files.length}
          </Text>
        </HStack>
      }
    </Button >
  </Box >
}

type FilesListProps = {
  files: File[]
  removeFile: (index: number) => void
}
const FilesList: React.FC<FilesListProps> = ({
  files, removeFile
}) => {
  if (files.length === 0) return <Box>No files provided</Box>
  return <Box
    bg='white'
    borderRadius={'xl'}
    p='2'>
    {files === undefined ?
      <Spinner />
      : files.map((file, index) => <Box>
        <HStack
          p='2'
          bg='gray.100'
          borderRadius={'lg'}>
          <VStack alignItems={'start'}>
            <Text>
              {file.name}
            </Text>

            <Text>
              {bytesToMegabytes(file.size)}
            </Text>
          </VStack>

          <Button
            bg='white'
            variant={'outline'}
            onClick={() => removeFile(index)}
            _hover={{ borderColor: 'red.300' }}
            size={'sm'}>
            <LuX color='red' />
          </Button>
        </HStack>
      </Box>)}
  </Box>
}