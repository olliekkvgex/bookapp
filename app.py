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
st.write("Using Open Library")

# --- STEP 1: CLEAN THE INPUT ---
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
        
        # --- FIXED SUBJECTS LOGIC ---
        # This part was causing the crash. We now carefully extract the names.
        raw_subjects = book_data.get('subjects', [])
        subject_names = []
        for s in raw_subjects:
            if isinstance(s, dict):
                subject_names.append(s.get('name', ''))
            else:
                subject_names.append(str(s))
        
        clean_subjects = ", ".join(subject_names[:10])
        
        st.success(f"**Found:** {title}")
        if 'cover' in book_data:
            st.image(book_data['cover']['medium'])

        # --- STEP 2: AI CATEGORIZATION ---
        with st.spinner("Analyzing with AI..."):
            prompt = f"""<s>[INST] Analyze this book: '{title}'. 
            Themes: {clean_subjects}
            
            Pick exactly TWO from: {CATEGORIES}. 
            Format as:
            PRIMARY: [Category]
            SECONDARY: [Category]
            WHY: [Brief explanation] [/INST]</s>"""
            
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250, "return_full_text": False}}
            response = requests.post(API_URL, headers=headers_hf, json=payload)
            
            if response.status_code == 200:
                st.markdown("### 🏷️ Results")
                st.write(response.json()[0]['generated_text'])
            elif response.status_code == 503:
                st.warning("AI is waking up... wait 10 seconds and try again!")
            else:
                st.error(f"AI Error: {response.status_code}")
    else:
        st.error(f"Could not find ISBN: {isbn} in Open Library.")
