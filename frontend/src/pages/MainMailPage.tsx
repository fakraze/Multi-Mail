import { useEffect, useState } from 'react'
import { ArrowLeft, ChevronDown, Inbox, RefreshCw, Search, Star, Tag } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { fetchMailbox, fetchMessage } from '@/services/mailbox'
import type { Mailbox, MessageDetail } from '@/types/mail'

import '../App.css'

function formatTime(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleString()
}

function formatListTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const today = new Date()
  const isToday = date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() && date.getDate() === today.getDate()
  return isToday
    ? date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
    : date.toLocaleDateString()
}

function MainMailPage({ onConnect }: { onConnect: () => void }) {
  const [mailbox, setMailbox] = useState<Mailbox | null>(null)
  const [message, setMessage] = useState<MessageDetail | null>(null)
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [accountEnabled, setAccountEnabled] = useState(true)
  const [labelsExpanded, setLabelsExpanded] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [messageLoading, setMessageLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const visibleMessages = mailbox && accountEnabled ? mailbox.messages : []
  const allSelected = visibleMessages.length > 0 && visibleMessages.every((item) => selectedIds.includes(item.id))
  const someSelected = visibleMessages.some((item) => selectedIds.includes(item.id))

  async function reload() {
    setLoading(true)
    setError(null)
    try {
      setMailbox(await fetchMailbox())
      setMessage(null)
      setSelectedIds([])
    } catch (cause) {
      setMailbox(null)
      setError(cause instanceof Error ? cause.message : 'Could not load Gmail.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const controller = new AbortController()
    fetchMailbox(controller.signal)
      .then((result) => {
        setMailbox(result)
        setLoading(false)
      })
      .catch((cause: unknown) => {
        if (controller.signal.aborted) return
        setError(cause instanceof Error ? cause.message : 'Could not load Gmail.')
        setLoading(false)
      })
    return () => controller.abort()
  }, [])

  async function openMessage(messageId: string) {
    setMessageLoading(true)
    setError(null)
    try {
      setMessage(await fetchMessage(messageId))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not open the message.')
    } finally {
      setMessageLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="mail-frame" aria-label="Main mail page">
        <aside className="mail-sidebar">
          <h1>Multi Mail</h1>
          <Button className="connect-button" onClick={onConnect}>Connect Gmail</Button>
          <nav className="mail-navigation" aria-label="Mail folders">
            <button type="button" className="navigation-item" aria-current="page" onClick={() => setMessage(null)}>
              <Inbox aria-hidden="true" size={20} /> Inbox
            </button>
            <button type="button" className="navigation-item" onClick={() => setNotice('Starred mail')}>
              <Star aria-hidden="true" size={20} /> Starred
            </button>
            <button
              type="button"
              className="navigation-item"
              aria-expanded={labelsExpanded}
              aria-controls="mail-labels"
              onClick={() => setLabelsExpanded((expanded) => !expanded)}
            >
              <Tag aria-hidden="true" size={20} /> Labels
              <ChevronDown className="navigation-chevron" aria-hidden="true" size={16} />
            </button>
            {labelsExpanded && (
              <div className="label-navigation" id="mail-labels">
                {mailbox?.labels.map((label) => (
                  <button
                    type="button"
                    className="navigation-item label-item"
                    key={label.id}
                    title={label.name}
                    onClick={() => setNotice(`Label: ${label.name}`)}
                  >
                    <span className="label-name">{label.name}</span>
                  </button>
                ))}
                {mailbox && mailbox.labels.length === 0 && <span className="label-empty">No Gmail labels</span>}
              </div>
            )}
          </nav>
          <Separator />
          <div className="account-list" aria-label="Connected accounts">
            {mailbox && (
              <div className="account-row">
                <label className="account-toggle">
                  <Checkbox
                    checked={accountEnabled}
                    onCheckedChange={(checked) => {
                      setAccountEnabled(checked === true)
                      if (checked !== true) setMessage(null)
                    }}
                    aria-label={`Include ${mailbox.account}`}
                  />
                  <span title={mailbox.account}>{mailbox.account}</span>
                </label>
                <Button
                  className="disconnect-button"
                  variant="link"
                  size="sm"
                  aria-label={`Disconnect ${mailbox.account}`}
                  onClick={() => setNotice(`Disconnect ${mailbox.account}`)}
                >
                  Disconnect
                </Button>
              </div>
            )}
          </div>
        </aside>

        <section className="mail-panel" aria-label="Mail">
          <div className="mail-toolbar">
            {message ? (
              <Button variant="ghost" size="icon" aria-label="Back to inbox" onClick={() => setMessage(null)}>
                <ArrowLeft aria-hidden="true" size={20} />
              </Button>
            ) : (
              <Checkbox
                checked={allSelected ? true : someSelected ? 'indeterminate' : false}
                onCheckedChange={(checked) =>
                  setSelectedIds((current) => checked === true
                    ? [...new Set([...current, ...visibleMessages.map((item) => item.id)])]
                    : current.filter((id) => !visibleMessages.some((item) => item.id === id)))
                }
                aria-label="Select all visible emails"
              />
            )}
            <Button variant="ghost" size="icon" aria-label="Refresh mail" disabled={loading} onClick={() => void reload()}>
              <RefreshCw aria-hidden="true" size={20} />
            </Button>
            <div className="search-wrap">
              <Search aria-hidden="true" size={20} />
              <Input
                aria-label="Search mail"
                placeholder="Search mail"
                onKeyDown={(event) => {
                  if (event.key === 'Enter') setNotice('Search mail')
                }}
              />
            </div>
          </div>

          <ScrollArea className="message-list">
            {loading && <p className="empty-message" role="status">Loading Gmail inbox…</p>}
            {error && <p className="empty-message error-message" role="alert">{error}</p>}
            {!loading && !mailbox && (
              <div className="empty-message"><p>Connect Gmail to see your inbox.</p><Button onClick={onConnect}>Connect Gmail</Button></div>
            )}
            {!loading && mailbox && !message && visibleMessages.length === 0 && (
              <p className="empty-message">{accountEnabled ? 'This Gmail inbox is empty.' : 'Select the account to show its mail.'}</p>
            )}
            {!loading && !message && visibleMessages.map((item) => (
              <div className="message-row live-message-row" key={item.id}>
                <div className="message-actions">
                  <Checkbox
                    checked={selectedIds.includes(item.id)}
                    onCheckedChange={(checked) => setSelectedIds((current) => checked === true
                      ? [...new Set([...current, item.id])]
                      : current.filter((id) => id !== item.id))}
                    aria-label={`Select ${item.subject}`}
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    className={item.starred ? 'marked-action' : undefined}
                    aria-label={`${item.starred ? 'Unstar' : 'Star'} ${item.subject}`}
                    onClick={() => setNotice(`${item.starred ? 'Unstar' : 'Star'} ${item.subject}`)}
                  >
                    <Star aria-hidden="true" size={16} fill={item.starred ? 'currentColor' : 'none'} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Labels for ${item.subject}`}
                    onClick={() => setNotice(`Labels for ${item.subject}`)}
                  >
                    <Tag aria-hidden="true" size={16} />
                  </Button>
                </div>
                <button type="button" className="message-open sender" onClick={() => void openMessage(item.id)}>{item.sender}</button>
                <button type="button" className="message-open message-copy" onClick={() => void openMessage(item.id)}>
                  <span className="subject">{item.subject}</span>
                  <span className="snippet">{item.snippet}</span>
                </button>
                <span className="account-chip" title={item.account}>{item.account.split('@', 1)[0]}</span>
                <time className="time" dateTime={item.received_at} title={formatTime(item.received_at)}>
                  {formatListTime(item.received_at)}
                </time>
              </div>
            ))}
            {messageLoading && <p className="empty-message" role="status">Opening message…</p>}
            {message && !messageLoading && (
              <article className="message-detail">
                <h2>{message.subject}</h2>
                <p className="message-meta">From: {message.sender}</p>
                <p className="message-meta">Account: {message.account}</p>
                <time className="message-meta" dateTime={message.received_at}>{formatTime(message.received_at)}</time>
                <pre className="message-body">{message.body}</pre>
              </article>
            )}
          </ScrollArea>
        </section>
      </section>

      <Dialog open={notice !== null} onOpenChange={(open) => !open && setNotice(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{notice}</DialogTitle>
            <DialogDescription>This action is not connected to Gmail yet. No Gmail data was changed.</DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </main>
  )
}

export default MainMailPage
