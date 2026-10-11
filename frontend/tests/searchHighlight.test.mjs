import assert from 'node:assert/strict'
import test from 'node:test'

import { highlightSegments, searchHighlightTerms } from '../src/lib/searchHighlight.ts'

test('extracts visible search words and whole quoted phrases without filter operators', () => {
  assert.deepEqual(
    searchHighlightTerms('from:Alice subject:"Quarterly Report" after:2026/01/01 in:inbox project OR -draft'),
    ['Quarterly Report', 'project', 'Alice'],
  )
})

test('highlights every visible match without changing the original text', () => {
  assert.deepEqual(highlightSegments('Alice sent a report to ALICE', ['Alice']), [
    { text: 'Alice', highlighted: true },
    { text: ' sent a report to ', highlighted: false },
    { text: 'ALICE', highlighted: true },
  ])
})

test('treats punctuation in query terms as literal text', () => {
  assert.deepEqual(highlightSegments('a+b a.b', ['a+b', 'a.b']), [
    { text: 'a+b', highlighted: true },
    { text: ' ', highlighted: false },
    { text: 'a.b', highlighted: true },
  ])
  assert.deepEqual(highlightSegments('Inbox', []), [{ text: 'Inbox', highlighted: false }])
})
