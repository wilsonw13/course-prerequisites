import { useEffect, useState } from 'react'
import Graph from './ForceGraph'
import Sidebar from './Sidebar'
import { GraphData, Query } from './interfaces/index.ts'

export default function App () {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [query, setQuery] = useState<Query>({
    courses: '',
    departments: 'CSE',
    show_direct_prerequisites: false,
    show_transitive_prerequisites: false,
    show_disconnected_courses: true
  })
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [focusControls, setFocusControls] = useState<boolean>(true)

  const states = { socket, setSocket, query, setQuery, graphData, setGraphData, focusControls, setFocusControls }

  useEffect(() => {
    // creates a new WebSocket connection
    const socket: WebSocket = new WebSocket('ws://localhost:3003')

    setSocket(socket)

    // event handlers for the WebSocket
    socket.onopen = () => {
      console.log('WebSocket connection opened')
      socket.send(JSON.stringify({ type: 'query', query })) // TODO: Remove
    }

    socket.onmessage = (event) => {
      const msgData = JSON.parse(event.data)

      if (msgData?.type === 'graph') {
        // Update graph data
        setGraphData(msgData.data)
      } else {
        console.log('Unknown message type', msgData)
      }
    }

    socket.onclose = () => {
      console.log('WebSocket connection closed')
    }

    // closes the WebSocket connection when the component unmounts
    return () => {
      socket.close()
    }
  }, [])

  return (
    <div className="App">
      <Sidebar {...states}/>
      <Graph graphData={graphData}/>
    </div>
  )
}
