import streamlit as st
from groq import Groq
import json
import time
import re
import requests
import html
from datetime import date
import urllib.parse

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
    .success-box, .error-box { 
        padding: 25px; 
        border-radius: 20px; 
        margin-bottom: 15px; 
        font-size: 17px; 
        border: none;
        box-shadow: 0 10px 20px rgba(0,0,0,0.02);
    }
    .success-box { background-color: #f4faf6; color: #2d5a3f; border-left: 10px solid #4caf50; }
    .error-box { background-color: #fff9f2; color: #855d21; border-left: 10px solid #ff9800; }
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

st.title("✨ Köklerin Gizemi")
st.write("Sadece verilerin değil, senin hikayenin sessiz yankıları.")

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Ruhsal Kayıtlarını Aç")
    email = st.text_input("E-posta adresin:", placeholder="analizin buraya mühürlenecek...")
    
    col_c, col_y = st.columns(2)
    with col_c:
        cinsiyet = st.selectbox("Cinsiyetin:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
    with col_y:
        dogum_tarihi = st.date_input("Doğum Tarihin", min_value=date(1920, 1, 1), value=date(1990, 1, 1))

    dogum_saati = st.time_input("Doğum Saatin (Yaklaşık)")

    st.write("---")
    kardes_sirasi = st.number_input("Kaçıncı çocuksun? (Düşük/Kayıplar dahil)", min_value=1, step=1)
    aile_evlilik = st.selectbox("EBEVEYNLERİNİN evliliği?", ["Severek evlendiler", "Görücü usulü", "Mantık/Zorunlu evlilik", "Bilmiyorum"])
    dislanan_biri = st.selectbox("AİLEDE dışlanan/hakkı yenen biri var mı?", ["Evet, var", "Hayır, yok", "Emin değilim"])
    agir_yazgi = st.selectbox("AİLEDE ağır bir yazgı (İntihar, iflas, erken ölüm)?", ["Evet, var", "Hayır, yok", "Bazı zorluklar var"])
    kisisel_travma = st.selectbox("SİZİN geçmişinizde derin bir travma/depresyon oldu mu?", ["Evet", "Hayır", "Belirsiz"])
    tikaniklik = st.selectbox("Şifalanmasını istediğin alan:", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    kvkk_onay = st.checkbox("Ruhsal kayıtlarımın işlenmesine ve analiz edilmesine onay veriyorum.")
    submit = st.form_submit_button("Dizimi Başlat")

if submit:
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
    
    if not email or "@" not in email:
        st.error("Lütfen geçerli bir e-posta girin.")
    elif not kvkk_onay:
        st.warning("Onay vermeden dizim başlayamaz.")
    else:
        placeholder = st.empty()
        placeholder.info("Kuantum alan taranıyor, sessiz hikayeler toplanıyor...")

        try:
            # Enerji İmzası
            saat_notu = ""
            if dogum_saati.hour < 6: saat_notu = "Şafak öncesinin derin sessizliği; saklıyı görme ve kökleri şifalandırma gücü."
            elif dogum_saati.hour < 12: saat_notu = "Sabahın yükselen iradesi; tıkanıklıkları cesaretle dönüştürme
