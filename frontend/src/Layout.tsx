import { Box, Button, HStack, Menu, Portal, Spacer } from "@chakra-ui/react"
import React, { useState } from "react"
import MainPage from "./pages/main"
import HistoryPage from "./pages/history"
import AccountPage from "./pages/account"
import { MdAccountCircle } from "react-icons/md"
import { LuChartBar, LuHistory } from "react-icons/lu"



type SelectedPage = {
  index: number
  icon: React.ReactNode
  title: string
  component: React.ReactNode
}

export const Layout: React.FC = () => {
  const pages: SelectedPage[] = [
    {
      index: 0,
      icon: <LuChartBar />,
      title: "Main",
      component:
        <MainPage />,
    },
    {
      index: 1,
      icon: <LuHistory />,
      title: "History",
      component: <HistoryPage />
    },
  ]



  const [selectedPage, setSelectedPage] = useState<SelectedPage>(pages[0])
  const [isAccountPage, setIsAccountPage] = useState<boolean>(false)
  const handlePageSelection = (index: number) => {
    setSelectedPage(pages[index])
    setIsAccountPage(false)
  }

  const handleAccountMenuSelection = (d: string) => {
    switch (d) {
      case 'logout':
        return
      case 'profile':
        setIsAccountPage(true)
        return
      default:
        return
    }
  }

  return <Box p='4'>
    <Box
      bg={'gray.100'}
      borderRadius='xl'
      p='2'>
      <HStack>
        {
          pages.map(page => <Button
            key={"layout" + page.index}
            variant={'outline'}
            bg='white'

            onClick={() => handlePageSelection(page.index)}>
            {<HStack>
              {page.icon}
              {page.title}
            </HStack>}
          </Button>)
        }

        <Spacer />

        <Menu.Root onSelect={(d) => handleAccountMenuSelection(d.value)}>
          <Menu.Trigger asChild>
            <Button
              variant={'outline'}
              bg='white'>
              <MdAccountCircle />
            </Button>
          </Menu.Trigger>

          <Portal>
            <Menu.Positioner>
              <Menu.Content>
                <Menu.Item value="profile">
                  Profile
                </Menu.Item>

                <Menu.Item
                  value='logout'
                  color={'fg.error'}
                  disabled
                  _hover={{ bg: 'bg.error', color: 'fg.error' }}>
                  Log out
                </Menu.Item>
              </Menu.Content>
            </Menu.Positioner>
          </Portal>
        </Menu.Root>
      </HStack>
    </Box>

    {isAccountPage
      ? <AccountPage /> :
      selectedPage.component
    }
  </Box>
}
