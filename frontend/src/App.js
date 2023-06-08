import React, { useEffect, useState } from "react";
import ForceGraph3D from "react-force-graph-3d";

function App() {
  const [socket, setSocket] = useState(null);
  const [query, setQuery] = useState({
    courses: "",
    departments: "",
    show_direct_prerequisites: false,
    show_transitive_prerequisites: false,
    show_disconnected_courses: true,
  });

  const [graphData, setGraphData] = useState(null);

  useEffect(() => {
    // creates a new WebSocket connection
    const socket = new WebSocket("ws://localhost:3001");

    setSocket(socket);

    // event handlers for the WebSocket
    socket.onopen = () => {
      console.log("WebSocket connected opened");
    };

    socket.onmessage = (event) => {
      const msgData = JSON.parse(event.data);

      if (msgData?.type === "graph") {
        // Update graph data
        setGraphData(msgData.data);
      } else {
        console.log("Unknown message type", msgData);
      }
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    // closes the WebSocket connection when the component unmounts
    return () => {
      socket.close();
    };
  }, []);

  const sendQuery = () => {
    if (socket) {
      // Send message through the WebSocket connection
      socket.send(JSON.stringify({ type: "query", query: query }));
    }
  };

  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    let inputValue;

    if (type === "checkbox") {
      inputValue = checked;
    } else if (name === "courses" || name === "departments") {
      // Parse input values as arrays
      inputValue = value.split(",").map((item) => item.toUpperCase().trim());
    } else {
      inputValue = value;
    }

    setQuery((prevState) => ({
      ...prevState,
      [name]: inputValue,
    }));
  };

  return (
    <div className="App">
      {graphData ? (
        <ForceGraph3D
          graphData={graphData}
          nodeLabel={"id"}
          nodeAutoColorBy={"group"}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          controlType={"fly"}
        />
      ) : (
        <>
          <div>
            <div>
              <label htmlFor="courses">Courses:</label>
              <input
                type="text"
                id="courses"
                name="courses"
                value={query.courses}
                onChange={handleInputChange}
              />
            </div>

            <div>
              <label htmlFor="departments">Departments:</label>
              <input
                type="text"
                id="departments"
                name="departments"
                value={query.departments}
                onChange={handleInputChange}
              />
            </div>

            <div>
              <label htmlFor="show_direct_prerequisites">
                Show Direct Prerequisites:
              </label>
              <input
                type="checkbox"
                id="show_direct_prerequisites"
                name="show_direct_prerequisites"
                checked={query.show_direct_prerequisites}
                onChange={handleInputChange}
              />
            </div>

            <div>
              <label htmlFor="show_transitive_prerequisites">
                Show Transitive Prerequisites:
              </label>
              <input
                type="checkbox"
                id="show_transitive_prerequisites"
                name="show_transitive_prerequisites"
                checked={query.show_transitive_prerequisites}
                onChange={handleInputChange}
              />
            </div>

            <div>
              <label htmlFor="show_disconnected_courses">
                Show Disconnected Courses:
              </label>
              <input
                type="checkbox"
                id="show_disconnected_courses"
                name="show_disconnected_courses"
                checked={query.show_disconnected_courses}
                onChange={handleInputChange}
              />
            </div>
          </div>
          <button onClick={sendQuery}>Query</button>
        </>
      )}
    </div>
  );
}

export default App;
