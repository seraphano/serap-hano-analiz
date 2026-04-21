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
    st.error(f"Bağlantı hatası: {e}")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 8px solid #4caf50; margin-bottom: 15px; color: #2e7d32; font-weight: bold; }
    .error-box { background-color: #fff3e0; padding: 20px; border-radius: 15px; border-left: 8px solid #ff9800; margin-bottom: 15px; color: #e65100; font-weight: bold; }
    .main-text { font-size: 18px; line-height: 1.9; color: #333; background: #fff; padding: 25px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 20px; white-space: pre-wrap; }
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
    email = st.text_input("E-posta adresiniz:", placeholder="ornek@mail.com")
    
    col_g, col_a, col_y = st.columns(3)
    with col_g: gun = st.selectbox("Doğum Günü", gunler)
    with col_a: ay = st.selectbox("Ay", aylar)
    with col_y: yil = st.selectbox("Yıl", yillar, index=36)
    
    kardes_sirasi = st.number_input("Kaçıncı çocuksunuz?", min_value=1, step=1)
    aile_hikayesi = st.selectbox("Ağır bir aile kaderi var mı?", ["Evet", "Hayır", "Bilmiyorum"])
    tikaniklik = st.selectbox("Tıkanıklık alanı", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    submit = st.form_submit_button("Dizimi Başlat")

if submit:
    if not email or not email_gecerli_mi(email):
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    else:
        placeholder = st.empty()
        steps = ["Kökler taranıyor...", "Atasal bağlar inceleniyor...", "Analiz mühürleniyor..."]
        for step in steps:
            with placeholder.container():
                st.info(step)
                time.sleep(2)
        placeholder.empty()

        try:
            # GÜÇLENDİRİLMİŞ PROMPT
            prompt_metni = f"""
            Sen Serap Hano'sun. Bilge, sıcak ve profesyonel bir Sistem Dizimi rehberisin. 
            Kullanıcı: {kardes_sirasi}. çocuk, Tıkanıklık: {tikaniklik}, Aile Kaderi: {aile_hikayesi}.
            
            GÖREVİN:
            1. 'analiz' alanına en az 150 kelimelik, derin, sistemik bir yorum yaz. 'Sen' dilini kullan.
            2. 'isik' ve 'golge' alanlarına doğrudan metni yaz (asla iç içe sözlük yapma).
            3. Dil tamamen doğal Türkçe olsun. 'Kariyer decisions' gibi karma kelimeler kullanma.
            
            JSON FORMATI (SADECE BU ANAHTARLARI KULLAN):
            {{
                "isik": ["Buraya birinci ışık özellik", "Buraya ikinci ışık özellik"],
                "golge": ["Buraya birinci gölge özellik", "Buraya ikinci gölge özellik"],
                "analiz": "Buraya uzun ve derin analiz metni...",
                "soru": "Sistemi sarsacak o can alıcı soru...",
                "cta": "Serap Hano Akademi'ye özel bir davet cümlesi..."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_metni}],
                response_format={"type": "json_object"}
            )
            
            raw_data = json.loads(completion.choices[0].message.content)

            # --- VERİ TEMİZLEME MANTIĞI ---
            def temizle(anahtar, varsayilan=""):
                val = raw_data.get(anahtar, varsayilan)
                if isinstance(val, dict): # Eğer hala sözlük gelirse içindeki metni çek
                    return next(iter(val.values()), str(val))
                return val

            # --- SONUÇLARI GÖSTER ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız Belirlendi")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Işık Tarafın**")
                isiklar = raw_data.get('isik', [])
                if isinstance(isiklar, str): isiklar = [isiklar]
                for i in isiklar:
                    st.markdown(f'<div class="success-box">{temizle("isik", i) if isinstance(i, dict) else i}</div>', unsafe_allow_html=True)
            
            with c2:
                st.write("🟠 **Gölge Tarafın**")
                golgeler = raw_data.get('golge', [])
                if isinstance(golgeler, str): golgeler = [golgeler]
                for g in golgeler:
                    st.markdown(f'<div class="error-box">{temizle("golge", g) if isinstance(g, dict) else g}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{temizle("analiz")}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Sana Özel Soru:** {temizle('soru')}")
            st.markdown(f"### 🎯 {temizle('cta')}")
            
            # --- TABLOYA GÖNDER ---
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, "dogum": f"{gun} {ay} {yil}", 
                    "sira": str(kardes_sirasi), "tikaniklik": tikaniklik
                }, timeout=5)
            except: pass

            st.balloons()

        except Exception as e:
            st.error(f"Analiz sırasında bir enerji düğümü oluştu: {e}")
