<div align="center">

```
██╗   ██╗████████╗██████╗  ██████╗ ██╗    ██╗███╗   ██╗
╚██╗ ██╔╝╚══██╔══╝██╔══██╗██╔═══██╗██║    ██║████╗  ██║
 ╚████╔╝    ██║   ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║
  ╚██╔╝     ██║   ██║  ██║██║   ██║██║███╗██║██║╚██╗██║
   ██║      ██║   ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║
   ╚═╝      ╚═╝   ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝
```

### 🔴 Free • Fast • No Ads • Open Source

[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Python](https://img.shields.io/badge/Python_3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![pytubefix](https://img.shields.io/badge/pytubefix-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://github.com/JuanBindez/pytubefix)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)

![GitHub last commit](https://img.shields.io/github/last-commit/SOMU3103/YTDOWN?color=red&style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/SOMU3103/YTDOWN?style=flat-square&color=yellow)
![GitHub repo size](https://img.shields.io/github/repo-size/SOMU3103/YTDOWN?style=flat-square&color=blue)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

</div>

---

> **YTDOWN** is a **Flask web application** that lets you download YouTube videos and audio directly from your browser — no desktop app needed. Just paste a URL, pick your format and quality, and hit download. Powered by `pytubefix` + `FFmpeg` for high-quality merging.

---

## ⚡ What Makes This Different

| Feature | YTDOWN | Other Tools |
|--------|--------|-------------|
| 🌐 Web-based (Flask) | ✅ Yes | ❌ Usually desktop-only |
| 💾 No server storage | ✅ Streams to buffer | ❌ Saves to server disk |
| 🎬 Auto video+audio merge | ✅ FFmpeg powered | ❌ Separate files |
| 🚫 Zero ads | ✅ Always | ❌ Usually full of ads |
| 🔧 Self-hostable | ✅ Yes | ❌ Locked to their server |
| 🎛️ Quality selector | ✅ Dynamic per video | ❌ Fixed options |

---

## 🧠 How It Works

```
User pastes URL
      │
      ▼
Flask backend hits YouTube via pytubefix
      │
      ├──► Audio only?  ──► Stream buffer ──► .mp3 download
      │
      └──► Video?
              │
              ├── 360p/480p/720p → Progressive stream → .mp4 buffer → download
              │
              └── 1080p/1440p/4K → Download video + audio separately
                                         │
                                         ▼
                                   FFmpeg merges them
                                         │
                                         ▼
                                  Buffer → .mp4 download
                                  (temp files auto-deleted)
```

---

## 🛠️ Tech Stack

```python
backend   = "Flask"          # Web framework
extractor = "pytubefix"      # YouTube stream fetcher
merger    = "FFmpeg"         # Video + Audio combiner
frontend  = "HTML5 + Jinja2" # Templates served by Flask
storage   = "BytesIO buffer" # Zero disk writes on server
```

---
---

## 🚀 Getting Started

### Prerequisites

```bash
# Check Python version (3.8+ required)
python --version

# Check FFmpeg (required for 1080p+ merging)
ffmpeg -version
```

> 📥 FFmpeg not installed? Get it at [ffmpeg.org/download](https://ffmpeg.org/download.html) and add to PATH.

---

### Installation

**Clone the repo**
```bash
git clone https://github.com/SOMU3103/YTDOWN.git
cd YTDOWN
```

**Create & activate virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**Install dependencies**
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install flask pytubefix
```

**Run the Flask server**
```bash
python app.py
```

Open your browser at:
```
http://127.0.0.1:5000
```

---

## 🎮 Usage

```
1.  Open http://127.0.0.1:5000 in your browser
2.  Paste any YouTube URL
3.  Click "Fetch" — qualities are loaded dynamically
4.  Select:  [ MP4 Video ]  or  [ MP3 Audio ]
5.  Choose resolution  (360p / 480p / 720p / 1080p / 4K)
6.  Hit Download — file saves directly to your device
```

### Supported URLs
```
✅  https://www.youtube.com/watch?v=XXXXXXXXXXX
✅  https://youtu.be/XXXXXXXXXXX
✅  YouTube Shorts
✅  Age-unrestricted public videos
```

---

## 📁 Project Structure

```
YTDOWN/
│
├── 📄 app.py                  # Flask app — routes, download logic, FFmpeg merge
├── 📂 templates/
│   └── 📄 index.html          # Frontend UI (served by Flask/Jinja2)
├── 📂 static/                 # CSS, JS, icons
├── 📋 requirements.txt        # Python dependencies
└── 📖 README.md
```

### Key Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | `GET` | Renders the main download page |
| `/` | `POST` | Handles download request (video/audio) |
| `/get_qualities` | `POST` | Returns available streams for a URL (JSON) |

---

## ⚙️ API Reference

### `POST /get_qualities`

Fetch all available streams for a YouTube URL.

**Request**
```json
{
  "url": "https://www.youtube.com/watch?v=XXXXXXXXXXX"
}
```

**Response**
```json
{
  "success": true,
  "title": "Video Title Here",
  "duration": 243,
  "video_qualities": [
    { "resolution": "1080", "label": "1080p", "fps": 30 },
    { "resolution": "720",  "label": "720p",  "fps": 30 }
  ],
  "audio_qualities": [
    { "bitrate": "128kbps", "label": "128kbps" }
  ]
}
```

---

## 🤝 Contributing

```bash
# 1. Fork the repo on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/YTDOWN.git

# 3. New branch
git checkout -b feature/your-feature

# 4. Make changes & commit
git commit -m "feat: add your feature"

# 5. Push & open a PR
git push origin feature/your-feature
```

**Ideas welcome:**
- 🌙 Dark/light mode toggle
- 📋 Download history
- 📦 Playlist batch download
- 🖼️ Thumbnail preview on URL paste
- 📊 Real-time download speed indicator
- 🐳 Docker support

---

## ⚠️ Disclaimer

> This tool is for **personal and educational use only.**
> Respect YouTube's [Terms of Service](https://www.youtube.com/t/terms) and applicable copyright laws.
> Do not download content you do not have rights to.

---

## 📝 License

```
MIT License — Copyright (c) 2026 Somnath (SOMU3103)
```

See [`LICENSE`](https://github.com/SOMU3103/YTDOWN/blob/main/LICENSE) for details.

---

<div align="center">

**Built by [SOMU3103](https://github.com/SOMU3103)**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-somnath312006-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/somnath312006)
[![GitHub](https://img.shields.io/badge/GitHub-SOMU3103-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/SOMU3103)
[![Repo](https://img.shields.io/badge/Repo-YTDOWN-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://github.com/SOMU3103/YTDOWN)

<br/>

*If this saved you time — drop a ⭐ on the repo. It means a lot!*

</div>
