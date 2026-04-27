import streamlit as st
import requests
import time

# --- CONFIGURATION ---
HF_API_KEY = "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"
# UPDATED URL: Using v0.3 which is currently active and stable
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
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

raw_isbn = st.text_input("Enter ISBN-13:", placeholder="9780141036144")
isbn = raw_isbn.replace("-", "").replace(" ", "").strip()

if isbn:
    with st.spinner("Searching Open Library..."):
        ol_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        res = requests.get(ol_url).json()
        
    book_key = f"ISBN:{isbn}"
    if book_key in res:
        book_data = res[book_key]
        title = book_data.get('title', 'Unknown Title')
        
        # Clean subjects extraction
        raw_subjects = book_data.get('subjects', [])
        subject_names = [s.get('name') if isinstance(s, dict) else str(s) for s in raw_subjects]
        clean_subjects = ", ".join(subject_names[:10])
        
        st.success(f"**Found:** {title}")
        if 'cover' in book_data:
            st.image(book_data['cover'].get('medium', ''))

        # --- STEP 2: AI CATEGORIZATION WITH RETRIES ---
        st.markdown("### 🏷️ AI Classification")
        with st.spinner("Connecting to AI..."):
            prompt = f"<s>[INST] Analyze the book '{title}' with themes '{clean_subjects}'. Pick TWO categories from this list: {CATEGORIES}. Format: PRIMARY: [Cat], SECONDARY: [Cat], WHY: [Reason] [/INST]</s>"
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250}}
            
            # Try 3 times
            for attempt in range(3):
                response = requests.post(API_URL, headers=headers_hf, json=payload)
                if response.status_code == 200:
                    try:
                        result = response.json()[0]['generated_text'].split('[/INST]')[-1]
                        st.write(result)
                    except:
                        st.write(response.json())
                    break
                elif response.status_code == 503:
                    st.info(f"AI is loading (Attempt {attempt+1}/3)... waiting 15s")
                    time.sleep(15) 
                else:
                    st.error(f"Error: {response.status_code}")
                    break
    else:
        st.error(f"Could not find ISBN: {isbn}")
