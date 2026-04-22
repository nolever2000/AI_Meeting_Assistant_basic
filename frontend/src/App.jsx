import { useEffect, useMemo, useRef, useState } from 'react'
import ConversationTable from './components/ConversationTable'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [rows, setRows] = useState([])
  const [status, setStatus] = useState('connecting')
  const audioRef = useRef(null)

  useEffect(() => {
    fetch(`${API_URL}/history`)
      .then((r) => r.json())
      .then((history) => {
        const normalized = history.map((item) => ({
          source: item.source,
          original: item.original_text,
          translated: item.translated_text,
          timestamp: item.timestamp,
        }))
        setRows(normalized)
      })
      .catch(() => setStatus('api-unreachable'))
  }, [])

  useEffect(() => {
    const ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      setStatus('connected')
      ws.send('hello')
    }

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      setRows((prev) => [...prev, msg])
      if (msg.audio_base64) {
        const audio = audioRef.current
        audio.src = `data:audio/mp3;base64,${msg.audio_base64}`
        audio.play().catch(() => {})
      }
    }

    ws.onerror = () => setStatus('error')
    ws.onclose = () => setStatus('disconnected')

    return () => ws.close()
  }, [])

  const summary = useMemo(() => {
    const micCount = rows.filter((x) => x.source === 'mic').length
    const speakerCount = rows.filter((x) => x.source === 'speaker').length
    return { micCount, speakerCount }
  }, [rows])

  return (
    <main style={{ maxWidth: 1200, margin: '0 auto', padding: 20, fontFamily: 'Arial' }}>
      <h1>Realtime Bidirectional Speech Translation</h1>
      <p>
        WS status: <strong>{status}</strong> | mic messages: <strong>{summary.micCount}</strong> | speaker messages:{' '}
        <strong>{summary.speakerCount}</strong>
      </p>
      <audio ref={audioRef} hidden />
      <ConversationTable rows={rows} />
    </main>
  )
}
