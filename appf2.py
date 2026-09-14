# --- Imports ---
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np
import cv2
import random
from dotenv import load_dotenv
import google.generativeai as genai

# --- Directories ---
BG_DIR = os.path.join("Backgrounds")
OUTPUT_DIR = os.path.join("output", "videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Load Gemini API Key ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Helper Functions ---
def list_backgrounds():
    return [f for f in os.listdir(BG_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

def load_image(path, aspect_ratio):
    img = Image.open(path).convert("RGBA")
    if aspect_ratio:
        w, h = img.size
        target_w = w
        target_h = int(w / aspect_ratio)
        if target_h > h:
            target_h = h
            target_w = int(h * aspect_ratio)
        left = (w - target_w) // 2
        top = (h - target_h) // 2
        img = img.crop((left, top, left + target_w, top + target_h))
    return img

def overlay_text(img, text):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=int(img.height/15))
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (img.width - text_w) // 2
    y = (img.height - text_h) // 2
    shadowcolor = "black"
    for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
        draw.text((x+dx, y+dy), text, font=font, fill=shadowcolor)
    draw.text((x, y), text, font=font, fill="white")
    return img

def make_fadein_video_cv2(img, duration, fade_duration, output_path):
    fps = 24
    total_frames = int(duration * fps)
    fade_frames = int(fade_duration * fps)
    img_rgb = img.convert("RGB")
    arr = np.array(img_rgb)
    h, w, _ = arr.shape
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    black = np.zeros_like(arr)
    for i in range(total_frames):
        if i < fade_frames:
            alpha = i / fade_frames
            frame = cv2.addWeighted(black, 1 - alpha, arr, alpha, 0)
        else:
            frame = arr.copy()
        out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    out.release()

def generate_quote(theme=None, philosopher=None):
    model = genai.GenerativeModel("gemini-2.5-flash")
    if philosopher and philosopher != "None":
        prompt = (
            f"From {philosopher}’s writings, select a less-quoted passage that carries deep existential, controversial, or challenging insight. Do not use popular or commonly shared quotes — instead, surface the ones hidden in their texts that make readers stop and question their own beliefs "
            "Do not include any list, explanation, or extra text. Only output the quote itself."
        )
    elif theme and theme != "None":
        prompt = (
            f"Write one original, profound, and thought-provoking philosophical quote about {theme.lower()}. It should feel timeless, hard-hitting, and open to interpretation — the kind of quote that challenges assumptions, stirs reflection, and lingers in the reader’s mind "
            "Do not include any list, explanation, or extra text. Only output the quote itself."
        )
    else:
        prompt = (
            "Write one powerful, original, and thought-provoking philosophical quote that feels timeless — it should challenge beliefs, provoke reflection, sometimes border on controversial, and leave the reader with an open question lingering in their mind."
            "Do not include any list, explanation, or extra text. Only output the quote itself."
        )
    response = model.generate_content(prompt)
    text = response.text.strip()
    if "\n" in text:
        lines = [l for l in text.splitlines() if l.strip() and not l.strip()[0] in "-•0123456789"]
        if lines:
            text = lines[0].strip()
    return text

# --- Streamlit UI ---
st.title("📸 Instagram Video Generator")


# --- UI Controls ---
aspect = st.sidebar.selectbox("Aspect Ratio", ["4:5", "9:16", "16:9", "4:3", "1:1"], index=0)
aspect_map = {"4:5": 4/5, "9:16": 9/16, "16:9": 16/9, "4:3": 4/3, "1:1": 1.0}
aspect_ratio = aspect_map[aspect]
fade_duration = st.sidebar.slider("Fade-in Duration (seconds)", 0.5, 3.0, 2.0, 0.1)
video_duration = st.sidebar.slider("Video Duration (seconds)", 3.0, 8.0, 5.0, 0.1)
font_size = st.sidebar.slider("Quote Font Size (%)", 2, 10, 4, 1)
placement = st.sidebar.selectbox("Quote Placement", ["Center", "Top", "Bottom"], index=0)

# --- Quote Theme & Input ---
st.write("**Quote:**")
themes = ["None", "Religion", "Atheism", "Solitude", "Consistency", "Existence", "Focus", "Motivation"]
selected_theme = st.selectbox("Quote Theme", themes, index=0)
philosophers = [
    "None",
    "Fyodor Dostoevsky", "Friedrich Nietzsche", "Franz Kafka", "Marcus Aurelius", "Epictetus", "Arthur Schopenhauer",
    "Socrates", "Aristotle", "Plato", "Heraclitus", "Epicurus", "Confucius", "Lao Tzu",
    "Khalil Gibran", "Immanuel Kant", "Spinoza", "Soren Kierkegaard", "Carl Jung", "Albert Camus"
]
selected_philosopher = st.selectbox("Philosopher (optional)", philosophers, index=0)
quote_mode = st.radio("Choose quote input method:", ["Manual", "Generate with Gemini"], horizontal=True)
if quote_mode == "Manual":
    user_quote = st.text_area("Enter your quote (2-3 lines recommended):", "Solitude is the soul's holiday.\nLet your mind wander.")
    quote = user_quote.strip()
else:
    if st.button("Generate Quote with Gemini"):
        quote = generate_quote(selected_theme, selected_philosopher)
        st.session_state.generated_quote = quote
    quote = st.session_state.get("generated_quote", "")
    st.text_area("Generated quote:", value=quote, key="generated_quote_area")

# --- Text Wrapping Helper ---
def wrap_text(text, font, max_width, draw):
    # Split text into lines that fit max_width
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test_line = line + (" " if line else "") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > max_width and line:
            lines.append(line)
            line = word
        else:
            line = test_line
    if line:
        lines.append(line)
    return lines

def overlay_text(img, text, font_percent=10, placement="Center"):
    draw = ImageDraw.Draw(img)
    # Font size as percent of image height
    font_px = max(10, int(img.height * font_percent / 100))
    try:
        font = ImageFont.truetype("arial.ttf", size=font_px)
    except:
        font = ImageFont.load_default()
    # Wrap text to fit image width (90%)
    max_width = int(img.width * 0.9)
    lines = wrap_text(text, font, max_width, draw)
    # Only keep 2-3 lines
    if len(lines) > 3:
        lines = lines[:3]
        lines[-1] += "..."
    text_block = "\n".join(lines)
    # Get total text block height
    bbox = draw.multiline_textbbox((0, 0), text_block, font=font, spacing=6)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    # Placement
    if placement == "Top":
        x = (img.width - text_w) // 2
        y = int(img.height * 0.08)
    elif placement == "Bottom":
        x = (img.width - text_w) // 2
        y = img.height - text_h - int(img.height * 0.08)
    else:  # Center
        x = (img.width - text_w) // 2
        y = (img.height - text_h) // 2
    # Draw shadow
    shadowcolor = "black"
    for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
        draw.multiline_text((x+dx, y+dy), text_block, font=font, fill=shadowcolor, align="center", spacing=6)
    draw.multiline_text((x, y), text_block, font=font, fill="white", align="center", spacing=6)
    return img

# --- Generate Video Button ---
if st.button("Generate Instagram Video"):
    bg_files = list_backgrounds()
    if not bg_files:
        st.error("⚠ No images found in 'Backgrounds/' folder!")
    elif not quote:
        st.error("Please enter or generate a quote.")
    else:
        bg_choice = random.choice(bg_files)
        bg_path = os.path.join(BG_DIR, bg_choice)
        img = load_image(bg_path, aspect_ratio)
        img = overlay_text(img, quote, font_percent=font_size, placement=placement)
        st.image(img, caption="Preview", use_column_width=True)
        filename = f"{os.path.splitext(bg_choice)[0]}_{aspect.replace(':','x')}.mp4"
        out_path = os.path.join(OUTPUT_DIR, filename)
        with st.spinner("Rendering video..."):
            make_fadein_video_cv2(img, video_duration, fade_duration, out_path)
        st.success(f"Video saved to {out_path}")
        with open(out_path, "rb") as f:
            st.video(f.read())
        st.write("Quote used:")
        st.info(quote)