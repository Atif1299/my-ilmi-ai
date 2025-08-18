import streamlit as st
import requests
import pandas as pd

# Define base URL
BASE_URL = "http://localhost:8000"

# Configure page layout
st.set_page_config(layout="wide", page_title="Islamic Knowledge Explorer", page_icon="☪")

# Custom CSS for a more polished look
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# --- Main Application ---
st.title("Islamic Knowledge Explorer ☪")
st.markdown("Analyze Hadith, find related Quranic Ayahs, and explore textual connections.")

# Input area for the Hadith
hadith_input = st.text_area(
    "Enter a Hadith here to begin analysis:",
    height=150,
    placeholder="For example: 'The reward of deeds depends upon the intentions and every person will get the reward according to what he has intended...'"
)

# --- Action Buttons ---
st.write("### Select an Analysis to Perform:")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("Complete Analysis"):
        if hadith_input.strip():
            with st.spinner("Performing comprehensive analysis..."):
                try:
                    url = f"{BASE_URL}/api/quran/get_hadith_complete_info"
                    payload = {"query": hadith_input}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.session_state.result = response.json()
                        st.session_state.result_type = "complete_info"
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter a Hadith.")

with col2:
    if st.button("Find Related Ayahs"):
        if hadith_input.strip():
            with st.spinner("Finding related Ayahs..."):
                try:
                    url = f"{BASE_URL}/api/quran/get_hadith_related_ayahs"
                    payload = {"query": hadith_input}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.session_state.result = response.json()
                        st.session_state.result_type = "related_ayahs"
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter a Hadith.")

with col3:
    if st.button("Extract Narrators"):
        if hadith_input.strip():
            with st.spinner("Extracting narrators..."):
                try:
                    url = f"{BASE_URL}/api/quran/get_hadith_narators"
                    payload = {"query": hadith_input}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.session_state.result = response.json()
                        st.session_state.result_type = "narrators"
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter a Hadith.")

with col4:
    if st.button("Extract Hadith Content"):
        if hadith_input.strip():
            with st.spinner("Extracting Hadith content..."):
                try:
                    url = f"{BASE_URL}/api/quran/get_hadith_content"
                    payload = {"query": hadith_input}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.session_state.result = response.json()
                        st.session_state.result_type = "hadith_content"
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter a Hadith.")

with col5:
    if st.button("Analyze Keywords"):
        if hadith_input.strip():
            with st.spinner("Analyzing keywords..."):
                try:
                    url = f"{BASE_URL}/api/quran/keyword_search"
                    payload = {"query": hadith_input}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.session_state.result = response.json()
                        st.session_state.result_type = "keyword_search"
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter a Hadith.")

with col6:
    if st.button("Highlight Keywords"):
        if hadith_input.strip():
            with st.spinner("Highlighting keywords..."):
                try:
                    url = f"{BASE_URL}/api/quran/highlight_keywords"
                    payload = {"query": hadith_input}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.session_state.result = response.json()
                        st.session_state.result_type = "keyword_highlight"
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter a Hadith.")

# --- Display Results ---
if 'result' in st.session_state and 'result_type' in st.session_state:
    st.markdown("---")
    st.header("Analysis Results")
    result_type = st.session_state.result_type
    data = st.session_state.result

    if result_type == "complete_info":
        st.subheader("🔍 Comprehensive Hadith Analysis")
        
        # Display Extracted Hadith Content
        st.write("### 📜 Extracted Hadith Content:")
        st.info(data.get("hadith_content", "Not available."))
        
        # Display Extracted Narrators
        st.write("### 👥 Extracted Narrators:")
        narrators = data.get("narrators", [])
        if narrators:
            for i, narrator in enumerate(narrators, 1):
                st.write(f"{i}. {narrator}")
        else:
            st.write("No narrators found.")
        
        # Display Related Quranic Ayahs with Highlighted Keywords
        st.write("### 📖 Related Quranic Ayahs (with Highlighted Keywords):")
        related_ayahs = data.get("related_ayahs", [])
        if related_ayahs:
            for i, ayah in enumerate(related_ayahs, 1):
                with st.expander(f"{i}. Surah {ayah['surah_name_english']} - Ayah {ayah['aya_number']} (Score: {ayah['score']:.2f})"):
                    if ayah.get('arabic_diacritics'):
                        st.markdown(f"**Arabic:** {ayah['arabic_diacritics']}")
                    
                    # Display English translation with highlighted keywords
                    st.markdown(f"**English Translation:** {ayah['english_translation']}")
        else:
            st.write("No related ayahs found.")
        
        # Display Keyword Analysis
        st.write("### 🔑 Keywords Found in Ayahs:")
        keywords = data.get("keywords", {})
        found_keywords = keywords.get("found_keywords", [])
        total_keywords = keywords.get("total_keywords_found", 0)
        
        if found_keywords:
            st.info(f"Found {total_keywords} unique keywords from the database highlighted in the ayahs")
            # Display keywords as colorful badges
            keyword_html = ""
            for keyword in found_keywords:
                keyword_html += f'<span style="background-color: #4CAF50; color: white; padding: 4px 8px; margin: 2px; border-radius: 12px; font-size: 12px; display: inline-block;">{keyword}</span> '
            st.markdown(keyword_html, unsafe_allow_html=True)
        else:
            st.info("No keywords from the database were found in the related ayahs.")

    elif result_type == "related_ayahs":
        st.subheader("Related Quranic Ayahs")
        results = data.get("results", [])
        if results:
            for i, ayah in enumerate(results, 1):
                with st.expander(f"{i}. Surah {ayah['surah_name_english']} - Ayah {ayah['aya_number']} (Score: {ayah['score']:.2f})"):
                    if ayah.get('arabic_diacritics'):
                        st.markdown(f"*Arabic:* {ayah['arabic_diacritics']}")
                    
                    # Display normal English translation (NO highlighting for Find Related Ayahs)
                    st.markdown(f"*English Translation:* {ayah['english_translation']}")
        else:
            st.write("No related ayahs found.")

    elif result_type == "narrators":
        st.subheader("Extracted Narrators")
        st.json(data.get("narrators", []))

    elif result_type == "hadith_content":
        st.subheader("Extracted Hadith Content")
        st.info(data.get("hadith_content", "Not available."))

    elif result_type == "keyword_search":
        st.subheader("Keyword Search Results")
        
        # Display query information
        query = data.get("query", "")
        total_matches = data.get("total_matches", 0)
        matched_ayats = data.get("matched_ayats", [])
        
        st.info(f"Search Query: **{query}** | Total Matches: **{total_matches}**")
        
        if matched_ayats:
            st.write(f"Showing top {len(matched_ayats)} matching ayats with **highlighted keywords**:")
            
            for i, ayah in enumerate(matched_ayats, 1):
                with st.expander(f"{i}. Surah {ayah['surah_name_english']} - Ayah {ayah['aya_number']} (Score: {ayah.get('score', 0):.2f})"):
                    if ayah.get('arabic_diacritics'):
                        st.markdown(f"**Arabic:** {ayah['arabic_diacritics']}")
                    
                    # Display highlighted English translation
                    st.markdown(f"**English Translation:** {ayah['english_translation']}")
                    
        else:
            st.write("No matching ayats found for your search query.")
        
        if data.get("error"):
            st.error(f"Search Error: {data['error']}")

    elif result_type == "keyword_highlight":
        st.subheader("Keywords Highlighted in Text")
        
        # Display original text
        st.write("**Original Text:**")
        st.text_area("", value=data.get("original_text", ""), height=100, disabled=True)
        
        # Display highlighted text
        st.write("**Text with Highlighted Keywords:**")
        highlighted_text = data.get("highlighted_text", "")
        st.markdown(highlighted_text, unsafe_allow_html=True)
        
        # Display found keywords
        found_keywords = data.get("found_keywords", [])
        if found_keywords:
            st.write("**Found Keywords:**")
            # Display keywords as colorful badges
            keyword_html = ""
            for keyword in found_keywords:
                keyword_html += f'<span style="background-color: #ffeb3b; color: #333; padding: 4px 8px; margin: 2px; border-radius: 12px; font-size: 12px; display: inline-block;">{keyword}</span> '
            st.markdown(keyword_html, unsafe_allow_html=True)
            st.write(f"Total keywords found: {len(found_keywords)}")
        else:
            st.info("No keywords from the database were found in the text.")

# --- Footer ---
st.markdown("---")
st.markdown("Developed with ❤ by NexusBerry Training & Solutions")