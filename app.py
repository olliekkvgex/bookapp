import streamlit as st
import requests
import time

# --- CONFIGURATION ---
HF_API_KEY = "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"
# SWITCHED TO GOOGLE GEMMA 2: Open access, no gating, high stability
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-9b-it"
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
st.write("Using Google Gemma 2 AI")

# --- STEP 1: ISBN INPUT ---
raw_isbn = st.text_input("Enter ISBN-13:", placeholder="9780141036144")
isbn = raw_isbn.replace("-", "").replace(" ", "").strip()

if isbn:
    with st.spinner("Searching for book..."):
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
        
        st.success(f"**Found:** {title}")
        if 'cover' in book_data:
            st.image(book_data['cover'].get('medium', ''))

        # --- STEP 2: AI CATEGORIZATION ---
        st.markdown("### 🏷️ AI Classification")
        with st.spinner("Analyzing with AI..."):
            # Gemma 2 specific prompt format
            prompt = f"<start_of_turn>user\nYou are a book expert. Analyze the book '{title}' with themes '{clean_subjects}'. \nPick exactly TWO categories from this list: {CATEGORIES}. \nFormat your response as:\nPRIMARY: [Category]\nSECONDARY: [Category]\nWHY: [Brief reason]<end_of_turn>\n<start_of_turn>model\n"
            
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250, "return_full_text": False}}
            
            for attempt in range(3):
                response = requests.post(API_URL, headers=headers_hf, json=payload)
                if response.status_code == 200:
                    result = response.json()[0]['generated_text'].strip()
                    st.info(result)
                    break
                elif response.status_code == 503:
                    st.warning(f"AI is waking up (Attempt {attempt+1}/3)... waiting 20s.")
                    time.sleep(20) 
                else:
                    st.error(f"Error {response.status_code}: Please check your Hugging Face token permissions.")
                    st.code(response.text)
                    break
    else:
        st.error(f"Could not find ISBN: {isbn}")

st.markdown("---")
st.caption("Powered by Open Library & Google Gemma 2")
