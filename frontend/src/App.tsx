import { useState } from 'react'

import LoginPage from '@/pages/LoginPage'
import MainMailPage from '@/pages/MainMailPage'
import SampleMailPage from '@/pages/SampleMailPage'

function App() {
  const [page, setPage] = useState<'sample' | 'live' | 'login'>(() =>
    new URLSearchParams(window.location.search).get('gmail') === 'connected' ? 'live' : 'sample',
  )
  const [returnPage, setReturnPage] = useState<'sample' | 'live'>(
    new URLSearchParams(window.location.search).get('gmail') === 'connected' ? 'live' : 'sample',
  )

  function openConnect(from: 'sample' | 'live') {
    setReturnPage(from)
    setPage('login')
  }

  if (page === 'login') return <LoginPage onBack={() => setPage(returnPage)} />
  if (page === 'live') return <MainMailPage onConnect={() => openConnect('live')} />
  return <SampleMailPage onConnect={() => openConnect('sample')} />
}

export default App
