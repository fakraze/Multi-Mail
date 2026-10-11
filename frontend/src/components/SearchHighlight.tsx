import { highlightSegments } from '@/lib/searchHighlight'

function SearchHighlight({ text, terms }: { text: string; terms: string[] }) {
  return <>{highlightSegments(text, terms).map((segment, index) => segment.highlighted
    ? <mark className="search-highlight" key={index}>{segment.text}</mark>
    : segment.text)}</>
}

export default SearchHighlight
