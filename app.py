import streamlit as st
import requests

# --- CONFIGURATION ---
# 1. PASTE YOUR GROQ API KEY HERE
GROQ_API_KEY = "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"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

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

        # --- STEP 2: GROQ AI CATEGORIZATION ---
        st.markdown("### 🏷️ AI Classification")
        with st.spinner("Analyzing with Groq (Light-speed)..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system", 
                        "content": f"You are a book expert. Categorize the book into TWO of these: {CATEGORIES}. Format: PRIMARY: [Cat], SECONDARY: [Cat], WHY: [Reason]"
                    },
                    {
                        "role": "user", 
                        "content": f"Title: {title}. Themes: {clean_subjects}"
                    }
                ]
            }
            
            response = requests.post(API_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                st.info(result)
            else:
                st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.error(f"Could not find ISBN: {isbn}")
