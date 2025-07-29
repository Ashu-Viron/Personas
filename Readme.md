# 🧠 Reddit User Persona Generator using Gemini AI

This project generates a detailed **user persona** from a Reddit user's public posts and comments using **Google's Gemini AI**.

It scrapes a user's Reddit activity, analyzes the content using an LLM, and returns:
- A JSON file with structured persona traits
- A clean, styled persona image with goals, frustrations, interests, and personality bars

---

## 🚀 Features

- 🔍 Scrapes Reddit posts & comments from a given profile
- 🤖 Uses Gemini 1.5 Flash for fast, smart persona generation
- 📊 Generates a PNG persona card with section backgrounds & bar charts
- 📁 Saves all output (JSON + Image) in `/output` folder
- 🧠 Cites exact Reddit URLs used for each trait
- 🧑‍💻 Streamlit-based UI

---

## 📦 Requirements

- Python 3.8+
- Google Gemini API Key
- Reddit API Credentials (from Reddit Developer Portal)

---

## 🔧 How to Run the Project

### 1. Clone the Project

```bash
git clone https://github.com/your-username/reddit-persona-generator.git
cd reddit-persona-generator
```
![Demo]
https://github.com/user-attachments/assets/f729ee26-7cfe-4da2-acdd-0b62acebd4ec


