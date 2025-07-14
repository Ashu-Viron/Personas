# app.py
import streamlit as st
from persona_generator import generate_persona_json, render_visual

st.set_page_config(page_title="Reddit Persona Generator", layout="centered")
st.title("🧠 Reddit User Persona Generator")

reddit_url = st.text_input("Enter Reddit Profile URL (e.g. https://www.reddit.com/user/kojied/)")

if reddit_url and reddit_url.startswith("https://www.reddit.com/user/"):
    username = reddit_url.rstrip("/").split("/")[-1]
    if st.button("Generate Persona"):
        with st.spinner("Fetching and analyzing Reddit data..."):
            json_path, json_data = generate_persona_json(username)
            if json_path is None:
                st.error(json_data)
            else:
                image_path = render_visual(json_data, username)
                st.success("Persona generated!")
                st.image(image_path, caption="Generated Persona", use_column_width=True)

                st.download_button("Download Persona JSON", open(json_path, "rb"), file_name=f"{username}_persona.json")
                st.download_button("Download Persona Image", open(image_path, "rb"), file_name=f"{username}_persona.png")
