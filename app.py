import streamlit as st
import requests
import time

# --- CONFIGURATION ---
HF_API_KEY = "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"
# Meta Llama 3 8B - Usually the most stable free model on HF
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
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
st.write("Using Meta Llama 3 AI")

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

        # --- STEP 2: LLAMA 3 AI CATEGORIZATION ---
        st.markdown("### 🏷️ AI Classification")
        with st.spinner("Analyzing with Llama 3..."):
            # Llama 3 specific instruction format (the <|tags|>)
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are a book categorization expert. You must pick TWO categories from this list: {CATEGORIES}.<|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Analyze the book '{title}' with these themes: {clean_subjects}. 
            Format your response as:
            PRIMARY: [Category]
            SECONDARY: [Category]
            WHY: [Brief reason]
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
            
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 200, "return_full_text": False}}
            
            for attempt in range(3):
                response = requests.post(API_URL, headers=headers_hf, json=payload)
                if response.status_code == 200:
                    # Llama 3 response cleaning
                    result = response.json()[0]['generated_text'].strip()
                    st.info(result)
                    break
                elif response.status_code == 503:
                    st.warning(f"Llama 3 is loading (Attempt {attempt+1}/3)... 20s wait.")
                    time.sleep(20) 
                else:
                    st.error(f"Error {response.status_code}: Model might be private or address moved.")
                    st.code(response.text)
                    break
    else:
        st.error(f"Could not find ISBN: {isbn}")

st.markdown("---")
st.caption("Powered by Open Library & Meta Llama 3")
