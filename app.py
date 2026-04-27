import streamlit as st
import requests

# --- CONFIGURATION ---
HF_API_KEY = "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"
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers_hf = {"Authorization": f"Bearer {HF_API_KEY}"}

CATEGORIES = [
    "Missing Folk", "Messed Up Families", "Don't Trust The Food", 
    "Suspicious Newcomer", "Celebrity & Pop Culture Fiction", "Revenge", 
    "When Cops Need Help", "Hostage", "Whodunnit Mystery", "Sci-Fi", 
    "Domestic Thriller", "Legal/Courtroom Thriller", "Cosy Crime", 
    "Political Thriller", "FemRage", "Weird Girl Fiction", "The Past Comes Back"
]

st.set_page_config(page_title="Book Genre Detective", page_icon="🕵️‍♀️")
st.title("🕵️‍♀️ Book Genre Detective")

# --- STEP 1: CLEAN THE INPUT ---
raw_isbn = st.text_input("Enter ISBN-13:", placeholder="9780141036144")
isbn = raw_isbn.replace("-", "").replace(" ", "").strip()

if isbn:
    # --- STEP 2: THE "HUMAN" REQUEST ---
    # We add 'headers' to pretend to be a real browser
    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    with st.spinner("Searching Google Books..."):
        # We try two different URL formats to be safe
        urls_to_try = [
            f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}",
            f"https://www.googleapis.com/books/v1/volumes?q={isbn}"
        ]
        
        book_data = None
        for url in urls_to_try:
            res = requests.get(url, headers=browser_headers).json()
            if "items" in res:
                book_data = res["items"][0]["volumeInfo"]
                break
    
    if book_data:
        title = book_data.get('title', 'Unknown Title')
        blurb = book_data.get("description", "No description available.")
        
        st.success(f"**Found:** {title}")
        with st.expander("See Book Description"):
            st.write(blurb)

        # --- STEP 3: AI CATEGORIZATION ---
        with st.spinner("Analyzing with AI..."):
            prompt = f"<s>[INST] Analyze this book: '{title}'. Blurb: '{blurb}' \nPick exactly TWO from: {CATEGORIES}. Format as PRIMARY: [Category], SECONDARY: [Category], WHY: [Explanation] [/INST]</s>"
            
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250, "return_full_text": False}}
            response = requests.post(API_URL, headers=headers_hf, json=payload)
            
            if response.status_code == 200:
                st.markdown("### 🏷️ Results")
                st.write(response.json()[0]['generated_text'])
            elif response.status_code == 503:
                st.warning("AI is waking up... give it 10 seconds and try again!")
    else:
        st.error(f"Google Books couldn't find ISBN: {isbn}. Try a different one!")
