import { useEffect, useState } from 'react'
import Graph from './ForceGraph/index.tsx'
import Sidebar from './Sidebar/index.tsx'
import { GraphData, Query, QueryOption } from './interfaces/index.ts'

export default function ForceGraph3DPage () {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [queryOptions, setQueryOptions] = useState<QueryOption[]>([])
  const [query, setQuery] = useState<Query | null>(null)
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [focusControls, setFocusControls] = useState<boolean>(true)

  useEffect(() => {
    // creates a new WebSocket connection
    const socket: WebSocket = new WebSocket('ws://localhost:3003')

    socket.onopen = () => {
      console.log('WebSocket connection opened')
      setSocket(socket)
    }

    // receives messages from the server
    socket.onmessage = (event) => {
      const msgObj = JSON.parse(event.data)
      const { type, data } = msgObj

      console.log('Received Message:', msgObj)

      switch (type) {
        case 'graph':
          // Update graph data
          setGraphData(data)
          break

        case 'query_options':
          // Update query options
          setQueryOptions(data)
          break

        default:
          console.log('Unknown message type', msgObj)
      }
    }

    socket.onclose = () => { console.log('WebSocket connection closed') }

    // closes the WebSocket connection when the component unmounts
    return () => {
      socket.close()
    }
  }, [])

  const sendQuery = (s: WebSocket | null = socket, q: Query | null = query) => {
    if (s) {
      s.send(JSON.stringify({ type: 'query', data: q }))
    } else {
      console.log('Failed to send message to socket:', s)
    }
  }

  const states = { socket, setSocket, queryOptions, setQueryOptions, query, setQuery, graphData, setGraphData, focusControls, setFocusControls, sendQuery }

  return (
    <div className="App">
      <Sidebar {...states}/>
      <Graph graphData={graphData}/>
    </div>
  )
}
