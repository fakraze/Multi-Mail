export type MailMessage = {
  id: string
  account: string
  sender: string
  subject: string
  snippet: string
  received_at: string
  starred: boolean
  label_ids: string[]
}

export type MailLabel = {
  id: string
  name: string
  kind: 'user' | 'system'
  modifiable: boolean
  deletable: boolean
}

export type Mailbox = {
  account: string
  labels: MailLabel[]
  messages: MailMessage[]
  next_page_token: string | null
}

export type MessageDetail = MailMessage & { body: string }

export type MessageLabels = Pick<MailMessage, 'id' | 'account' | 'label_ids' | 'starred'>
