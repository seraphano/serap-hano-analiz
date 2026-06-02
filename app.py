import streamlit as st
from groq import Groq
import json
import time
import requests
import html
from datetime import date
import urllib.parse
import random

# 1. Page Config
st.set_page_config(page_title="Serap Hano Akademi | Ruhun Aynası", layout="centered")

# --- CSS: ŞİİRSEL VE DERİN TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .main-text { 
        font-size: 21px; 
        line-height: 2.4; 
        color: #1a252f; 
        background: #ffffff; 
        padding: 50px; 
        border-radius: 40px; 
        border: none; 
        margin-bottom: 30px; 
        white-space: pre-wrap; 
        box-shadow: 0 20px 60px rgba(0,0,0,0.05);
        font-family: 'Georgia', serif;
    }
    .success-box, .error-box, .kader-box, .fragman-box, .hikaye-box, .mektup-box { 
        padding: 25px; 
        border-radius: 20px; 
        margin-bottom: 15px; 
        font-size: 17px; 
        border: none;
        box-shadow: 0 10px 20px rgba(0,0,0,0.02);
    }
    .success-box { background-color: #f4faf6; color: #2d5a3f; border-left: 10px solid #4caf50; }
    .error-box { background-color: #fff9f2; color: #855d21; border-left: 10px solid #ff9800; }
    .kader-box { background-color: #1a1a2e; color: #e94560; border-left: 10px solid #e94560; font-weight: bold; font-style: italic; font-size: 22px; text-align: center; }
    .fragman-box { background-color: #0f0f0f; color: #e5e5e5; border-left: 10px solid #e50914; font-family: 'Courier New', monospace; }
    .hikaye-box { background-color: #f5f0e6; color: #4a4031; border-left: 10px solid #8b7355; font-style: italic; }
    .mektup-box { background-color: #f0f4f8; color: #2c3e50; border-left: 10px solid #3498db; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- BAĞLANTI ---
client = None
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]
else:
    st.error("Sistem ayarları eksik!")

# --- SESSION STATE TANIMLAMALARI ---
if "analiz_verisi" not in st.session_state:
    st.session_state.analiz_verisi = None
if "ruh_yasi" not in
