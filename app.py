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
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 18px; border-radius: 12px; border-left: 6px solid #4caf50; margin-bottom: 10px; color: #2e7d32; font-size: 15px; }
    .error-box { background-color: #fff3e0; padding: 18px; border-radius: 12px; border-left: 6px solid #ff9800; margin-bottom: 10px; color: #e65100; font-size: 15px; }
    .main-text { font-size: 19px; line-height: 2.2; color: #2c3e50; background: #fff; padding: 40px; border-radius: 25px; border: 1px solid #eee; margin-bottom: 25px; white-space: pre-wrap; box-shadow: 0 10px 30px rgba(0,0,0,0.03); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- BAĞLANTI ---
client = None
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]
else:
    st.error("API anahtarı eksik!")

st.title("✨ Köklerin Gizemi")
st.write("Sistemik mirasın ve ruhsal tıkanıklıkların bilge analizi.")

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Ruhsal Kayıtlarınızı Açın")
    email = st.text_input("E-posta adresiniz:", placeholder="analiziniz mühürlenecek...")
    
    col_c, col_y = st.columns(2)
    with col_c:
        cinsiyet = st.selectbox("Cinsiyetiniz:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
    with col_y:
        dogum_tarihi = st.date_input("Doğum Tarihiniz", min_value=date(1920, 1, 1), value=date(1990, 1, 1))

    dogum_saati = st.time_input("Doğum Saatiniz (Yaklaşık)")

    st.write("---")
    kardes_sirasi = st.number_input("Kaçıncı çocuksunuz? (Kayıplar/Düşükler dahil)", min_value=1, step=1)
    aile_evlilik = st.selectbox("EBEVEYNLERİNİZİN evlilik temeli?", ["Severek evlendiler", "Görücü usulü", "Mantık/Zorunlu evlilik", "Bilmiyorum"])
    dislanan_biri = st.selectbox("AİLENİZDE dışlanmış veya hakkı yenen biri var mı?", ["Evet, var", "Hayır, yok", "Emin değilim"])
    agir_yazgi = st.selectbox("AİLE GEÇMİŞİNDE ağır yazgı (İntihar, göç, iflas, erken ölüm)?", ["Evet, var", "Hayır, yok", "Bazı zorluklar var"])
    kisisel_travma = st.selectbox("SİZİN geçmişinizde derin bir travma/depresyon oldu mu?", ["Evet", "Hayır", "Belirsiz"])
    tikaniklik = st.selectbox("Şifalanmasını istediğiniz alan:", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    kvkk_onay = st.checkbox("Verilerimin işlenmesine ve kaydedilmesine onay veriyorum.")
    submit = st.form_submit_button("Dizimi Başlat")

# --- ANALİZ ---
if submit:
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
    
    if not email or "@" not in email:
        st.error("Geçerli bir e-posta girin.")
    elif not kvkk_onay:
        st.warning("KVKK onayını işaretleyin.")
    elif yas < 15:
        st.warning("Analiz 15 yaş ve üzeri içindir.")
    else:
        placeholder = st.empty()
        placeholder.info("Kökler taranıyor, analiz mühürleniyor...")

        try:
            # SAAT MEKANİZMASI (Prompt'a yedirilecek)
            saat_vurgusu = ""
            if dogum_saati.hour < 6: saat_vurgusu = "Şafak öncesi sessizliği; ailenin gizli yüklerini çözme gücü."
            elif dogum_saati.hour < 12: saat_vurgusu = "Sabah enerjisi; sistemik tıkanıklıkları eylemle aşma potansiyeli."
            else: saat_vurgusu = "Gece/Akşam derinliği; bilinçaltı rehberliği ve ruhsal köprü olma misyonu."

            # V8 MASTER PROMPT
            prompt_metni = f"""
            ROL: Sen Serap Hano'sun. %100 Türkçe konuşan, sarsıcı ve bilge bir Sistem Dizimi uzmanısın.
            
            KÖK BİLGİLER (BUNLAR DANIŞANIN DEĞİL, AİLESİNİN HİKAYESİDİR):
            - Anne-Baba Evliliği: {aile_evlilik}
            - Ailede Dışlanan: {dislanan_biri}
            - Atasal Yazgı/Travma: {agir_yazgi}
            
            DANIŞAN BİLGİLERİ (BUNLAR SENİN ÖZNENDİR):
            - Yaş/Cinsiyet: {yas} yaşında {cinsiyet}
            - Kardeş Sırası: {kardes_sirasi}
            - Kişisel Travma: {kisisel_travma}
            - Tıkanıklık Alanı: {tikaniklik}
            - Enerji İmzası (Saat): {saat_vurgusu}

            SİSTEMİK ANALİZ KURALLARI:
            1. ÖZNE KONTROLÜ: Ebeveyn evliliğini veya dışlanan birini sakın DANIŞANIN KENDİSİ yaşamış gibi yazma. Onlar köklerdir.
            2. MEKANİZMA: Tıkanıklık ile atasal yük arasında neden-sonuç bağı kur. "Ataların şunu yaşamış, bu yüzden sende bugün şu kilitlenme oluyor" de.
            3. YASAKLAR: "loading", "experience", "only", "possible", "mümkün", "yolculuk", "iç ışık", "gizem".
            4. ASLA yaş, kardeş sırası veya verileri rakamla yazma. Onları metnin ruhuna gizle.

            JSON ÇIKTI:
            {{
                "isik": ["Sistemik Güç 1", "Sistemik Güç 2"],
                "golge": ["Taşınan Atasal Yük 1", "Taşınan Atasal Yük 2"],
                "analiz": "150-200 kelimelik, edebi, sarsıcı ve sadece 'sen' diliyle yazılmış analiz.",
                "soru": "Ruhsal bir yüzleşme sorusu.",
                "cta": "Serap Hano Akademi davet cümlesi."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen sadece Türkçe konuşan, usta bir edebiyatçısın. İngilizce kelime kullanman imkansızdır."},
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            res_data = json.loads(completion.choices[0].message.content)
            analiz = res_data.get("analiz", "")
