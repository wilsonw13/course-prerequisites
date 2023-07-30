# Course Prerequisites

![All UG Course Data](/docs/images/full-graph.png)

## About

This is a fullstack web application that allows users to search for courses at Stony Brook University (SBU) and view their prerequisites with a [3D Force Graph](https://github.com/vasturiano/react-force-graph). The web client is built in React.js while the backend websocket server, and web scraper is built in Python. The course data is scraped from SBU's [Undergraduate Course Bulletin](https://www.stonybrook.edu/sb/bulletin/current).

## Documentation

Documentation that explains the entire design and specifics of the application can be found [here](/docs/docs.md).

## Local Installation (on Windows)

### Clone the Repository

```bash
git clone https://github.com/wilsonw13/course-prerequisites
```

### Python Backend

1. Install [Python 3.7](https://www.python.org/downloads/)
2. Install [XSB](https://sourceforge.net/projects/xsb/)
3. Add both Python, pip, and XSB to your PATH and restart your terminal/editor:
    - Python: `C:\Users\{USERNAME}\AppData\Local\Programs\Python\Python37\`
    - pip: `C:\Users\{USERNAME}\AppData\Local\Programs\Python\Python37\Scripts`
    - XSB: `C:\Program Files (x86)\XSB\config\x64-pc-windows\bin`

4. Change directory to the `backend` folder, create and activate a virtual environment, and install the required packages:

    ```bash
    cd backend
    py -3.7 -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

### React Frontend

1. Install [Node.js v18+](https://nodejs.org/en/download/)
2. Change directory to the `frontend` folder, install yarn, and install the required packages:

    ```bash
    cd frontend
    npm install yarn -g
    yarn
    ```

### Running the Application

Run the backend websocket server and the frontend react server in separate terminals. The frontend react server will automatically open a browser window to the application.

```bash
# Terminal 1
cd backend
venv\Scripts\activate
py -m da --rules src/ws_server.da
```

```bash
# Terminal 2
cd frontend
yarn dev
```

***Note: If you want to run the web scraper again, run `py src/web_scrape.py` in the backend folder and it will regenerate `full_graph.json` within the `json` folder.
