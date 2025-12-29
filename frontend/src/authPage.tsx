import { Box, Button, Center, Input, Text, VStack } from "@chakra-ui/react"
import { useState } from "react"

import { useAuth } from "./hooks/useAuth"

type LoginPageProps = {
  children: React.ReactNode
}

export const LoginPage: React.FC<LoginPageProps> = ({ children }) => {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const { login, logout, error, isAuthenticated } = useAuth()
  const handleLogin = async () => {
    login(username, password)
  }

  const handleLogout = () => {
    logout()
  }

  if (error !== undefined) return <Center>
    {error}
  </Center>
  if (isAuthenticated) return <>
    {children}
  </>
  return (
    <Center>
      <Box w="360px">
        <VStack
          align="stretch"
          gap="3">
          <Text
            fontSize="lg"
            fontWeight="semibold">
            JWT Authentication
          </Text>

          <Input
            placeholder="Username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />

          <Input
            placeholder="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />

          <Button
            onClick={handleLogin}
            colorScheme="blue">
            Sign in
          </Button>

          <Button
            variant="outline"
            onClick={handleLogout}>
            Sign out
          </Button>

        </VStack>
      </Box>
    </Center>
  )
}
