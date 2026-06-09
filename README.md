# YoutDown - Modern YouTube Downloader

A sleek, fast, and modern web application to download YouTube videos in high-quality MP4 and MP3 formats. Built with Python (Flask) on the backend and pure HTML/CSS/JS without any clunky frameworks on the frontend.

## Features

* **Sleek UI:** Dark modern UI with gradients, soft shadows, and clean typography.
* **Auto-Paste:** Quick button to paste YouTube URLs.
* **Format Selection:** Choose from 1080p, 720p, 480p, or high-quality Audio (MP3).
* **Metadata Preview:** Displays the video title, duration, and thumbnail preview before downloading.
* **Automated Cleanup:** Downloads are stored temporarily and cleared automatically.
* **Mobile Ready:** Fully responsive design that works beautifully on all screen sizes.

## Project Structure

```text
yout/
├── app.py                 # Flask REST backend and download logic
├── requirements.txt       # Python dependencies 
├── templates/
│   └── index.html         # Main UI
└── static/
    ├── style.css          # Vanilla CSS styling
    └── script.js          # Vanilla JS integration with API
```

## How to Run Locally

### 1. Requirements
Ensure you have Python 3.8+ installed and `ffmpeg` installed on your system PATH (required for audio extraction and muxing 1080p).

For Windows, you can install ffmpeg via winget or chocolatey:
```bash
winget install ffmpeg
```

### 2. Setup
Create and activate a virtual environment, then install the dependencies:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the App
```bash
# Start the Flask development server on port 5000
python app.py
```
Visit http://127.0.0.1:5000 in your browser.

## Deployment on a VPS (Ubuntu/Debian)

To deploy securely behind Nginx using Gunicorn on a Linux VPS:

1. Copy the project source to `/var/www/youtDown`.
2. Install `ffmpeg`:
   ```bash
   sudo apt update && sudo apt install ffmpeg python3-pip python3-venv -y
   ```
3. Create a virtual environment and install via pip:
   ```bash
   cd /var/www/youtDown
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Start the app with Gunicorn to test:
   ```bash
   gunicorn --bind 0.0.0.0:8000 app:app
   ```
5. Use `systemd` to keep the gunicorn service running in the background.

## Disclaimer
This project is for educational purposes only. Downloading copyrighted material without permission may violate terms of service and copyright laws.
