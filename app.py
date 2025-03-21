import streamlit as st
import requests
from summa import summarizer
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk

# Ensure necessary NLTK downloads
nltk.download('punkt')

# Flask API URL (Ensure Flask is running on this address)
API_URL = "http://127.0.0.1:5000/summarize"

def get_summary_from_backend(text, style):
    """Sends text to the Flask backend for summarization."""
    try:
        response = requests.post(API_URL, json={"text": text, "style": style})
        if response.status_code == 200:
            result = response.json()
            return result.get("summary", "⚠️ No summary generated.")
        else:
            return f"⚠️ Error: {response.json().get('error', 'Unknown error')}"
    except requests.exceptions.ConnectionError:
        return "🚨 Could not connect to the backend. Make sure Flask is running."

def train_word2vec(text):
    """Trains a Word2Vec model on tokenized text."""
    try:
        sentences = [word_tokenize(sentence) for sentence in sent_tokenize(text)]
        model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
        return model
    except Exception as e:
        return str(e)

# Streamlit UI with Sidebar
st.set_page_config(page_title="AI Text Summarizer", page_icon="📝", layout="wide")
st.sidebar.title("⚡ AI Text Summarizer")
st.sidebar.write("Summarize long texts quickly with AI.")

# Sidebar Options
summary_style = st.sidebar.radio("📌 Select Summary Style:", ["Concise", "Balanced", "Detailed"], index=1)
ratio = st.sidebar.slider("Summarization fraction", min_value=0.1, max_value=1.0, value=0.4, step=0.05)

# Main Page
st.title("🚀 AI-Powered Text Summarizer")
st.write("Generate intelligent, concise summaries using advanced NLP with a sleek UI.")

# User Input
text = st.text_area("✍️ Enter your text below:", height=300, placeholder="Type or paste your text here...")

# Summarize Button
if st.button("Summarize ✍️"):
    if text.strip():
        with st.spinner("Generating summary..."):
            # Generate summary using summa with an increased ratio
            summary = summarizer.summarize(text, ratio=ratio, language="english")
            
            if not summary.strip():
                st.error("⚠️ No summary generated. Try increasing the ratio or providing a longer text.")
            else:
                st.success("✅ Summary Generated Successfully!")
                st.write("### 📜 Summary:")
                st.markdown(summary)  

                # Train Word2Vec and Display Similar Words
                st.write("### 🔍 Word2Vec Similar Words:")
                word2vec_model = train_word2vec(text)
                
                if isinstance(word2vec_model, Word2Vec):
                    sample_words = word_tokenize(summary)[:3]  # Take first 3 words as samples
                    for sample_word in sample_words:
                        try:
                            similar_words = word2vec_model.wv.most_similar(sample_word, topn=3)
                            st.write(f"Words similar to '{sample_word}':")
                            for word, score in similar_words:
                                st.write(f"- {word} (score: {score:.2f})")
                        except KeyError:
                            st.write(f"⚠️ The word '{sample_word}' is not in the Word2Vec vocabulary.")
                else:
                    st.write("⚠️ Could not train Word2Vec model due to input constraints.")
    else:
        st.warning("⚠️ Please enter some text before summarizing.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Pro Tip:** Use *Detailed* mode for in-depth summaries and *Concise* for quick insights!")
