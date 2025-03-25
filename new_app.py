import streamlit as st
import google.generativeai as genai
from datetime import datetime


# Function to get summary using Google Gemini API
def get_summary_from_gemini(text, mode, length_factor):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = (
            f"Summarize the following text in a {mode.lower()} manner. "
            f"The summary should be approximately {int(length_factor * 100)}% of the original content.\n\n{text}"
        )

        response = model.generate_content(prompt)

        # Properly extract text from API response
        if hasattr(response, "text") and response.text.strip():
            return response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            return response.candidates[0].text.strip() if response.candidates[0].text else "⚠️ No summary generated."
        elif hasattr(response, "parts") and response.parts:
            return response.parts[0].text.strip() if response.parts[0].text else "⚠️ No summary generated."
        else:
            return "⚠️ No valid summary received from the API."

    except genai.GenerativeAIError as e:
        return f"⚠️ Gemini API Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected Error: {str(e)}"

# Initialize session state
def init_session_state():
    if "summary_mode" not in st.session_state:
        st.session_state.summary_mode = "Concise"
    if "length_factor" not in st.session_state:
        st.session_state.length_factor = 0.5
    if "history" not in st.session_state:
        st.session_state.history = []

init_session_state()

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

    /* Small Dark Header - Responsive */
    .custom-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: #262730;
        padding: 10px 20px;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        z-index: 100;
        transition: all 0.3s ease-in-out;
    }

    /* Texeer Title Default Position */
   /* Default position when sidebar is closed */
.custom-header h1 {
    color: white;
    font-size: 22px;
    font-weight: bold;
    margin: 0;
    margin-left: 50px; /* Start a bit to the right */
    transition: margin-right 0.3s ease-in-out;
}

/* Adjust position when sidebar is open */
[data-testid="stSidebar"][aria-expanded="true"] ~ [data-testid="stHeader"] .custom-header h1 {
    margin-right: 300px; /* Align with sidebar edge when opened */
}
    /* Light Mode Input & Buttons */
    .stTextArea textarea {
        background-color: #ffffff;  /* White background */
        color: black;               /* Text color */
        border: 2px solid #ccc;     /* Slightly dark border */
        padding: 10px;
        font-size: 16px;
        font-family: Arial, sans-serif; /* Professional Font */
    }
       
    .stButton button {
    background-color: white !important;  /* Set button background to white */
    color: black !important;  /* Keep text black */
    border: 1px solid #ccc;  /* Light border for a clean look */
    padding: 8px 12px;  /* Adjust padding for better spacing */
    border-radius: 5px;  /* Slightly rounded edges */
    box-shadow: none;  /* Remove any default shadows */
}

.stButton button:hover {
    background-color: #f0f0f0;  /* Light gray hover effect */
    color: black;
}

.stTextArea textarea {
    background-color: white !important;  /* Remove unwanted background */
    color: black !important;
    border: 1px solid #ccc;
    padding: 8px;
    border-radius: 5px;
}

    /* Professional Placeholder */
    .stTextArea textarea::placeholder {
        color: #666;  /* Darker gray for better visibility */
        font-style: normal;
        font-weight: 500;
        font-size: 15px;
        font-family: Arial, sans-serif; /* Sleek Font */
    }

    /* Blinking Cursor Effect */
    @keyframes blink {
        50% { opacity: 0; }
    }

    .stTextArea textarea::before {
        content: "|";
        font-size: 18px;
        color: black;
        font-weight: bold;
        display: inline-block;
        animation: blink 1s infinite;
    }

    /* Light Sidebar Theme */
    .stSidebar, .stSidebar div {
        background-color: #f8f9fa !important;
        color: black !important;
    }

    /* 🚀 Move Container Upward */
    .block-container { 
        padding-top: 10px !important;  /* Decreased from 60px */
        margin-top: -40px !important;  /* Move up more */
    }
    </style>
"""

st.set_page_config(page_title="Texeer - AI Summarizer", layout="wide", initial_sidebar_state="collapsed")
st.markdown(custom_css, unsafe_allow_html=True)

# Custom Responsive Header
st.markdown(
    """
    <div class="custom-header">
        <h1>Texeer - AI Summarizer</h1>
    </div>
    <div class="custom-header h1">
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

if st.button("Summarize"):
    if text.strip():
        with st.spinner("Generating summary..."):
            summary = get_summary_from_gemini(text, st.session_state.summary_mode, st.session_state.length_factor)
            
            if summary.startswith("⚠️"):
                st.error("❌ Error: Unable to generate summary. Please try again!")
            else:
                st.success("✅ Summary Generated Successfully!")

                # Display summary
                st.markdown("### Summary:")
                st.markdown(summary)

                # Save to history
                st.session_state.history.append({
                    "title": text[:30] + "...",
                    "summary": summary,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })

                # **Auto-scroll to summary (Ensures the page moves to the bottom)**
                st.markdown(
                    """
                    <script>
                        function scrollToBottom() {
                            var scrollHeight = document.documentElement.scrollHeight;
                            window.scrollTo({ top: scrollHeight, behavior: 'smooth' });
                        }
                        setTimeout(scrollToBottom, 500);
                    </script>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.markdown(
            """
            <div style="color: red; font-weight: bold;">
                ⚠️ Please enter some text before summarizing.
            </div>
            """, 
            unsafe_allow_html=True
        )
