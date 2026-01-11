import { Box, VStack, SimpleGrid, Badge, Button, CodeBlock, createShikiAdapter, DataList, IconButton, Separator } from "@chakra-ui/react"
import { useHistory } from "./hooks/useHistory"
import { HighlighterGeneric } from "shiki"
import { AnalyzedFile } from "./types/analyzedFile"
import { ChartsContainer } from "./chartsContainer"

export const Page: React.FC = () => {
  const { pollingFiles,
    pollingStatus,
    pollingError } = useHistory()
  return (<Box>
    <VStack>
      <Box>
        {pollingStatus}
        {pollingError !== null && pollingError.message}
      </Box>

      <SimpleGrid>
        {pollingFiles !== undefined && pollingFiles.map(el => <ItemCard
          item={el}
          key={"analyzed_item" + el.id.toString()} />)}
      </SimpleGrid>
    </VStack>
  </Box>)
}

type ItemCardProps = {
  item: AnalyzedFile
}
const ItemCard: React.FC<ItemCardProps> = ({
  item
}) => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const shikiAdapter = createShikiAdapter<HighlighterGeneric<any, any>>({
    async load() {
      const { createHighlighter } = await import("shiki")
      return createHighlighter({
        langs: ["json"],
        themes: ["github-light"],
      })
    },
    theme: "github-light",
  })

  console.log(item)
  return <Box
    bg='gray.100'
    borderRadius={'xl'}
    maxH='600px'
    overflow={'scroll'}
    p='4'>
    <DataList.Root
      variant={'bold'}
      borderRadius={'xl'}
      p='2'
      bg='white'>
      <DataList.Item>
        <DataList.ItemLabel>
          uuid
        </DataList.ItemLabel>

        <DataList.ItemValue>
          {item.id}
        </DataList.ItemValue>
      </DataList.Item>

      <Separator />

      <DataList.Item>
        <DataList.ItemLabel>
          created at
        </DataList.ItemLabel>

        <DataList.ItemValue>
          {item.createdAt.toString()}
        </DataList.ItemValue>
      </DataList.Item>

      <DataList.Item>
        <DataList.ItemLabel>
          updated at
        </DataList.ItemLabel>

        <DataList.ItemValue>
          {item.updatedAt.toString()}
        </DataList.ItemValue>
      </DataList.Item>

      <Separator />

      <DataList.Item>
        <DataList.ItemLabel>
          status
        </DataList.ItemLabel>

        <DataList.ItemValue>
          <Badge colorPalette={item.status === 'done' ? 'green' : item.status === 'error' ? 'red' : 'yellow'}>

            {item.status}
          </Badge>
        </DataList.ItemValue>
      </DataList.Item>

      {item.error &&
        <DataList.Item>
          <DataList.ItemLabel>
            Error
          </DataList.ItemLabel>

          <DataList.ItemValue>
            {item.error}
          </DataList.ItemValue>
        </DataList.Item>
      }

      {item.result && <DataList.Item>
        <DataList.ItemLabel>
          Result charts
        </DataList.ItemLabel>

        <DataList.ItemValue>
          <ChartsContainer result={item.result} />
        </DataList.ItemValue>
      </DataList.Item>
      }

      {item.result && <DataList.Item>
        <DataList.ItemLabel>
          Result data
        </DataList.ItemLabel>

        <DataList.ItemValue>
          <CodeBlock.AdapterProvider value={shikiAdapter}>
            <CodeBlock.Root
              maxLines={10}
              code={JSON.stringify(
                item.result, null, 2
              )}
              language="json"
            >

              <CodeBlock.Header>
                <CodeBlock.Title />

                <CodeBlock.Control>
                  <CodeBlock.CopyTrigger asChild>
                    <IconButton
                      bg='transparent'
                      variant="outline"
                      size="2xs"
                      _hover={{ borderColor: 'white' }}

                    >
                      <CodeBlock.CopyIndicator p='1' />
                    </IconButton>
                  </CodeBlock.CopyTrigger>
                </CodeBlock.Control>
              </CodeBlock.Header>

              <CodeBlock.Content>
                <CodeBlock.Code>
                  <CodeBlock.CodeText />
                </CodeBlock.Code>

                <CodeBlock.Overlay>
                  <CodeBlock.CollapseTrigger asChild>
                    <Button
                      variant="outline"
                      bg={'transparent'}
                      w='100px'
                      size="xs"
                      _hover={{ borderColor: 'white' }}
                    >
                      Expand
                    </Button>
                  </CodeBlock.CollapseTrigger>
                </CodeBlock.Overlay>
              </CodeBlock.Content>
            </CodeBlock.Root>
          </CodeBlock.AdapterProvider>

        </DataList.ItemValue>
      </DataList.Item>}
    </DataList.Root>
  </Box >
}