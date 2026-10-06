import type { Mailbox, MailMessage, MessageDetail } from '@/types/mail'

const backendBaseUrl = (import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isMessage(value: unknown): value is MailMessage {
  return isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.account === 'string' &&
    typeof value.sender === 'string' &&
    typeof value.subject === 'string' &&
    typeof value.snippet === 'string' &&
    typeof value.received_at === 'string' &&
    typeof value.starred === 'boolean'
}

async function request(path: string, signal?: AbortSignal): Promise<unknown> {
  let response: Response
  try {
    response = await fetch(`${backendBaseUrl}${path}`, { signal, headers: { Accept: 'application/json' } })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    throw new Error('Cannot reach the mail backend. Check that it is running.', { cause: error })
  }
  const data: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = isRecord(data) && typeof data.detail === 'string' ? data.detail : 'Gmail request failed.'
    throw new Error(detail)
  }
  return data
}

export async function fetchMailbox(signal?: AbortSignal): Promise<Mailbox> {
  const data = await request('/api/mailbox', signal)
  if (!isRecord(data) || typeof data.account !== 'string' ||
    !Array.isArray(data.labels) || !data.labels.every((label: unknown) =>
      isRecord(label) && typeof label.id === 'string' && typeof label.name === 'string') ||
    !Array.isArray(data.messages) || !data.messages.every(isMessage)) {
    throw new Error('The mail backend returned invalid inbox data.')
  }
  return { account: data.account, labels: data.labels, messages: data.messages }
}

export async function fetchMessage(messageId: string, signal?: AbortSignal): Promise<MessageDetail> {
  const data = await request(`/api/messages/${encodeURIComponent(messageId)}`, signal)
  const body = isRecord(data) ? data.body : undefined
  if (!isMessage(data) || typeof body !== 'string') {
    throw new Error('The mail backend returned invalid message data.')
  }
  return { ...data, body }
}
