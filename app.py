import streamlit as st
import google.generativeai as genai

def get_summary_from_gemini(text):
    """Uses Gemini AI to generate a summary."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Use latest model
        response = model.generate_content(f"Summarize the following text:\n\n{text}")
        
        if hasattr(response, "text"):
            return response.text  # Extract summary correctly
        return "⚠️ No summary generated."
    except Exception as e:
        return f"⚠️ Gemini API Error: {str(e)}"

# Streamlit UI Setup
st.set_page_config(page_title="Gemini AI Summarizer", page_icon="📝", layout="wide")
st.title("🚀 Gemini AI-Powered Text Summarizer")
st.write("Generate intelligent, concise summaries using Google's Gemini AI.")

# User Input
text = st.text_area("✍️ Enter your text below:", height=300, placeholder="Type or paste your text here...")

# Summarize Button
if st.button("Summarize ✍️"):
    if text.strip():
        with st.spinner("🔄 Generating summary..."):
            summary = get_summary_from_gemini(text)

            if summary.startswith("⚠️") or summary.startswith("🚨"):
                st.error(summary)
            else:
                st.success("✅ Summary Generated Successfully!")
                st.write("### 📜 Summary:")
                st.markdown(summary)
    else:
        st.warning("⚠️ Please enter some text before summarizing.")

# Footer
st.markdown("---")
st.markdown("💡 **Powered by Google Gemini AI** | 🔗 [Learn More](https://ai.google.dev/)")
