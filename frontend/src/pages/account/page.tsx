import { Box, Button, DataList, Text, Separator, Spinner, HStack, Input } from "@chakra-ui/react"
import { useUser } from "./hooks/useUser"
import { useTokens } from "./hooks/useTokens"
import { Token } from "./types/token"
import { useState } from "react"
import { CgCopy } from "react-icons/cg"
import {SingleDatepicker} from "chakra-dayzed-datepicker"
export const Page: React.FC = () => {
  const { user, userStatus } = useUser()
  const { tokens, tokensStatus, create } = useTokens()
  const [expiresAt, setExpiresAt] = useState(new Date())
  return <Box
    bg='gray.100'
    borderRadius={'xl'}
    marginTop='4'
    p='4'>
    {
      userStatus === 'success' && user !== undefined ?
        <Box
          bg='white'
          p='2'
          borderRadius={'xl'}
        >
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
        </Box>
        : <Spinner />
    }

    <Separator m='2' />

    <Box
      bg='white'
      p='2'
      borderRadius={'xl'}
    >
      <HStack >
        <Text>
          Total:
          {' '}
          {tokens?.length}
        </Text>

        <Separator />

        <HStack
          p='2'
        >
          <SingleDatepicker
            name="expiration-date-input"
            date={expiresAt}
            onDateChange={(date) => setExpiresAt(date as Date)} />

          <Button
            variant='outline'
            onClick={() => create(expiresAt)}>
            Create
          </Button>
        </HStack>
      </HStack>

      {
        tokensStatus === "success" && tokens !== undefined ?
          <DataList.Root>
            {tokens.map((token, index) => {
              return (
                <TokenBox
                  index={index}
                  token={token} />
              )
            })}
          </DataList.Root>
          : <Spinner />
      }
    </Box>
  </Box>
}

type TokenBoxProps = { token: Token, index: number }

const TokenBox: React.FC<TokenBoxProps> = ({ token, index }) => {
  return <Box
    bg='gray.100'
    borderRadius={'3xl'}
    p='4'>
    <DataList.Root>
      <DataList.Item>
        <DataList.ItemLabel>
          №
        </DataList.ItemLabel>

        <DataList.ItemValue>
          {index.toString()}
        </DataList.ItemValue>
      </DataList.Item>

      <DataList.Item>
        <DataList.ItemLabel>
          Value
        </DataList.ItemLabel>

        <DataList.ItemValue
          onClick={() => navigator.clipboard.writeText(token.token)}
          border='dashed'
          borderColor={'blue.400'}
          borderRadius={'lg'}
          w='fit-content'
          paddingRight={'2'}
          paddingLeft={'2'}
        >
          <HStack justify={'center'}>
            <CgCopy />
            {token.token}
          </HStack>
        </DataList.ItemValue>
      </DataList.Item>

      <DataList.Item>
        <DataList.ItemLabel>
          Created at
        </DataList.ItemLabel>

        <DataList.ItemValue>
          {token.createdAt.toString()}
        </DataList.ItemValue>
      </DataList.Item>

      <DataList.Item>
        <DataList.ItemLabel>
          Expires in
        </DataList.ItemLabel>

        <DataList.ItemValue>
          {token.expiresAt.toString()}
        </DataList.ItemValue>
      </DataList.Item>
    </DataList.Root>
  </Box>
}