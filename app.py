import streamlit as st
import requests

# --- CONFIGURATION ---
# Using the key you provided
GROQ_API_KEY = "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"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# April 2026 Stable Model
MODEL_NAME = "llama-3.1-8b-instant"

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
raw_isbn = st.text_input("Enter ISBN-13:", placeholder="9780141036144")
isbn = raw_isbn.replace("-", "").replace(" ", "").strip()

if isbn:
    with st.spinner("🔍 Finding book..."):
        ol_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        res = requests.get(ol_url).json()
        
    book_key = f"ISBN:{isbn}"
    if book_key in res:
        book_data = res[book_key]
        title = book_data.get('title', 'Unknown Title')
        
        # Safe subject extraction
        raw_subjects = book_data.get('subjects', [])
        subject_names = [s.get('name') if isinstance(s, dict) else str(s) for s in raw_subjects]
        clean_subjects = ", ".join(subject_names[:10])
        
        st.success(f"📖 Found: **{title}**")
        if 'cover' in book_data:
            st.image(book_data['cover'].get('medium', ''), width=150)

        # --- STEP 2: CLEAN AI CLASSIFICATION ---
        st.markdown("---")
        with st.spinner("🧠 AI is analyzing..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # We strictly tell the AI to ONLY provide the three fields
            data = {
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "system", 
                        "content": f"You are a book expert. Pick TWO categories from: {CATEGORIES}. Respond ONLY in this format: PRIMARY: [Category] | SECONDARY: [Category] | WHY: [One sentence reason]"
                    },
                    {
                        "role": "user", 
                        "content": f"Book: {title}. Themes: {clean_subjects}"
                    }
                ],
                "temperature": 0.1 # Low temperature keeps it consistent
            }
            
            response = requests.post(API_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                full_text = response.json()['choices'][0]['message']['content']
                
                # We split the text by the pipes "|" to display nicely
                if "|" in full_text:
                    parts = full_text.split("|")
                    for part in parts:
                        st.subheader(part.strip())
                else:
                    st.info(full_text)
            else:
                st.error(f"AI Error: {response.status_code}")
    else:
        st.error(f"ISBN {isbn} not found.")

st.markdown("---")
st.caption("Stable April 2026 Edition")
