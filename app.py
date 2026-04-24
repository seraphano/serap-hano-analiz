import streamlit as st
from groq import Groq
import json
import time
import re
import requests
import html
from datetime import date
import urllib.parse

# 1. Page Config (Zorunlu olarak en üstte)
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

# --- GÖRSEL TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 6px solid #4caf50; margin-bottom: 12px; color: #2e7d32; font-size: 15px; }
    .error-box { background-color: #fff3e0; padding: 20px; border-radius: 15px; border-left: 6px solid #ff9800; margin-bottom: 12px; color: #e65100; font-size: 15px; }
    .main-text { font-size: 19px; line-height: 2.2; color: #2c3e50; background: #fff; padding: 40px; border-radius: 25px; border: 1px solid #eee; margin-bottom: 25px; white-space: pre-wrap; box-shadow: 0 10px 30px rgba(0,0,0,0.03); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- API BAĞLANTI ---
client = None
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]
else:
    st.error("Secrets ayarlarında API anahtarı eksik!")

st.title("✨ Köklerin Gizemi")
st.write("Atasal mirasın ve ruhsal tıkanıklıkların bilge analizi.")

# --- FORM BÖLÜMÜ ---
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
    aile_evlilik = st.selectbox("EBEVEYNLERİNİZİN evlilik temeli nedir?", ["Severek evlendiler", "Görücü usulü", "Mantık/Zorunlu evlilik", "Bilmiyorum"])
    dislanan_biri = st.selectbox("AİLENİZDE dışlanmış veya hakkı yenen biri var mı?", ["Evet, var", "Hayır, yok", "Emin değilim"])
    agir_yazgi = st.selectbox("AİLE GEÇMİŞİNDE ağır bir yazgı (İntihar, göç, iflas, erken ölüm)?", ["Evet, var", "Hayır, yok", "Bazı zorluklar var"])
    kisisel_travma = st.selectbox("SİZİN geçmişinizde derin bir travma/depresyon oldu mu?", ["Evet", "Hayır", "Belirsiz"])
    tikaniklik = st.selectbox("Şifalanmasını istediğiniz alan:", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    kvkk_onay = st.checkbox("Verilerimin sistemik analiz için işlenmesine ve kaydedilmesine onay veriyorum.")
    submit = st.form_submit_button("Sistemik Analizi Başlat")

# --- ANALİZ MOTORU ---
if submit:
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
    
    if not email or "@" not in email:
        st.error("Geçerli bir e-posta adresi girin.")
    elif not kvkk_onay:
        st.warning("Devam etmek için KVKK onayını işaretlemelisiniz.")
    elif yas < 15:
        st.warning(f"Analizler 15 yaş ve üzeri içindir. Yaşınız: {yas}")
    else:
        placeholder = st.empty()
        placeholder.info("Sistemik alan taranıyor, analiz mühürleniyor...")

        try:
            # Enerji İmzası
            saat_enerjisi = ""
            if dogum_saati.hour < 6: saat_enerjisi = "Gece yarısı derinliği; aile sırlarını açığa çıkarma gücü."
            elif dogum_saati.hour < 12: saat_enerjisi = "Sabah ışığı; yeni yollar açma ve sistemik liderlik."
            else: saat_enerjisi = "Gün batımı ve gece; ruhsal köprü olma ve bilinçaltı rehberliği."

            # PROMPT
            prompt_metni = f"""
            ROL: Sen Serap Hano'sun. %100 Türkçe konuşan, sarsıcı içgörüler üreten bir Sistem Dizimi uzmanısın.
            
            KÖK VERİLER (BUNLAR AİLENİN HİKAYESİDİR, DANIŞANIN DEĞİL):
            - Anne-Baba Evliliği: {aile_evlilik}
            - Ailede Dışlanan: {dislanan_biri}
            - Atasal Yazgı: {agir_yazgi}
            
            DANIŞAN VERİLERİ (BUNLAR SENİN ÖZNENDİR):
            - Profil: {yas} yaşında {cinsiyet}, {kardes_sirasi}. çocuk.
            - Kişisel Geçmiş: {kisisel_travma}
            - Tıkanıklık Alanı: {tikaniklik}
            - Enerji İmzası (Doğum Saati): {saat_enerjisi}

            ANALİZ KURALLARI:
            1. ÖZNE KONTROLÜ: Ebeveyn evliliğini sakın DANIŞANIN KENDİ evliliği gibi yazma. Onlar köklerdir.
            2. MEKANİZMA KUR: "Atasal yükün var" demek yetmez. O yükün bugünkü {tikaniklik} alanını NASIL kilitlediğini açıkla.
               Örnek: "Anne-baban sevilmeden evlendiği için sen başarıyı 'soğuk bir zorunluluk' gibi yaşıyorsun."
            3. YASAKLAR: "olabilir", "yönlendirebilir", "yolculuk", "iç ışık", "gizem", "mucize", "mümkün", "only", "possible", "loading".
            4. VERİ TEKRARI YASAK: Yaş, saat, seçenek isimlerini rakamla veya direkt yazma. Onları hissettir.

            JSON ÇIKTI:
            {{
                "isik": ["Sistemik Yetenek 1", "Sistemik Yetenek 2"],
                "golge": ["Taşınan Atasal Yük 1", "Taşınan Atasal Yük 2"],
                "analiz": "En az 150 kelimelik, mekanizma odaklı, bilgece analiz metni.",
                "soru": "Ruhsal bir yüzleşme sorusu.",
                "cta": "Serap Hano Akademi davet cümlesi."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen usta bir Türk edebiyatçısın. İngilizce kelime kullanman imkansızdır. Sadece JSON formatında cevap ver."},
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"},
                temperature=0.35
            )
            
            res_data = json.loads(completion.choices[0].message.content)
            placeholder.empty()

            # --- EKRAN ÇIKTISI ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız ve Atasal Kayıtlarınız")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Sistemik Işığın**")
                for i in res_data.get('isik', []): 
                    st.markdown(f'<div class="success-box">{html.escape(i)}</div>', unsafe_allow_html=True)
            with c2:
                st.write("🟠 **Atasal Yükün (Gölge)**")
                for g in res_data.get('golge', []): 
                    st.markdown(f'<div class="error-box">{html.escape(g)}</div>', unsafe_allow_html=True)

            # Analiz Metni
            st.markdown(f'<div class="main-text">{html.escape(res_data.get("analiz", ""))}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Ruhuna Soru:** {html.escape(res_data.get('soru', ''))}")
            
            cta = res_data.get('cta', '')
            if cta:
                st.markdown(f"<div style='text-align: center; border: 2px dashed #4caf50; padding: 25px; border-radius: 15px; color: #2e7d32; font-weight: bold; background: #f1f8e9;'>🎯 {html.escape(cta)}</div>", unsafe_allow_html=True)

            # --- KART VE PAYLAŞIM ---
            tilsim_kartlari = {
                "Sağlık & Enerji": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-saglik.webp",
                "Özgüven & Özdeğer": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-ozguven-ozdeger.webp",
                "Kariyer": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-kariyer.webp",
                "Para & Bereket": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-para-bereket.webp",
                "İlişkiler": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-iliskiler.webp"
            }
            
            if tikaniklik in tilsim_kartlari:
                st.image(tilsim_kartlari[tikaniklik], use_container_width=True)
                share_msg = urllib.parse.quote(f"Köklerin Gizemi analizimi yaptım! ✨ Sen de denemelisin: https://seraphano-analiz.streamlit
