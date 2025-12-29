import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from './Layout'
import { LoginPage } from './authPage'


const client = new QueryClient()
//* нужно для того, чтобы работал dev-tools и расширение
declare global {
  interface Window {
    __TANSTACK_QUERY_CLIENT__:
    import("@tanstack/query-core").QueryClient
  }
}
window.__TANSTACK_QUERY_CLIENT__ = client

function App() {


  return (
    <QueryClientProvider client={client}>
      <LoginPage>
        <Layout />
      </LoginPage>
    </QueryClientProvider>
  )
}

export default App
