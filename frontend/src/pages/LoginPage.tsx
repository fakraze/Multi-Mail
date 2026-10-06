import { ArrowLeft, Mail } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { startGoogleOAuth } from '@/services/googleOAuth'

import './LoginPage.css'

function LoginPage({ onBack }: { onBack: () => void }) {
  return (
    <main className="login-shell">
      <section className="login-panel" aria-labelledby="login-title">
        <Button className="login-back-button" variant="ghost" size="sm" type="button" onClick={onBack}>
          <ArrowLeft aria-hidden="true" size={16} />
          Back
        </Button>
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
