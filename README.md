# Visual-Sound-Hud-Even-Realities-G2

> A real-time audio classification and visual feedback system. This project listens to the environment and translates sounds into immediate visual cues, projecting them directly onto Even Realities G2 smart glasses while simultaneously updating a companion app.

---

## Disclaimer

> **Not a Safety Device:** This software is an experimental prototype intended for educational and accessibility exploration. It is not a certified medical device or a reliable safety mechanism. Do not rely on this application for emergency alerts (e.g., fire alarms, sirens, or approaching vehicles). The developer assumes no liability for missed audio events, false positives, or any resulting damages or injuries. **Always use dedicated, certified alerting devices for personal safety.**

---

## Features

* **Real-Time ML Inference:** Utilises TensorFlow and the YAMNet model to classify over 500 different environmental sounds with zero delay.
* **Smart Glasses HUD Integration:** Leverages the Even Hub SDK to push low-latency text and ASCII-art alerts directly to the user's field of vision.
* **Companion UI:** A fully responsive, dark-mode web application featuring animated visualisers, deep gradients, and contextual Material Icons.
* **"Lock-On" Debouncing System:** Intelligent backend logic that prevents UI flickering by holding high-confidence sounds on screen and filtering out background noise.
* **Emergency Alerting:** Distinct visual warnings for high-priority sounds like alarms, sirens, smoke detectors, and glass shattering. *(Please see the disclaimer above).*

---

## Architecture

The project is split into two primary components communicating over WebSockets:

### 1. The Inference Backend (Python)
A Python-based WebSocket server that ingests raw audio chunks from the frontend.
* **Machine Learning:** Uses `tensorflow_hub` to run audio through Google's YAMNet model.
* **Audio Processing:** Normalises and clips audio streams using `numpy`.
* **Stability Logic:** Implements a custom timer and confidence threshold (Rule A/B) to lock onto dominant sounds and ignore transient noise.

### 2. The Client Frontend (TypeScript / HTML)
A lightweight web application that captures microphone input and manages the visual output.
* **Hardware Bridge:** Connects to the Even Realities G2 glasses via [`@evenrealities/even_hub_sdk`](https://hub.evenrealities.com/docs/getting-started/overview).
* **Dual-Output Translation:** Maps detected YAMNet classes into two visual streams:
    * **HUD (Glasses):** Clean, recognisable ASCII art (e.g., `\((!))/ ALARM`, `V^..^V DOG`).
    * **Phone (Web):** Formatted text and Material Icons.
* **Audio Streaming:** Captures PCM audio events from the Even Hub and streams them securely to the backend via an ngrok tunnel. 

---

## Getting Started

Follow these steps to set up the Python backend server, establish a secure tunnel, and package the frontend application for the smart glasses.

### Prerequisites

Ensure your development environment is set up with the following:

* **[Node.js](https://nodejs.org/)** (v20 LTS or v22+ recommended)
* **Python 3** & **TensorFlow**
* **[Ngrok](https://ngrok.com/)** (For secure local tunneling)
* **Even Hub CLI** (Installed globally via `npm install -g @evenrealities/evenhub-cli`)
* **Even Realities App** (Installed on your smartphone and actively paired with your glasses)

---

### Part 1: Backend Setup (Python & Ngrok)

The backend handles the heavy lifting of processing environmental audio. This server must remain running locally to communicate with the glasses.

**1. Initialize the Processing Server**
Open PowerShell and navigate to your Python server directory (adjust the path to match your machine):
```powershell
cd C:\path\to\your\backend\folder
.\venv\Scripts\activate
python server.py
```
> **Note:** Leave this terminal window open and running in the background.

**2. Establish the Cloud Tunnel**
Open a **new** PowerShell window. Start the Ngrok tunnel to securely expose your active Python port (assuming port 8765) to the web:
```powershell
.\ngrok http 8765
```
> **Crucial Step:** Locate the "Forwarding" line in the terminal output and copy the generated secure URL (e.g., `https://random-words.ngrok-free.app`). Leave this window open and running.

---

### Part 2: Frontend Setup (Vite)

Initialise the frontend interface that will execute directly on the smart glasses.

**1. Scaffold the Workspace:**
Open a third PowerShell window, create a fresh Vite project using TypeScript, and install the required SDK:
```powershell
# Create the Vite TypeScript project
npm create vite@latest APP -- --template vanilla-ts

# Move into the project directory
cd APP

# Install standard dependencies
npm install

# Install the Even Hub SDK
npm install @evenrealities/even_hub_sdk

# Initialize your Even Hub manifest file
evenhub init APP
```

**2. Configure the Application Manifest:**
Before building, ensure your Even Hub manifest is configured correctly to request microphone access and use a valid package ID. Open `app.json` in your project root and update the `package_id` and `permissions` arrays:
```json
 "permissions": [
    {
      "name": "network",
      "desc": "This app needs to access the network in order to provide sound recognition.",
      "whitelist": [     
		
      ]
    },
    {
      "name": "g2-microphone",
      "desc": "Required to capture audio directly from the glasses."
    }  
  ],
```
*(Note: The `package_id` must follow a reverse-domain format using only lowercase letters and numbers).*

**3. Import and Connect Application Logic:**
1. Copy the application code (`src/main.ts`) into your newly created `APP/src` directory.
2. Open `src/main.ts` in your code editor.
3. Update the WebSocket connection string in the code with the **Ngrok URL** you generated in Part 1.

---

### Part 3: Build, Package & Deploy

Compile the TypeScript application and upload it to your device.

**1. Compile the Application:**
This command processes the code and generates a `dist` directory containing your optimised production assets:
```powershell
npm run build
```

**2. Package the Build:**
Use the Even Hub CLI to bundle the `dist` folder and your `app.json` manifest into an Even Hub Package (`.ehpk`):
```powershell
evenhub pack app.json dist -o APP.ehpk
```

**3. Sideload and Launch:**
Upload the compiled package to your Even account to access it permanently on your device.
1. Navigate to the [Even Hub Developer Portal](https://hub.evenrealities.com/) and log in.
2. Go to your Apps / Workspace section and select **Upload Build** (Private Apps/Sideloading).
3. Upload the generated `APP.ehpk` file.
4. Open the **Even Realities app** on your smartphone and navigate to your **Private Apps** list.
5. Tap the app to launch it. Press the "Initialize System" button on your phone screen to start the microphone array and begin broadcasting audio to your Python server.
