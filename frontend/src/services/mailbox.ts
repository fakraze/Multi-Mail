import type { Mailbox, MailLabel, MailMessage, MessageDetail, MessageLabels } from '@/types/mail'

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
    typeof value.starred === 'boolean' &&
    Array.isArray(value.label_ids) && value.label_ids.every((id: unknown) => typeof id === 'string')
}

async function request(path: string, signal?: AbortSignal, body?: object, method?: 'PATCH' | 'POST' | 'DELETE'): Promise<unknown> {
  let response: Response
  try {
    response = await fetch(`${backendBaseUrl}${path}`, {
      signal,
      method: method ?? (body ? 'PATCH' : 'GET'),
      headers: { Accept: 'application/json', ...(body ? { 'Content-Type': 'application/json' } : {}) },
      body: body ? JSON.stringify(body) : undefined,
    })
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

export async function fetchMailbox(labelId?: string, signal?: AbortSignal): Promise<Mailbox> {
  const path = labelId ? `/api/mailbox?label_id=${encodeURIComponent(labelId)}` : '/api/mailbox'
  const data = await request(path, signal)
  if (!isRecord(data) || typeof data.account !== 'string' ||
    !Array.isArray(data.labels) || !data.labels.every((label: unknown) =>
      isRecord(label) && typeof label.id === 'string' && typeof label.name === 'string' &&
      (label.kind === 'user' || label.kind === 'system') &&
      typeof label.modifiable === 'boolean' && typeof label.deletable === 'boolean') ||
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

export async function setMessageLabel(
  messageId: string, account: string, labelId: string, present: boolean,
): Promise<MessageLabels> {
  const data = await request(`/api/messages/${encodeURIComponent(messageId)}/labels`, undefined, {
    account, label_id: labelId, present,
  })
  if (!isRecord(data) || data.id !== messageId || data.account !== account ||
    typeof data.starred !== 'boolean' || !Array.isArray(data.label_ids) ||
    !data.label_ids.every((id: unknown) => typeof id === 'string')) {
    throw new Error('The mail backend returned invalid label data.')
  }
  return { id: messageId, account, starred: data.starred, label_ids: data.label_ids }
}

export async function createGmailLabel(account: string, name: string): Promise<MailLabel> {
  const data = await request('/api/labels', undefined, { account, name }, 'POST')
  if (!isRecord(data) || typeof data.id !== 'string' || typeof data.name !== 'string' ||
    data.kind !== 'user' || data.modifiable !== true || data.deletable !== true) {
    throw new Error('The mail backend returned invalid label data.')
  }
  return { id: data.id, name: data.name, kind: 'user', modifiable: true, deletable: true }
}

export async function deleteGmailLabel(account: string, labelId: string): Promise<void> {
  await request(`/api/labels/${encodeURIComponent(labelId)}?account=${encodeURIComponent(account)}`, undefined, undefined, 'DELETE')
}
