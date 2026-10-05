import { useState } from 'react'
import { ChevronDown, Inbox, RefreshCw, Search, Star, Tag } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'

import './App.css'

const accounts = ['primary@gmail.com', 'shared@gmail.com']
const labels = ['Work', 'Updates']

type MailView = 'inbox' | 'starred' | `label:${string}`

const messages = [
  {
    id: 'design-system',
    sender: 'Multi Mail Team',
    subject: 'Design system components are ready',
    account: accounts[0],
    time: '9:24 AM',
    starred: true,
    labels: ['Work'],
  },
  {
    id: 'connection',
    sender: 'Gmail Sync',
    subject: 'Account connection preview',
    account: accounts[1],
    time: '8:02 AM',
    starred: false,
    labels: ['Updates'],
  },
]

function App() {
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [activeAccounts, setActiveAccounts] = useState<string[]>(accounts)
  const [view, setView] = useState<MailView>('inbox')
  const [labelsExpanded, setLabelsExpanded] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const visibleMessages = messages.filter(
    (message) =>
      activeAccounts.includes(message.account) &&
      (view === 'inbox' ||
        (view === 'starred' && message.starred) ||
        (view.startsWith('label:') && message.labels.includes(view.slice(6)))),
  )
  const allSelected =
    visibleMessages.length > 0 && visibleMessages.every((message) => selectedIds.includes(message.id))
  const someSelected = visibleMessages.some((message) => selectedIds.includes(message.id))

  return (
    <main className="app-shell">
      <section className="mail-frame" aria-label="Main mail page">
        <aside className="mail-sidebar">
          <h1>Multi Mail</h1>
          <Button className="connect-button" onClick={() => setNotice('Connect Gmail')}>
            Connect Gmail
          </Button>
          <nav className="mail-navigation" aria-label="Mail folders">
            <button
              type="button"
              className="navigation-item"
              aria-current={view === 'inbox' ? 'page' : undefined}
              onClick={() => setView('inbox')}
            >
              <Inbox aria-hidden="true" size={20} />
              Inbox
            </button>
            <button
              type="button"
              className="navigation-item"
              aria-current={view === 'starred' ? 'page' : undefined}
              onClick={() => setView('starred')}
            >
              <Star aria-hidden="true" size={20} />
              Starred
            </button>
            <button
              type="button"
              className="navigation-item"
              aria-expanded={labelsExpanded}
              aria-controls="mail-labels"
              onClick={() => setLabelsExpanded((expanded) => !expanded)}
            >
              <Tag aria-hidden="true" size={20} />
              Labels
              <ChevronDown className="navigation-chevron" aria-hidden="true" size={16} />
            </button>
            {labelsExpanded && (
              <div className="label-navigation" id="mail-labels">
                {labels.map((label) => (
                  <button
                    type="button"
                    className="navigation-item label-item"
                    aria-current={view === `label:${label}` ? 'page' : undefined}
                    onClick={() => setView(`label:${label}`)}
                    key={label}
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </nav>
          <Separator />
          <div className="account-list" aria-label="Connected accounts">
            {accounts.map((account) => (
              <div className="account-row" key={account}>
                <label className="account-toggle">
                  <Checkbox
                    checked={activeAccounts.includes(account)}
                    onCheckedChange={(checked) =>
                      setActiveAccounts((current) =>
                        checked === true
                          ? [...current, account]
                          : current.filter((item) => item !== account),
                      )
                    }
                    aria-label={`Include ${account}`}
                  />
                  <span title={account}>{account}</span>
                </label>
                <Button
                  className="disconnect-button"
                  variant="link"
                  size="sm"
                  aria-label={`Disconnect ${account}`}
                  onClick={() => setNotice(`Disconnect ${account}`)}
                >
                  Disconnect
                </Button>
              </div>
            ))}
          </div>
        </aside>

        <section className="mail-panel" aria-label="Mail">
          <div className="mail-toolbar">
            <Checkbox
              checked={allSelected ? true : someSelected ? 'indeterminate' : false}
              onCheckedChange={(checked) =>
                setSelectedIds((current) =>
                  checked === true
                    ? [...new Set([...current, ...visibleMessages.map((message) => message.id)])]
                    : current.filter((id) => !visibleMessages.some((message) => message.id === id)),
                )
              }
              aria-label="Select all visible emails"
            />
            <Button
              variant="ghost"
              size="icon"
              aria-label="Refresh mail"
              onClick={() => setNotice('Refresh mail')}
            >
              <RefreshCw aria-hidden="true" size={20} />
            </Button>
            <div className="search-wrap">
              <Search aria-hidden="true" size={20} />
              <Input aria-label="Search mail" placeholder="Search mail" />
            </div>
          </div>

          <ScrollArea className="message-list">
            {visibleMessages.map((message) => (
                <div className="message-row" key={message.id}>
                  <div className="message-actions">
                    <Checkbox
                      checked={selectedIds.includes(message.id)}
                      onCheckedChange={(checked) =>
                        setSelectedIds((current) =>
                          checked === true
                            ? [...current, message.id]
                            : current.filter((id) => id !== message.id),
                        )
                      }
                      aria-label={`Select ${message.subject}`}
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className={message.starred ? 'marked-action' : undefined}
                      aria-label={`${message.starred ? 'Unstar' : 'Star'} ${message.subject}`}
                      onClick={() => setNotice(`${message.starred ? 'Unstar' : 'Star'} ${message.subject}`)}
                    >
                      <Star aria-hidden="true" size={16} fill={message.starred ? 'currentColor' : 'none'} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Labels for ${message.subject}: ${message.labels.join(', ')}`}
                      onClick={() => setNotice(`Label ${message.subject}`)}
                    >
                      <Tag aria-hidden="true" size={16} />
                    </Button>
                  </div>
                  <span className="sender">{message.sender}</span>
                  <span className="subject">{message.subject}</span>
                  <span className="account-chip">{message.account}</span>
                  <span className="time">{message.time}</span>
                </div>
            ))}
            {visibleMessages.length === 0 && (
              <p className="empty-message">No sample mail in this view.</p>
            )}
          </ScrollArea>
        </section>
      </section>

      <Dialog open={notice !== null} onOpenChange={(open) => !open && setNotice(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{notice}</DialogTitle>
            <DialogDescription>
              Gmail account and mail actions will be available when the backend is connected.
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </main>
  )
}

export default App
