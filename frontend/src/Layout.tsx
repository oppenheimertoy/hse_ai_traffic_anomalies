import { Box, Button, HStack, SegmentGroup, Spacer } from "@chakra-ui/react"
import { useState } from "react"
import MainPage from "./pages/main"
import HistoryPage from "./pages/history"
import AccountPage from "./pages/account"

type LayoutProps = {
  children?: React.ReactNode
}

type SelectedPage = {
  index: number
  title: string
  component: React.ReactNode
}

export const Layout: React.FC<LayoutProps> = () => {
  const pages: SelectedPage[] = [
    {
      index: 0,
      title: "Main",
      component:
        <MainPage />,
    },
    {
      index: 1,
      title: "History",
      component: <HistoryPage />
    }
  ]


  const [selectedPage, setSelectedPage] = useState<SelectedPage>(pages[0])
  const [isAccountPage, setIsAccountPage] = useState<boolean>(false)
  
  const handlePageSelection = (index: number) => {
    setSelectedPage(pages[index])
    setIsAccountPage(false)
  }

  const handleAccountPageSelection = () => {
    setIsAccountPage(true)
  }
  return <Box p='4'>
    <Box
      bg={'gray.100'}
      borderRadius='2xl'
      p='2'>
      <HStack>
        {
          pages.map(page => <Button
            variant={'outline'}
            bg='white'
            onClick={() => handlePageSelection(page.index)}>
            {page.title}
          </Button>)
        }

        <Spacer />

        <Button
          onClick={handleAccountPageSelection}
          variant={'outline'}
          bg='white'>
          Account
        </Button>
      </HStack>
    </Box>

    {isAccountPage
      ? <AccountPage /> :
      selectedPage.component
    }
  </Box>
}