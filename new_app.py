import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Configure Google Gemini AI
API_KEY = "AIzaSyCOHxWJjmdGhxEN64gDepDxuLBDenWDXNA"
genai.configure(api_key=API_KEY)

# Initialize Gemini model
def get_summary_from_gemini(text, mode, length_factor):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Summarize the following text in a {mode.lower()} manner with about {int(length_factor * 100)}% of the original content:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, "text") else "⚠️ No summary generated."
    except Exception as e:
        return f"⚠️ Gemini API Error: {str(e)}"

# Initialize session state
def init_session_state():
    if "summary_mode" not in st.session_state:
        st.session_state.summary_mode = "Concise"
    if "length_factor" not in st.session_state:
        st.session_state.length_factor = 0.5
    if "history" not in st.session_state:
        st.session_state.history = []

init_session_state()

# Custom CSS for Small Dark Header
custom_css = """
    <style>
    /* Hide Default Streamlit Header & Footer */
    header, footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none !important; }

    /* Background & Dark Mode */
    body, .stApp { 
        background: #f8f9fa; 
        color: black; 
    }

    /* Small Dark Header */
    .custom-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: #262730;
        padding: 10px 0;
        text-align: center;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        z-index: 100;
    }
    .custom-header h1 {
        color: white;
        font-size: 22px;
        font-weight: bold;
        margin: 0;
    }

    /* Light Mode Input & Buttons */
    .stTextArea textarea, .stButton button {
        background-color: #f0f0f0;
        color: black;
    }
    .stSlider > div > div, .stRadio div label { color: black !important; }
    
    /* Light Sidebar Theme */
    .stSidebar, .stSidebar div {
        background-color: #f8f9fa !important;
        color: black !important;
    }
    </style>
"""

st.set_page_config(page_title="Texeer - AI Summarizer", layout="wide")
st.markdown(custom_css, unsafe_allow_html=True)

# Custom Small Header
st.markdown(
    """
    <div class="custom-header">
        <h1>Texeer - AI Summarizer</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Features
with st.sidebar:
    st.subheader("Summary Options")
    st.session_state.summary_mode = st.radio(
        "Select summary style:", ["Concise", "Brief", "Detailed"], 
        index=["Concise", "Brief", "Detailed"].index(st.session_state.summary_mode)
    )
    st.session_state.length_factor = st.slider("Summary Length:", 0.2, 1.0, st.session_state.length_factor, 0.1)
    
    st.markdown("---")
    st.subheader("Additional Features")
    
    if st.button("Clear History", key="clear_history", help="Clear all summary history"):
        st.session_state.history = []
        st.success("History cleared successfully!")

    if st.button("Export History", key="export_history", help="Export summary history as a text file"):
        if st.session_state.history:
            history_text = "\n\n".join([
                f"Title: {item['title']}\nSummary: {item['summary']}\nTimestamp: {item['timestamp']}"
                for item in st.session_state.history
            ])
            st.download_button(label="Download History", data=history_text, file_name="summary_history.txt", mime="text/plain")
        else:
            st.warning("No history available to export.")

    st.markdown("---")
    st.subheader("Recent Summaries")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-5:]):
            with st.expander(item["title"]):
                st.markdown(item["summary"])
    else:
        st.write("No summaries available.")

# Add spacing for header
st.markdown("<br><br><br>", unsafe_allow_html=True)

# Text Input
text = st.text_area("", height=300, placeholder="Type or paste your text here...")

# File Upload Feature
uploaded_file = st.file_uploader("Upload a file (TXT only)", type=["txt"])
if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")

# Summarize Button
if st.button("Summarize"):
    if text.strip():
        with st.spinner("Generating summary..."):
            summary = get_summary_from_gemini(text, st.session_state.summary_mode, st.session_state.length_factor)
            
            if summary.startswith("⚠️"):
                st.markdown(
                    """
                    <div style="color: red; font-weight: bold;">
                        ❌ Error: Unable to generate summary. Please try again!
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="color: green; font-weight: bold;">
                        ✅ Summary Generated Successfully!
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

                # Display summary
                st.markdown("### Summary:")
                st.markdown(summary)

                # Display Word Count
                word_count = len(summary.split())
                st.markdown(
                    f"""
                    <div style="font-weight: bold;">
                        📌 Word Count: {word_count}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

                # Save to history
                st.session_state.history.append({
                    "title": text[:30] + "...",
                    "summary": summary,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
    else:
        st.markdown(
            """
            <div style="color: red; font-weight: bold;">
                ⚠️ Please enter some text before summarizing.
            </div>
            """, 
            unsafe_allow_html=True
        )
