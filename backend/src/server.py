import asyncio
from websockets.server import serve
import json

from main import query_prerequisite_graph

url = "localhost"
port = 3001


async def handler(websocket):
    async for message in websocket:
        # parses the message into a dictionary
        msgData = json.loads(message)

        # checks the type of message
        if msgData["type"] == "query":

            # queries the graph and sends the response back to the client
            response = query_prerequisite_graph(**msgData["query"])
            await websocket.send(json.dumps({"type": "graph", "data": response}))


async def main():
    async with serve(handler, url, port):
        print(f"Server running at http://{url}:{port}")
        await asyncio.Future()  # run forever

asyncio.run(main())
