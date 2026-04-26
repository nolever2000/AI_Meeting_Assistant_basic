export default function ConversationTable({ rows }) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr>
          <th style={cellStyle}>Time (UTC)</th>
          <th style={cellStyle}>Source</th>
          <th style={cellStyle}>Original</th>
          <th style={cellStyle}>Translated</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, idx) => (
          <tr key={`${row.timestamp}-${idx}`}>
            <td style={cellStyle}>{new Date(row.timestamp).toLocaleString()}</td>
            <td style={cellStyle}>{row.source}</td>
            <td style={cellStyle}>{row.original}</td>
            <td style={cellStyle}>{row.translated}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

const cellStyle = {
  border: '1px solid #ddd',
  padding: '8px',
  textAlign: 'left',
  verticalAlign: 'top',
}
