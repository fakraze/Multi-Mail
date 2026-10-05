import { Mail } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { startGoogleOAuth } from '@/services/googleOAuth'

import './LoginPage.css'

function LoginPage() {
  return (
    <main className="login-shell">
      <section className="login-panel" aria-labelledby="login-title">
        <div className="login-icon" aria-hidden="true">
          <Mail size={20} />
        </div>
        <h1 id="login-title">Multi Mail</h1>
        <p>Connect and manage multiple Gmail accounts in one place.</p>
        <Button className="login-button" size="lg" type="button" onClick={startGoogleOAuth}>
          Continue with Google
        </Button>
      </section>
    </main>
  )
}

export default LoginPage
