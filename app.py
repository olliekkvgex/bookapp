import streamlit as st
import requests
import time

# --- CONFIGURATION ---
# Replace this with your key from console.groq.com
GROQ_API_KEY = "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"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# These are the current stable models for April 2026
PRIMARY_MODEL = "llama-3.1-8b-instant"
FALLBACK_MODEL = "llama-3.3-70b-versatile"

CATEGORIES = [
    "Missing Folk", "Messed Up Families", "Don't Trust The Food", 
    "Suspicious Newcomer", "Celebrity & Pop Culture Fiction", "Revenge", 
    "When Cops Need Help", "Hostage", "Whodunnit Mystery", "Sci-Fi", 
    "Domestic Thriller", "Legal/Courtroom Thriller", "Cosy Crime", 
    "Political Thriller", "FemRage", "Weird Girl Fiction", "The Past Comes Back"
]

st.set_page_config(page_title="Book Genre Detective", page_icon="🕵️‍♀️")
st.title("🕵️‍♀️ Book Genre Detective")

# --- STEP 1: ISBN INPUT ---
raw_isbn = st.text_input("Enter ISBN-13 (e.g., 9780141036144):")
isbn = raw_isbn.replace("-", "").replace(" ", "").strip()

if isbn:
    with st.spinner("🔍 Fetching book details..."):
        ol_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        try:
            res = requests.get(ol_url).json()
            book_key = f"ISBN:{isbn}"
            
            if book_key in res:
                book_data = res[book_key]
                title = book_data.get('title', 'Unknown Title')
                
                # Extract subject strings safely
                raw_subjects = book_data.get('subjects', [])
                subject_names = [s.get('name') if isinstance(s, dict) else str(s) for s in raw_subjects]
                clean_subjects = ", ".join(subject_names[:10])
                
                st.success(f"📖 Found: **{title}**")
                if 'cover' in book_data:
                    st.image(book_data['cover'].get('medium', ''), width=200)

                # --- STEP 2: GROQ AI CLASSIFICATION ---
                st.markdown("### 🏷️ AI Analysis")
                
                def call_groq(model_name):
                    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": f"Categorize this book into exactly TWO of these categories: {CATEGORIES}. Format as: PRIMARY: [Cat], SECONDARY: [Cat], WHY: [Reason]"},
                            {"role": "user", "content": f"Title: {title}. Themes: {clean_subjects}"}
                        ],
                        "temperature": 0.5
                    }
                    return requests.post(API_URL, headers=headers, json=payload)

                with st.spinner("🧠 Categorizing..."):
                    # Attempt 1: Primary Model
                    response = call_groq(PRIMARY_MODEL)
                    
                    if response.status_code == 200:
                        st.info(response.json()['choices'][0]['message']['content'])
                    else:
                        # Attempt 2: Fallback Model
                        st.warning("Primary model busy, trying fallback...")
                        response = call_groq(FALLBACK_MODEL)
                        if response.status_code == 200:
                            st.info(response.json()['choices'][0]['message']['content'])
                        else:
                            st.error(f"AI Connection Error ({response.status_code}). Please verify your Groq API Key.")
            else:
                st.error("No book found for this ISBN. Please check the number.")
        except Exception as e:
            st.error(f"Technical error: {e}")

st.markdown("---")
st.caption("v2.0 Stable - 2026 Edition")
