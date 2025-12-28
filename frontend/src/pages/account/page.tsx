import { Box, DataList, Separator, Spinner } from "@chakra-ui/react"
import { useUser } from "./hooks/useUser"

export const Page: React.FC = () => {
  const { user, userStatus } = useUser()

  return <Box>
    {
      userStatus === 'success' && user !== undefined ?
        <DataList.Root>
          {Object.entries(user).map(entry => <DataList.Item>
            <DataList.ItemLabel>
              {entry[0]}
            </DataList.ItemLabel>

            <DataList.ItemValue>
              {(entry[1] ?? "unknown").toString()}
            </DataList.ItemValue>
          </DataList.Item>)}
        </DataList.Root>
        : <Spinner />
    }

    <Separator/>
  </Box>
}