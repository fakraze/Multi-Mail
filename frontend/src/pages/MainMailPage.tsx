import { useEffect, useRef, useState, type FormEvent } from 'react'
import { ArrowLeft, ChevronDown, ChevronLeft, ChevronRight, Inbox, Plus, RefreshCw, Search, Star, Tag, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import SearchHighlight from '@/components/SearchHighlight'
import { searchHighlightTerms } from '@/lib/searchHighlight'
import { createGmailLabel, deleteGmailLabel, fetchMailbox, fetchMessage, setMessageLabel, syncMailbox } from '@/services/mailbox'
import type { Mailbox, MailLabel, MailMessage, MessageDetail } from '@/types/mail'

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
  const [folder, setFolder] = useState('INBOX')
  const folderRef = useRef(folder)
  const [searchText, setSearchText] = useState('')
  const [activeQuery, setActiveQuery] = useState<string | null>(null)
  const [displayedQuery, setDisplayedQuery] = useState<string | null>(null)
  const [labelTarget, setLabelTarget] = useState<MailMessage | null>(null)
  const [createLabelOpen, setCreateLabelOpen] = useState(false)
  const [newLabelName, setNewLabelName] = useState('')
  const [createLabelError, setCreateLabelError] = useState<string | null>(null)
  const [creatingLabel, setCreatingLabel] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<MailLabel | null>(null)
  const [deletingLabel, setDeletingLabel] = useState(false)
  const [deleteLabelError, setDeleteLabelError] = useState<string | null>(null)
  const [busyMessageId, setBusyMessageId] = useState<string | null>(null)
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [accountEnabled, setAccountEnabled] = useState(true)
  const [labelsExpanded, setLabelsExpanded] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [messageLoading, setMessageLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [loadedPage, setLoadedPage] = useState(1)
  const [pageTokens, setPageTokens] = useState<(string | null)[]>([null])
  const [loadRevision, setLoadRevision] = useState(0)
  const [syncing, setSyncing] = useState(false)
  const [syncCycle, setSyncCycle] = useState(0)
  const syncTask = useRef<Promise<void> | null>(null)
  const requestedPageToken = pageTokens[page - 1] ?? undefined
  const viewKey = `${folder}:${activeQuery ?? ''}:${page}:${requestedPageToken ?? ''}`
  const viewKeyRef = useRef(viewKey)

  useEffect(() => { viewKeyRef.current = viewKey }, [viewKey])

  const visibleMessages = mailbox && accountEnabled ? mailbox.messages : []
  const highlightTerms = displayedQuery ? searchHighlightTerms(displayedQuery) : []
  const userLabels = mailbox?.labels.filter((label) => label.kind === 'user') ?? []
  const editableLabels = mailbox?.labels.filter((label) => label.modifiable) ?? []
  const appliedLabels = editableLabels.filter((label) => labelTarget?.label_ids.includes(label.id))
  const allSelected = visibleMessages.length > 0 && visibleMessages.every((item) => selectedIds.includes(item.id))
  const someSelected = visibleMessages.some((item) => selectedIds.includes(item.id))

  function reload() {
    setLoading(true)
    setError(null)
    setMessage(null)
    setSelectedIds([])
    setPage(1)
    setPageTokens([null])
    setLoadRevision((current) => current + 1)
  }

  async function refreshMail(manual: boolean) {
    if (!mailbox) return
    if (manual) {
      setSyncCycle((current) => current + 1)
      setSyncing(true)
    }
    if (syncTask.current) {
      try { await syncTask.current } finally { if (manual) setSyncing(false) }
      return
    }
    const originalView = viewKey
    const task = (async () => {
      try {
        await syncMailbox(activeQuery ? undefined : folder === 'INBOX' ? undefined : folder,
          activeQuery ?? undefined, requestedPageToken)
        if (viewKeyRef.current === originalView) {
          const result = await fetchMailbox(activeQuery ? undefined : folder === 'INBOX' ? undefined : folder,
            undefined, activeQuery ?? undefined, requestedPageToken)
          if (viewKeyRef.current === originalView) {
            setMailbox(result)
            setError(null)
          }
        }
      } catch (cause) {
        if (viewKeyRef.current === originalView) {
          setError(cause instanceof Error ? cause.message : 'Could not synchronize Gmail.')
        }
      }
    })()
    syncTask.current = task
    try { await task } finally {
      syncTask.current = null
      if (manual) setSyncing(false)
    }
  }

  useEffect(() => {
    const timer = window.setInterval(() => { void refreshMail(false) }, 60_000)
    return () => window.clearInterval(timer)
  // The timer resets on manual refresh and when the active mailbox view changes.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [syncCycle, viewKey, mailbox?.account])

  useEffect(() => {
    const controller = new AbortController()
    fetchMailbox(activeQuery ? undefined : folder === 'INBOX' ? undefined : folder,
      controller.signal, activeQuery ?? undefined, requestedPageToken)
      .then((result) => {
        if (controller.signal.aborted) return
        setMailbox(result)
        setDisplayedQuery(activeQuery)
        setLoadedPage(page)
        setError(null)
        setLoading(false)
      })
      .catch((cause: unknown) => {
        if (controller.signal.aborted) return
        setError(cause instanceof Error ? cause.message : 'Could not load Gmail.')
        setLoading(false)
      })
    return () => controller.abort()
  }, [folder, activeQuery, page, requestedPageToken, loadRevision])

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const query = searchText.trim() ? searchText : null
    setMessage(null)
    setSelectedIds([])
    setError(null)
    setLoading(true)
    if (query === activeQuery && (query !== null || folder === 'INBOX')) {
      reload()
      return
    }
    if (query === null) setFolder('INBOX')
    setActiveQuery(query)
    setPage(1)
    setPageTokens([null])
  }

  function selectFolder(nextFolder: string) {
    if (nextFolder === folder && activeQuery === null) {
      setMessage(null)
      setSelectedIds([])
      return
    }
    folderRef.current = nextFolder
    setFolder(nextFolder)
    setActiveQuery(null)
    setSearchText('')
    setMessage(null)
    setSelectedIds([])
    setError(null)
    setLoading(true)
    setPage(1)
    setPageTokens([null])
  }

  function changePage(nextPage: number) {
    if (loading || nextPage < 1 || nextPage > loadedPage + 1 ||
        (nextPage > loadedPage && !mailbox?.next_page_token)) return
    const nextToken = mailbox?.next_page_token
    if (nextPage > loadedPage && nextToken) {
      setPageTokens((current) => [...current.slice(0, loadedPage), nextToken])
    }
    setPage(nextPage)
    setMessage(null)
    setSelectedIds([])
    setError(null)
    setLoading(true)
  }

  async function changeLabel(item: MailMessage, labelId: string, present: boolean) {
    if (busyMessageId) return
    setBusyMessageId(item.id)
    setError(null)
    try {
      const result = await setMessageLabel(item.id, item.account, labelId, present)
      if (folderRef.current !== folder) return
      const update = <T extends MailMessage>(mail: T): T => mail.id === item.id
        ? { ...mail, label_ids: result.label_ids, starred: result.starred }
        : mail
      setMailbox((current) => current && {
        ...current,
        messages: current.messages.map(update).filter((mail) =>
          activeQuery !== null || folder === 'INBOX' || mail.label_ids.includes(folder)),
      })
      setMessage((current) => current ? update(current) : null)
      setLabelTarget((current) => current ? update(current) : null)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not change the Gmail label.')
    } finally {
      setBusyMessageId(null)
    }
  }

  async function submitNewLabel(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!mailbox || creatingLabel || !newLabelName.trim()) return
    setCreatingLabel(true)
    setCreateLabelError(null)
    try {
      const label = await createGmailLabel(mailbox.account, newLabelName.trim())
      setMailbox((current) => current && {
        ...current,
        labels: [...current.labels, label].sort((a, b) => a.name.localeCompare(b.name)),
      })
      setLabelsExpanded(true)
      setCreateLabelOpen(false)
      setNewLabelName('')
    } catch (cause) {
      setCreateLabelError(cause instanceof Error ? cause.message : 'Could not create the Gmail label.')
    } finally {
      setCreatingLabel(false)
    }
  }

  async function confirmDeleteLabel() {
    if (!mailbox || !deleteTarget || deletingLabel) return
    setDeletingLabel(true)
    setDeleteLabelError(null)
    try {
      await deleteGmailLabel(mailbox.account, deleteTarget.id)
      const deletedId = deleteTarget.id
      setMailbox((current) => current && {
        ...current,
        labels: current.labels.filter((label) => label.id !== deletedId),
        messages: current.messages.map((mail) => ({
          ...mail, label_ids: mail.label_ids.filter((id) => id !== deletedId),
        })),
      })
      setMessage((current) => current && {
        ...current, label_ids: current.label_ids.filter((id) => id !== deletedId),
      })
      if (folderRef.current === deletedId) selectFolder('INBOX')
      setDeleteTarget(null)
    } catch (cause) {
      setDeleteLabelError(cause instanceof Error ? cause.message : 'Could not delete the Gmail label.')
    } finally {
      setDeletingLabel(false)
    }
  }

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
          <h1><button type="button" className="mail-home-button" onClick={() => selectFolder('INBOX')}>Multi Mail</button></h1>
          <Button className="connect-button" onClick={onConnect}>Connect Gmail</Button>
          <nav className="mail-navigation" aria-label="Mail folders">
            <button type="button" className="navigation-item" aria-current={folder === 'INBOX' ? 'page' : undefined} onClick={() => selectFolder('INBOX')}>
              <Inbox aria-hidden="true" size={20} /> Inbox
            </button>
            <button type="button" className="navigation-item" aria-current={folder === 'STARRED' ? 'page' : undefined} onClick={() => selectFolder('STARRED')}>
              <Star aria-hidden="true" size={20} /> Starred
            </button>
            <button type="button" className="navigation-item" aria-current={folder === 'IMPORTANT' ? 'page' : undefined}
              onClick={() => selectFolder('IMPORTANT')}>
              <Tag aria-hidden="true" size={20} /> Important
            </button>
            <div className="label-navigation-heading">
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
              <Button variant="ghost" size="icon" className="label-create-button"
                aria-label="Create Gmail label" disabled={!mailbox}
                onClick={() => { setNewLabelName(''); setCreateLabelError(null); setCreateLabelOpen(true) }}>
                <Plus aria-hidden="true" size={16} />
              </Button>
            </div>
            {labelsExpanded && (
              <div className="label-navigation" id="mail-labels">
                {userLabels.map((label) => (
                  <div className="label-row" key={label.id}>
                    <button
                      type="button"
                      className="navigation-item label-item"
                      title={label.name}
                      aria-current={folder === label.id ? 'page' : undefined}
                      onClick={() => selectFolder(label.id)}
                    >
                      <span className="label-name">{label.name}</span>
                    </button>
                    {label.deletable && (
                      <Button variant="ghost" size="icon" className="label-delete-button"
                        aria-label={`Delete label ${label.name}`}
                        onClick={() => { setDeleteLabelError(null); setDeleteTarget(label) }}>
                        <Trash2 aria-hidden="true" size={16} />
                      </Button>
                    )}
                  </div>
                ))}
                {mailbox && userLabels.length === 0 && <span className="label-empty">No custom labels</span>}
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
            <Button variant="ghost" size="icon" aria-label="Refresh mail" disabled={loading || syncing} onClick={() => void refreshMail(true)}>
              <RefreshCw aria-hidden="true" size={20} />
            </Button>
            {(syncing || loading && mailbox) && <span className="sync-status" role="status">Loading</span>}
            <form className="search-wrap" role="search" onSubmit={submitSearch}>
              <button type="submit" aria-label="Search mail" disabled={!accountEnabled || loading}>
                <Search aria-hidden="true" size={20} />
              </button>
              <Input
                aria-label="Search Gmail"
                placeholder="Search mail"
                value={searchText}
                onChange={(event) => setSearchText(event.target.value)}
                disabled={!accountEnabled}
              />
            </form>
          </div>


          <ScrollArea className="message-list">
            {loading && !mailbox && <p className="empty-message" role="status">Loading Gmail mail…</p>}
            {error && <p className="empty-message error-message" role="alert">{error}</p>}
            {!loading && !mailbox && !error && (
              <div className="empty-message"><p>Connect Gmail to see your inbox.</p><Button onClick={onConnect}>Connect Gmail</Button></div>
            )}
            {mailbox && !message && visibleMessages.length === 0 && (
              <p className="empty-message">{!accountEnabled ? 'Select the account to show its mail.' : activeQuery ? 'No messages match this search.' : 'No messages in this view.'}</p>
            )}
            {!message && visibleMessages.map((item) => (
              <div className="message-row live-message-row" key={item.id}>
                <div className="message-actions">
                  <Checkbox
                    checked={selectedIds.includes(item.id)}
                    disabled={loading}
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
                    disabled={loading || busyMessageId !== null || !item.label_ids.includes('INBOX')}
                    onClick={() => void changeLabel(item, 'STARRED', !item.starred)}
                  >
                    <Star aria-hidden="true" size={16} fill={item.starred ? 'currentColor' : 'none'} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Labels for ${item.subject}`}
                    disabled={loading || busyMessageId !== null || !item.label_ids.includes('INBOX')}
                    onClick={() => setLabelTarget(item)}
                  >
                    <Tag aria-hidden="true" size={16} />
                  </Button>
                </div>
                <button type="button" className="message-open sender" disabled={loading} onClick={() => void openMessage(item.id)}>
                  <SearchHighlight text={item.sender} terms={highlightTerms} />
                </button>
                <button type="button" className="message-open message-copy" disabled={loading} onClick={() => void openMessage(item.id)}>
                  <span className="subject"><SearchHighlight text={item.subject} terms={highlightTerms} /></span>
                  <span className="snippet"><SearchHighlight text={item.snippet} terms={highlightTerms} /></span>
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
                <div className="detail-actions">
                  <Button variant="ghost" size="sm" disabled={busyMessageId !== null || !message.label_ids.includes('INBOX')}
                    onClick={() => void changeLabel(message, 'STARRED', !message.starred)}>
                    <Star aria-hidden="true" size={16} fill={message.starred ? 'currentColor' : 'none'} />
                    {message.starred ? 'Unstar' : 'Star'}
                  </Button>
                  <Button variant="ghost" size="sm" disabled={busyMessageId !== null || !message.label_ids.includes('INBOX')}
                    onClick={() => setLabelTarget(message)}>
                    <Tag aria-hidden="true" size={16} /> Labels
                  </Button>
                </div>
                <p className="message-meta">From: {message.sender}</p>
                <p className="message-meta">Account: {message.account}</p>
                <time className="message-meta" dateTime={message.received_at}>{formatTime(message.received_at)}</time>
                <pre className="message-body">{message.body}</pre>
              </article>
            )}
          </ScrollArea>
          {mailbox && accountEnabled && !message && (
            <nav className="mail-pagination" aria-label="Mail pages">
              <Button variant="ghost" size="icon" aria-label="Previous page"
                disabled={loading || loadedPage === 1}
                onClick={() => changePage(loadedPage - 1)}>
                <ChevronLeft aria-hidden="true" size={20} />
              </Button>
              <span aria-current="page">{loadedPage}</span>
              <Button variant="ghost" size="icon" aria-label="Next page"
                disabled={loading || !mailbox.next_page_token}
                onClick={() => changePage(loadedPage + 1)}>
                <ChevronRight aria-hidden="true" size={20} />
              </Button>
            </nav>
          )}
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
      <Dialog open={labelTarget !== null} onOpenChange={(open) => !open && setLabelTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Labels for {labelTarget?.subject}</DialogTitle>
            <DialogDescription>Select labels to add or remove in Gmail.</DialogDescription>
          </DialogHeader>
          {error && <p className="error-message" role="alert">{error}</p>}
          {labelTarget && appliedLabels.length === 0 && <p>No labels applied.</p>}
          <div className="label-options">
            {editableLabels.map((label) => (
              <label className="label-option" key={label.id}>
                <Checkbox
                  checked={labelTarget?.label_ids.includes(label.id) ?? false}
                  disabled={busyMessageId !== null}
                  onCheckedChange={(checked) => {
                    if (labelTarget) void changeLabel(labelTarget, label.id, checked === true)
                  }}
                />
                <span>{label.name}</span>
              </label>
            ))}
            {editableLabels.length === 0 && <p>No editable Gmail labels.</p>}
          </div>
        </DialogContent>
      </Dialog>
      <Dialog open={createLabelOpen} onOpenChange={(open) => !open && !creatingLabel && setCreateLabelOpen(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Gmail label</DialogTitle>
            <DialogDescription>The new label will be available in Gmail and in this sidebar.</DialogDescription>
          </DialogHeader>
          <form className="create-label-form" onSubmit={(event) => void submitNewLabel(event)}>
            <Input aria-label="New label name" placeholder="Label name" value={newLabelName}
              maxLength={225} disabled={creatingLabel}
              onChange={(event) => setNewLabelName(event.target.value)} />
            {createLabelError && <p className="error-message" role="alert">{createLabelError}</p>}
            <Button type="submit" disabled={creatingLabel || !newLabelName.trim()}>
              {creatingLabel ? 'Creating…' : 'Create label'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
      <Dialog open={deleteTarget !== null} onOpenChange={(open) => !open && !deletingLabel && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete label {deleteTarget?.name}?</DialogTitle>
            <DialogDescription>
              This removes the label from Gmail and from every message that uses it. Messages will not be deleted.
            </DialogDescription>
          </DialogHeader>
          {deleteLabelError && <p className="error-message" role="alert">{deleteLabelError}</p>}
          <div className="label-delete-actions">
            <Button variant="outline" disabled={deletingLabel} onClick={() => setDeleteTarget(null)}>Cancel</Button>
            <Button variant="outline" className="label-delete-confirm" disabled={deletingLabel} onClick={() => void confirmDeleteLabel()}>
              {deletingLabel ? 'Deleting…' : 'Delete label'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  )
}

export default MainMailPage
