# persona_generator.py

import os
import praw
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import google.generativeai as genai
import textwrap
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_AGENT = os.getenv("REDDIT_USER_AGENT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_AGENT
)

def fetch_user_data(username, limit=30):
    user = reddit.redditor(username)
    items = []
    try:
        for comment in user.comments.new(limit=limit):
            items.append({
                "type": "comment",
                "text": comment.body,
                "subreddit": str(comment.subreddit),
                "url": f"https://www.reddit.com{comment.permalink}"
            })
    except: pass
    try:
        for post in user.submissions.new(limit=limit):
            items.append({
                "type": "post",
                "text": f"{post.title}\n{post.selftext}",
                "subreddit": str(post.subreddit),
                "url": f"https://www.reddit.com{post.permalink}"
            })
    except: pass
    return items

def build_prompt(items):
    compiled = ""
    for item in items:
        compiled += f"{item['type'].upper()} in r/{item['subreddit']}:\n{item['text']}\n(URL: {item['url']})\n\n"
    return f"""
You are a UX researcher. You will receive Reddit comments and posts.

ONLY return a **valid JSON object** matching the following structure. Do NOT include markdown, explanation, or anything else.

```json
{{
  "name": "",
  "age": "",
  "location": "",
  "profile_quote": "",
  "goals": [],
  "frustrations": [],
  "interests": [],
  "personality": {{
    "openness": 0-100,
    "conscientiousness": 0-100,
    "extraversion": 0-100,
    "agreeableness": 0-100,
    "neuroticism": 0-100
  }},
  "technology": [],
  "image_hint": "",
  "citations": {{
    "goals": [],
    "frustrations": [],
    "interests": [],
    "personality": []
  }}
}}

Only return a valid JSON object.

Reddit Data:
{compiled}
"""

def generate_persona_json(username):
    data = fetch_user_data(username)
    if not data:
        return None, "No data found"
    prompt = build_prompt(data)
    response = model.generate_content(prompt)
    try:
        # Clean up Gemini's response
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        json_data = json.loads(text)
    except:
        return None, "Invalid JSON from Gemini"
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    out_path = output_dir / f"{username}_persona.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    return out_path, json_data

def render_visual(json_data, username):
    # Setup
    width = 900
    height = 1600
    background = "white"
    section_bg = "#f0f0f0"
    bar_color = "#4A90E2"
    section_gap = 40
    padding = 25
    line_height = 28
    wrap_width = 60

    # Create canvas
    img = Image.new('RGB', (width, height), color=background)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("fonts/arial.ttf", 20)
        heading_font = ImageFont.truetype("fonts/arial.ttf", 24)
    except:
        font = ImageFont.load_default()
        heading_font = font

    y = padding

    def draw_text_block(label, text, x, y, font):
        draw.text((x, y), f"{label}: {text if text else 'N/A'}", font=font, fill="black")
        return y + line_height + 5

    def draw_wrapped_list(title, items, y):
        # Draw section box
        section_height = (len(items) + 1) * line_height + 30
        draw.rectangle([0, y - 10, width, y + section_height], fill=section_bg)
        draw.text((padding, y), f"{title}:", font=heading_font, fill="black")
        y += line_height + 10
        for item in items:
            for line in textwrap.wrap(f"- {item}", width=wrap_width):
                draw.text((padding + 20, y), line, font=font, fill="black")
                y += line_height
        return y + section_gap

    def draw_personality_bar(trait, value, y):
        bar_x = padding + 180
        bar_width = 400
        bar_height = 20

        # Label
        draw.text((padding, y), f"{trait}:", font=font, fill="black")

        # Bar background
        draw.rectangle([bar_x, y, bar_x + bar_width, y + bar_height], fill="#ddd")
        # Bar fill
        fill_width = int(bar_width * (value / 100))
        draw.rectangle([bar_x, y, bar_x + fill_width, y + bar_height], fill=bar_color)

        # Value
        draw.text((bar_x + bar_width + 10, y), f"{value}%", font=font, fill="black")

        return y + bar_height + 10

    # Header section
    y = draw_text_block("Name", json_data['name'], padding, y, heading_font)
    y = draw_text_block("Age", str(json_data['age']), padding, y, font)
    y = draw_text_block("Location", json_data['location'], padding, y, font)
    y = draw_text_block("Quote", json_data['profile_quote'], padding, y, font)
    y += section_gap

    # Goals, Frustrations, Interests, Technology
    for section in ['goals', 'frustrations', 'interests', 'technology']:
        y = draw_wrapped_list(section.capitalize(), json_data.get(section, []), y)

    # Personality
    y = draw_wrapped_list("Personality Traits", [], y)
    for trait, value in json_data.get("personality", {}).items():
        y = draw_personality_bar(trait.capitalize(), value, y)

    # Save image
    output_path = Path("output") / f"{username}_persona.png"
    img.save(output_path)
    return output_path
