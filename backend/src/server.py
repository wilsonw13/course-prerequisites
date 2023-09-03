import asyncio
import websockets
import json

from file_utils import get_config, get_from_json_dir, write_to_json_dir

config = get_config()
host, port = config["ws_host"], config["ws_port"]
assert host and port, "Failed to load host and port from config.json!"


query_connection = None
clients = {}


async def handler(websocket):
    global query_connection

    # sets the query connection to the first client that connects
    if not query_connection:
        query_connection = websocket

        async for message in websocket:
            # parses the message into a dictionary
            msg_dict = json.loads(message)

            if msg_dict.get("type") == "graph":
                client_id = msg_dict.pop("client_id", None)
                assert client_id, "No client id provided from query!"

                print(f"Sending graph data to client {client_id}")

                # sends the graph data to the client
                await clients[client_id].send(json.dumps(msg_dict))

    # otherwise, it is a client
    else:
        # get a unique id for the client
        client_id = id(websocket)
        clients[client_id] = websocket
        print(f"Client {client_id} connected")

        # send the client the default query options
        await websocket.send(json.dumps(
            {"type": "query_options", "data": get_from_json_dir("query_options.json")}))

        try:
            async for message in websocket:
                # parses the message into a dictionary
                msg_dict = json.loads(message)
                print(msg_dict)

                # checks the type of message
                if msg_dict.get("type") == "query":
                    options = msg_dict["data"]

                    # parses specific query options into a list and cleans it up
                    # creates a list of courses from the string of courses
                    options["courses"] = [
                        f"{c[:3].upper()} {c[-3:]}"
                        for c in options["courses"].replace(" ", "").split(",")
                        if c.strip()
                    ]

                    # creates a list of departments from the string of departments
                    options["departments"] = [
                        code.upper()
                        for code in options["departments"].replace(" ", "").split(",")
                        if code.strip()
                    ]

                    # print(options)

                    # send the query object to the query connection
                    await query_connection.send(json.dumps({
                        "type": "query", "data": options, "client_id": client_id
                    }))

                else:
                    print(
                        f"Received unknown message type: {msg_dict.get('type')}")
                    print(msg_dict)

                    # query_connection = await asyncio.create_subprocess_exec(
                    #     "python", "-m", "backend.src.ws_server", stdout=asyncio.subprocess.PIPE)
        finally:
            clients.pop(client_id)
            print(f"Client {client_id} disconnected")


async def main():
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # run forever
