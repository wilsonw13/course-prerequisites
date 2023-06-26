import asyncio
from websockets.server import serve
import threading
import subprocess
import os
import json

from main import query_prerequisite_graph

with open("config.json", "r") as f:
    config = json.load(f)
    host, port = config["ws_host"], config["ws_port"]
    assert host and port, "Failed to load host and port from config.json!"


def test():
    print("Running subprocess...")
    subprocess.run(f"py -m da --rules src/test.da",
                   env={**os.environ, "PYTHONPATH": "src:da:ps"}
                   )


async def handler(websocket):
    async for message in websocket:
        # parses the message into a dictionary
        msgData = json.loads(message)

        # checks the type of message
        if msgData.get("type") == "query":

            # queries the graph and sends the response back to the client
            response = query_prerequisite_graph(**msgData["query"])
            await websocket.send(json.dumps({"type": "graph", "data": response}))

        else:
            print("Received unknown message type: ")
            print(msgData)


async def main():
    async with serve(handler, host, port):
        print(
            f"Server running at ws://{host}:{port}")

        # start the test thread
        test_thread = threading.Thread(target=test)
        test_thread.start()

        await asyncio.Future()  # run forever

asyncio.run(main())
