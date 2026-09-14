# --- Caption and Hashtag Generation ---
caption_and_hashtags = ""
def generate_caption_and_hashtags(quote, theme=None, philosopher=None):
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = (
        f"Given the following quote: '{quote}'\n"
        + (f"Theme: {theme}.\n" if theme and theme != "None" else "")
        + (f"Philosopher: {philosopher}.\n" if philosopher and philosopher != "None" else "")
        + "Write a concise, direct Instagram caption (2-3 lines) that clearly explains the meaning of the quote without unnecessary hooks or excessive enthusiasm. Be thoughtful and to the point. "
        "Then, on a new line, provide 5-6 relevant and trending hashtags for this quote. "
        "Format: Caption first, then hashtags on a new line, separated by spaces."
    )
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            return "[Gemini did not return a valid caption. Please try again later.]"
    except Exception as e:
        return f"[Error generating caption: {e}]"

# --- Bulk Video Generation ---
def generate_bulk_videos(n=20):
    bg_files = list_backgrounds()
    if not bg_files:
        st.error("⚠ No images found in 'Backgrounds/' folder!")
        return
    if not quote:
        st.error("Please enter or generate a quote.")
        return
    for i in range(n):
        bg_choice = random.choice(bg_files)
        bg_path = os.path.join(BG_DIR, bg_choice)
        # For each video, generate a new quote if using Gemini, else use the manual quote
        if quote_mode == "Generate with Gemini":
            q = generate_quote(selected_theme, selected_philosopher)
        else:
            q = quote
        img = load_image(bg_path, aspect_ratio)
        img = overlay_text(img, q, font_percent=font_size, placement=placement)
        filename = f"{os.path.splitext(bg_choice)[0]}_{aspect.replace(':','x')}_bulk_{i+1}.mp4"
        out_path = os.path.join(OUTPUT_DIR, filename)
        with st.spinner(f"Rendering video {i+1}/{n}..."):
            make_fadein_video_cv2(img, video_duration, fade_duration, out_path)
        st.success(f"Video {i+1} saved to {out_path}")
        with open(out_path, "rb") as f:
            st.video(f.read())

# --- Place the bulk button after all UI controls and quote logic ---
# (Place this after the single video button logic in your file)
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
            f"Give one of the best, most profound philosophical quotes from {philosopher}. "
            "Do not include any list, explanation, or extra text. Only output the quote itself."
        )
    elif theme and theme != "None":
        prompt = (
            f"Write only one deep, original, philosophical quote about {theme.lower()} suitable for Instagram. "
            "Do not include any list, explanation, or extra text. Only output the quote itself."
        )
    else:
        prompt = (
            "Write only one deep, original, philosophical quote suitable for Instagram. "
            "Do not include any list, explanation, or extra text. Only output the quote itself."
        )
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            text = response.text.strip()
            if "\n" in text:
                lines = [l for l in text.splitlines() if l.strip() and not l.strip()[0] in "-•0123456789"]
                if lines:
                    text = lines[0].strip()
            return text
        else:
            return "[Gemini did not return a valid quote. Please try again later.]"
    except Exception as e:
        return f"[Error generating quote: {e}]"


# --- Semantic Similarity Helpers ---
from typing import List
def get_gemini_embedding(text: str):
    try:
        # Use Gemini's embedding API (replace with correct call if needed)
        emb = genai.embed_content([text])[0]
        return np.array(emb)
    except Exception:
        return None

def cosine_similarity(vec1, vec2):
    if vec1 is None or vec2 is None:
        return 0.0
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

# --- Streamlit UI ---
st.title("📸 Instagram Video Generator")


# --- UI Controls ---
FONTS_DIR = os.path.join("fonts")
def list_fonts():
    if not os.path.exists(FONTS_DIR):
        return []
    return [f for f in os.listdir(FONTS_DIR) if f.lower().endswith(('.ttf', '.otf'))]

font_files = list_fonts()
font_options = ["Default"] + font_files
selected_font = st.sidebar.selectbox("Quote Font", font_options, index=0)
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
    "Fyodor Dostoevsky","Nicollo Machiavelli", "Friedrich Nietzsche", "Franz Kafka", "Marcus Aurelius", "Epictetus", "Arthur Schopenhauer",
    "Socrates", "Aristotle", "Plato", "Heraclitus", "Epicurus", "Confucius", "Lao Tzu",
    "Khalil Gibran", "Immanuel Kant", "Spinoza", "Soren Kierkegaard", "Carl Jung", "Albert Camus"
]
selected_philosopher = st.selectbox("Philosopher (optional)", philosophers, index=0)
quote_mode = st.radio("Choose quote input method:", ["Manual", "Generate with Gemini"], horizontal=True)
if quote_mode == "Manual":
    user_quote = st.text_area("Enter your quote (2-3 lines recommended):", "Solitude is the soul's holiday.\nLet your mind wander.")
    quote = user_quote.strip()
    # Layout: two columns, left for quote, right for history (to match AI section)
    col1, col2 = st.columns([2,1])
    with col1:
        st.text_area("Manual quote:", value=quote, key="manual_quote_area")
    with col2:
        st.markdown("**Quote History (last 10):**")
        for idx, q in enumerate(st.session_state.get('quote_history', [])):
            st.markdown(f"{idx+1}. {q}")

    # Option to generate Instagram caption & hashtags for manual quote
    if quote:
        if st.button("Generate Instagram Caption & Hashtags", key="caption_btn_manual"):
            with st.spinner("Generating caption and hashtags..."):
                caption_and_hashtags = generate_caption_and_hashtags(quote, selected_theme, selected_philosopher)
            st.session_state.caption_and_hashtags = caption_and_hashtags
        caption_and_hashtags = st.session_state.get("caption_and_hashtags", "")
        if caption_and_hashtags:
            st.markdown("---")
            st.subheader("Instagram Caption & Hashtags")
            st.code(caption_and_hashtags, language="markdown")
            st.info("Copy the above caption and hashtags for your Instagram post.")
else:
    # Initialize quote history in session state
    if 'quote_history' not in st.session_state:
        st.session_state.quote_history = []
    if 'quote_embeddings' not in st.session_state:
        st.session_state.quote_embeddings = []
    if st.button("Generate Quote with Gemini"):
        # Try up to 10 times to get a semantically unique quote
        last_quote = st.session_state.quote_history[0] if st.session_state.quote_history else None
        new_quote = None
        new_emb = None
        threshold = 0.9
        for _ in range(10):
            candidate = generate_quote(selected_theme, selected_philosopher)
            candidate_emb = get_gemini_embedding(candidate)
            is_duplicate = False
            for emb in st.session_state.quote_embeddings:
                if cosine_similarity(candidate_emb, emb) > threshold:
                    is_duplicate = True
                    break
            if candidate and candidate != last_quote and candidate not in st.session_state.quote_history and not is_duplicate:
                new_quote = candidate
                new_emb = candidate_emb
                break
        if not new_quote:
            # fallback: allow a quote not equal to last, but may be semantically similar
            for _ in range(5):
                candidate = generate_quote(selected_theme, selected_philosopher)
                if candidate and candidate != last_quote:
                    new_quote = candidate
                    new_emb = get_gemini_embedding(candidate)
                    break
        if not new_quote:
            new_quote = generate_quote(selected_theme, selected_philosopher)
            new_emb = get_gemini_embedding(new_quote)
            st.warning("Could not find a unique quote after several attempts. You may see a repeat or paraphrase.")
        st.session_state.generated_quote = new_quote
        # Update history (keep last 10, newest first)
        st.session_state.quote_history = [new_quote] + [q for q in st.session_state.quote_history if q != new_quote]
        st.session_state.quote_history = st.session_state.quote_history[:10]
        st.session_state.quote_embeddings = [new_emb] + [e for i, e in enumerate(st.session_state.quote_embeddings) if i < 9]
    quote = st.session_state.get("generated_quote", "")
    # Layout: two columns, left for quote, right for history
    col1, col2 = st.columns([2,1])
    with col1:
        st.text_area("Generated quote:", value=quote, key="generated_quote_area")
    with col2:
        st.markdown("**Quote History (last 10):**")
        for idx, q in enumerate(st.session_state.quote_history):
            st.markdown(f"{idx+1}. {q}")

    # Option to generate Instagram caption & hashtags after quote generation
    if quote:
        if st.button("Generate Instagram Caption & Hashtags", key="caption_btn_quote"):
            with st.spinner("Generating caption and hashtags..."):
                caption_and_hashtags = generate_caption_and_hashtags(quote, selected_theme, selected_philosopher)
            st.session_state.caption_and_hashtags = caption_and_hashtags
        caption_and_hashtags = st.session_state.get("caption_and_hashtags", "")
        if caption_and_hashtags:
            st.markdown("---")
            st.subheader("Instagram Caption & Hashtags")
            st.code(caption_and_hashtags, language="markdown")
            st.info("Copy the above caption and hashtags for your Instagram post.")

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
    font = None
    if 'selected_font' in globals() and selected_font and selected_font != "Default":
        font_path = os.path.join(FONTS_DIR, selected_font)
        try:
            font = ImageFont.truetype(font_path, size=font_px)
        except:
            font = None
    if font is None:
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

    # Add philosopher name below quote if selected, in smaller size and Cinzel font
    philosopher = None
    if 'selected_philosopher' in globals() and selected_philosopher and selected_philosopher != "None":
        philosopher = selected_philosopher

    # Calculate quote block size
    bbox = draw.multiline_textbbox((0, 0), text_block, font=font, spacing=6)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Placement for quote
    if placement == "Top":
        x = (img.width - text_w) // 2
        y = int(img.height * 0.08)
    elif placement == "Bottom":
        x = (img.width - text_w) // 2
        y = img.height - text_h - int(img.height * 0.08)
    else:  # Center
        x = (img.width - text_w) // 2
        y = (img.height - text_h) // 2

    # Draw quote shadow and text
    shadowcolor = "black"
    for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
        draw.multiline_text((x+dx, y+dy), text_block, font=font, fill=shadowcolor, align="center", spacing=6)
    draw.multiline_text((x, y), text_block, font=font, fill="white", align="center", spacing=6)

    # Draw philosopher name below quote, smaller and in Cinzel font
    if philosopher:
        cinzel_path = os.path.join(FONTS_DIR, "Cinzel-VariableFont_wght.ttf")
        small_font_px = max(8, int(font_px * 0.7))
        try:
            cinzel_font = ImageFont.truetype(cinzel_path, size=small_font_px)
        except:
            cinzel_font = ImageFont.load_default()
        philo_text = f"- {philosopher} -"
        # Get size and position
        philo_bbox = draw.textbbox((0, 0), philo_text, font=cinzel_font)
        philo_w = philo_bbox[2] - philo_bbox[0]
        philo_h = philo_bbox[3] - philo_bbox[1]
        philo_x = (img.width - philo_w) // 2
        philo_y = y + text_h + int(img.height * 0.02)
        # Draw shadow for philosopher name
        for dx, dy in [(-1,-1), (1,-1), (-1,1), (1,1)]:
            draw.text((philo_x+dx, philo_y+dy), philo_text, font=cinzel_font, fill=shadowcolor)
        draw.text((philo_x, philo_y), philo_text, font=cinzel_font, fill="white")

    return img


# --- Generate Video Button ---
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

        # --- Instagram Caption & Hashtags Section ---
        if st.button("Generate Instagram Caption & Hashtags"):
            with st.spinner("Generating caption and hashtags..."):
                caption_and_hashtags = generate_caption_and_hashtags(quote, selected_theme, selected_philosopher)
            st.markdown("---")
            st.subheader("Instagram Caption & Hashtags")
            st.code(caption_and_hashtags, language="markdown")
            st.info("Copy the above caption and hashtags for your Instagram post.")

# --- Bulk Video Generation ---
if st.button("Generate 20 Videos (Bulk)"):
    bg_files = list_backgrounds()
    if not bg_files:
        st.error("⚠ No images found in 'Backgrounds/' folder!")
    elif not quote and quote_mode == "Manual":
        st.error("Please enter or generate a quote.")
    else:
        for i in range(20):
            bg_choice = random.choice(bg_files)
            bg_path = os.path.join(BG_DIR, bg_choice)
            # For each video, generate a new quote if using Gemini, else use the manual quote
            if quote_mode == "Generate with Gemini":
                q = generate_quote(selected_theme, selected_philosopher)
            else:
                q = quote
            img = load_image(bg_path, aspect_ratio)
            img = overlay_text(img, q, font_percent=font_size, placement=placement)
            filename = f"{os.path.splitext(bg_choice)[0]}_{aspect.replace(':','x')}_bulk_{i+1}.mp4"
            out_path = os.path.join(OUTPUT_DIR, filename)
            with st.spinner(f"Rendering video {i+1}/20..."):
                make_fadein_video_cv2(img, video_duration, fade_duration, out_path)
            st.success(f"Video {i+1} saved to {out_path}")
            with open(out_path, "rb") as f:
                st.video(f.read())