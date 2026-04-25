from app.main import create_streamlit_app, Chain, Portfolio, clean_text
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Check API key
api_key = None
try:
    api_key = st.secrets.get("GROQ_API_KEY")
except:
    pass

if not api_key:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Please add GROQ_API_KEY to Secrets (Settings → Secrets)")
    st.stop()

# Initialize and run
chain = Chain()
portfolio = Portfolio()
st.set_page_config(layout="wide", page_title="Job Application Assistant", page_icon="📧")
create_streamlit_app(chain, portfolio, clean_text)
