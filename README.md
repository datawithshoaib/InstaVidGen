# InstaGen

InstaGen is a Streamlit app for creating short Instagram quote videos. It can use a manually entered quote or generate one with Google Gemini, place the quote over a local background, add a fade-in effect, and export an MP4 video.

## Features

- Generate philosophical quotes with Gemini or enter a quote manually
- Choose a theme, philosopher, aspect ratio, font, placement, and video duration
- Generate Instagram captions and hashtags
- Create one video or a batch of 20 videos
- Keep a short history of generated quotes during the current session

## Requirements

- Python 3.10 or newer
- A Google Gemini API key for AI quote and caption generation
- Background images in `Backgrounds/`

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Keep this file private. It is excluded by `.gitignore`.

## Run

Start the Streamlit app with:

```powershell
python -m streamlit run app.py
```

Then open the local URL shown by Streamlit, usually `http://localhost:8501`.

## Project folders

| Path | Purpose |
| --- | --- |
| `app.py` | Main Streamlit application |
| `Backgrounds/` | Source PNG/JPG backgrounds |
| `fonts/` | Local font files used for quote rendering |
| `output/videos/` | Generated MP4 files |
| `requirements.txt` | Python dependencies |

Generated videos are intentionally ignored by Git. Keep any background images and fonts that the app needs in their respective folders.

## Notes

- The app uses OpenCV to encode video with the H.264 `avc1` codec. If video creation fails, install an OpenCV build and video codec support appropriate for your operating system.
- AI features require a working internet connection and a valid Gemini API key.