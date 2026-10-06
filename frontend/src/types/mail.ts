export type MailMessage = {
  id: string
  account: string
  sender: string
  subject: string
  snippet: string
  received_at: string
  starred: boolean
}

export type Mailbox = {
  account: string
  labels: { id: string; name: string }[]
  messages: MailMessage[]
}

export type MessageDetail = MailMessage & { body: string }
