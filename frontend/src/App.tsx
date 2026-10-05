import { useState } from 'react'

import LoginPage from '@/pages/LoginPage'
import MainMailPage from '@/pages/MainMailPage'

function App() {
  const [page, setPage] = useState<'mail' | 'login'>('mail')

  return page === 'login' ? (
    <LoginPage />
  ) : (
    <MainMailPage
      onConnect={() => setPage('login')}
    />
  )
}

export default App
