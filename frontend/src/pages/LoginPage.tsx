import { Mail } from 'lucide-react'

import { Button } from '@/components/ui/button'

import './LoginPage.css'

type LoginPageProps = {
  onContinue: () => void
}

function LoginPage({ onContinue }: LoginPageProps) {
  return (
    <main className="login-shell">
      <section className="login-panel" aria-labelledby="login-title">
        <div className="login-icon" aria-hidden="true">
          <Mail size={20} />
        </div>
        <h1 id="login-title">Multi Mail</h1>
        <p>Connect and manage multiple Gmail accounts in one place.</p>
        <Button className="login-button" size="lg" type="button" onClick={onContinue}>
          Continue with Google
        </Button>
      </section>
    </main>
  )
}

export default LoginPage
