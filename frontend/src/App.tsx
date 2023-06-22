import { useEffect, useState } from 'react'
import Graph from './ForceGraph'
import Sidebar from './Sidebar'
import { GraphData, Query, QueryForm } from './interfaces/index.ts'

export default function App () {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [queryForm, setQueryForm] = useState<QueryForm>({
    courses: 'CSE320',
    departments: '',
    show_direct_prerequisites: false,
    show_transitive_prerequisites: true,
    show_disconnected_courses: true
  })
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [focusControls, setFocusControls] = useState<boolean>(true)

  const computeQuery = (): Query => ({
    ...queryForm,
    courses: queryForm.courses.split(',').map((course) => `${course.slice(0, 3)} ${course.slice(3)}`),
    departments: queryForm.departments.split(',')
  })

  useEffect(() => {
    // creates a new WebSocket connection
    const socket: WebSocket = new WebSocket('ws://localhost:3003')

    setSocket(socket)

    // event handlers for the WebSocket
    socket.onopen = () => {
      console.log('WebSocket connection opened')
      sendQuery(socket)
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

  const sendQuery = (s: WebSocket | null = socket) => {
    if (s) {
      s.send(JSON.stringify({ type: 'query', query: computeQuery() })) // TODO: Remove
    } else {
      console.log('Failed to send message to socket:', s)
    }
  }

  const states = { socket, setSocket, queryForm, setQueryForm, graphData, setGraphData, focusControls, setFocusControls, sendQuery }

  return (
    <div className="App">
      <Sidebar {...states}/>
      <Graph graphData={graphData}/>
    </div>
  )
}
