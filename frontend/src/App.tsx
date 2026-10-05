import { useState } from 'react'

import LoginPage from '@/pages/LoginPage'
import MainMailPage from '@/pages/MainMailPage'

function App() {
  const [page, setPage] = useState<'mail' | 'login'>('mail')
  const [showPlaceholderNotice, setShowPlaceholderNotice] = useState(false)

  return page === 'login' ? (
    <LoginPage
      onContinue={() => {
        setShowPlaceholderNotice(true)
        setPage('mail')
      }}
    />
  ) : (
    <MainMailPage
      onConnect={() => {
        setShowPlaceholderNotice(false)
        setPage('login')
      }}
      initialNotice={
        showPlaceholderNotice
          ? 'Google sign-in is not connected yet. This is a sample inbox preview.'
          : undefined
      }
    />
  )
}

export default App
