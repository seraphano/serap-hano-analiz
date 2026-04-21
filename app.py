import streamlit as st
from groq import Groq
import json
import time
import re
import requests

# --- BAĞLANTI ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error(f"Kasa (Secrets) bağlantı hatası: {e}")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 8px solid #4caf50; margin-bottom: 15px; color: #2e7d32; font-weight: bold; }
    .error-box { background-color: #fff3e0; padding: 20px; border-radius: 15px; border-left: 8px solid #ff9800; margin-bottom: 15px; color: #e65100; font-weight: bold; }
    .main-text { font-size: 18px; line-height: 1.9; color: #333; background: #fff; padding: 25px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 20px; }
    .systemic-note { font-size: 14px; color: #666; font-style: italic; text-align: center; margin-top: 30px; padding: 15px; border-top: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın bilgeliğine hoş geldin.")

aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
gunler = list(range(1, 32))
yillar = list(range(2026, 1919, -1))

def email_gecerli_mi(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Bilgilerinizi Mühürleyin")
    email = st.text_input("Analizin mühürlenmesi için geçerli e-posta adresiniz:", placeholder="ornek@mail.com")
    
    col_g, col_a, col_y = st.columns(3)
    with col_g: gun = st.selectbox("Doğum Günü", gunler)
    with col_a: ay = st.selectbox("Ay", aylar)
    with col_y: yil = st.selectbox("Yıl", yillar, index=36)
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz?", min_value=1, step=1)
    aile_hikayesi = st.selectbox("Ailenizde ağır bir kader var mı?", ["Evet", "Hayır", "Bilmiyorum"])
    tikaniklik = st.selectbox("Düğümlenen ana alan", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    submit = st.form_submit_button("Dizimi Başlat")

if submit:
    if not email or not email_gecerli_mi(email):
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    else:
        # Animasyon
        placeholder = st.empty()
        steps = ["Kökler taranıyor...", "Atasal bağlar inceleniyor...", "Analiz Serap Hano rehberliğinde mühürleniyor..."]
        for step in steps:
            with placeholder.container():
                st.info(step)
                time.sleep(2)
        placeholder.empty()

        try:
            # ANALİZ TALEBİ
            prompt_metni = f"Sen Serap Hano'sun. Uzman bir Sistem Dizimi rehberi olarak karşındakine 'SEN' diye hitap et. Doğum tarihi verme. {kardes_sirasi}. çocuk, Tıkanıklık: {tikaniklik}, Aile Kaderi: {aile_hikayesi} için derin bir analiz yap. JSON: isik, golge, analiz, soru, cta."
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_metni}],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(completion.choices[0].message.content)

            # --- VERİYİ GOOGLE SHEETS'E GÖNDER ---
            try:
                payload = {
                    "email": email,
                    "dogum": f"{gun} {ay} {yil}",
                    "sira": str(kardes_sirasi),
                    "tikaniklik": tikaniklik
                }
                requests.post(SCRIPT_URL, json=payload, timeout=5)
            except Exception as e_sheet:
                # Veri yazma hatası analizi engellemesin diye sadece loglanır
                print(f"Tabloya yazma hatası: {e_sheet}")

            # --- SONUÇLAR ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız Belirlendi")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Işık Tarafın**")
                isik = data.get('isik', [])
                if isinstance(isik, str): isik = [isik]
                for i in isik: st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
            
            with c2:
                st.write("🟠 **Gölge Tarafın**")
                golge = data.get('golge', [])
                if isinstance(golge, str): golge = [golge]
                for g in golge: st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{data.get("analiz", "")}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Sana Özel Soru:** {data.get('soru', '')}")
            
            st.markdown('<div class="systemic-note">"Alan her an değişir. Lütfen sonuçları sindirmek için kendine zaman tanı."</div>', unsafe_allow_html=True)
            st.markdown(f"### 🎯 {data.get('cta', '')}")
            st.balloons()

        except Exception as e:
            # HATA GÖSTERİMİ DÜZELTİLDİ (GİRİNTİLİ)
            st.error(f"Teknik bir düğüm oluştu: {e}")
