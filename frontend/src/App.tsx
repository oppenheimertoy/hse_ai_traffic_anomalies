import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from './Layout'


const client = new QueryClient()
//* нужно для того, чтобы работал dev-tools и расширение
declare global {
  interface Window {
    __TANSTACK_QUERY_CLIENT__:
    import("@tanstack/query-core").QueryClient;
  }
}
window.__TANSTACK_QUERY_CLIENT__ = client

function App() {


  return (
    <QueryClientProvider client={client}>
      <Layout>

      </Layout>
    </QueryClientProvider>
  )
}

export default App
