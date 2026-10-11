export type HighlightSegment = { text: string; highlighted: boolean }

export function searchHighlightTerms(query: string): string[] {
  const tokens = query.match(/(?:[^\s"]+:)?(?:"[^"]+"|\S+)/g) ?? []
  const terms: string[] = []

  for (const token of tokens) {
    let value = token.replace(/^[({]+|[)}]+$/g, '')
    if (value.startsWith('-') || /^(OR|AND)$/i.test(value)) continue

    const separator = value.indexOf(':')
    if (separator > 0 && /^[a-z_]+$/i.test(value.slice(0, separator))) {
      const field = value.slice(0, separator).toLowerCase()
      if (field !== 'from' && field !== 'subject') continue
      value = value.slice(separator + 1)
    }

    value = value.replace(/^"|"$/g, '').trim()
    if (value && !terms.some((term) => term.toLocaleLowerCase() === value.toLocaleLowerCase())) {
      terms.push(value)
    }
  }

  return terms.sort((a, b) => b.length - a.length)
}

export function highlightSegments(text: string, terms: string[]): HighlightSegment[] {
  if (!terms.length) return [{ text, highlighted: false }]
  const pattern = terms.map((term) => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')
  const matches = new RegExp(pattern, 'gi')
  const segments: HighlightSegment[] = []
  let position = 0

  for (const match of text.matchAll(matches)) {
    const start = match.index
    if (start > position) segments.push({ text: text.slice(position, start), highlighted: false })
    segments.push({ text: match[0], highlighted: true })
    position = start + match[0].length
  }
  if (position < text.length) segments.push({ text: text.slice(position), highlighted: false })
  return segments.length ? segments : [{ text, highlighted: false }]
}
