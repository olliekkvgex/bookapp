import streamlit as st
import requests

# --- CONFIGURATION ---
# Your provided Hugging Face Access Token
HF_API_KEY = "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"
# Using the Mistral model which is excellent for following instructions
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

CATEGORIES = [
    "Missing Folk", "Messed Up Families", "Don't Trust The Food", 
    "Suspicious Newcomer", "Celebrity & Pop Culture Fiction", "Revenge", 
    "When Cops Need Help", "Hostage", "Whodunnit Mystery", "Sci-Fi", 
    "Domestic Thriller", "Legal/Courtroom Thriller", "Cosy Crime", 
    "Political Thriller", "FemRage", "Weird Girl Fiction", "The Past Comes Back"
]

# --- APP UI ---
st.set_page_config(page_title="Book Genre Detective", page_icon="🕵️‍♀️")
st.title("🕵️‍♀️ Book Genre Detective")
st.write("Enter an ISBN to see which of your custom categories it belongs to.")

isbn = st.text_input("Enter ISBN-13:", placeholder="e.g., 9781838855529")

if isbn:
    # 1. Lookup Book via Google Books (Free)
    with st.spinner("Fetching book details..."):
        google_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        res = requests.get(google_url).json()
    
    if "items" in res:
        info = res["items"][0]["volumeInfo"]
        title = info.get('title', 'Unknown Title')
        blurb = info.get("description", "No description available.")
        st.subheader(f"Analyzing: {title}")
        st.write(f"**Description:** {blurb[:300]}...") # Shows a snippet of the blurb

        # 2. Categorize via Hugging Face (Free)
        with st.spinner("Classifying based on your categories..."):
            # This specific prompt structure helps the AI "understand" your custom list
            prompt = f"""<s>[INST] You are a book expert. Analyze this blurb: "{blurb}"
            
            Pick exactly TWO categories from this list: {', '.join(CATEGORIES)}.
            
            Format your response exactly like this:
            PRIMARY: [Category]
            SECONDARY: [Category]
            WHY: [Short explanation] [/INST]</s>"""
            
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 200, "return_full_text": False}
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()[0]['generated_text']
                st.success("Analysis Complete!")
                st.markdown("---")
                st.write(result)
            elif response.status_code == 503:
                st.warning("The AI model is currently 'loading' on Hugging Face. This happens with free accounts. Please wait 20 seconds and try again!")
            else:
                st.error(f"Error: {response.status_code}")
    else:
        st.error("ISBN not found. Please check the number and try again.")

# --- FOOTER ---
st.markdown("---")
st.caption("Powered by Google Books and Hugging Face Mistral-7B")
