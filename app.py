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
    .success-box { background-color: #e8f5e9; padding: 18px; border-radius: 12px; border-left: 6px solid #4caf50; margin-bottom: 10px; color: #2e7d32; font-size: 15px; line-height: 1.5; }
    .error-box { background-color: #fff3e0; padding: 18px; border-radius: 12px; border-left: 6px solid #ff9800; margin-bottom: 10px; color: #e65100; font-size: 15px; line-height: 1.5; }
    .main-text { font-size: 18px; line-height: 1.9; color: #333; background: #fff; padding: 30px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 25px; white-space: pre-wrap; }
    .systemic-note { font-size: 14px; color: #777; font-style: italic; text-align: center; margin-top: 30px; padding: 15px; border-top: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın bilgeliğine hoş geldin.")

# --- AKILLI VERİ AYIKLAYICI ---
def veriyi_al(data, key):
    """AI'dan gelen veriyi (liste, metin veya sözlük) güvenli bir şekilde metne çevirir."""
    val = data.get(key, "")
    if isinstance(val, list):
        # Eğer listeyse, içindeki her bir öğeyi temizle ve listele
        return [veriyi_al({'x': i}, 'x') for i in val]
    if isinstance(val, dict):
        # Eğer sözlükse, içindeki ilk metin değerini bul
        return str(next(iter(val.values()), ""))
    return str(val)

def email_gecerli_mi(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Bilgilerinizi Mühürleyin")
    email = st.text_input("E-posta adresiniz:", placeholder="ornek@mail.com")
    
    col_g, col_a, col_y = st.columns(3)
    with col_g: gun = st.selectbox("Gün", list(range(1, 32)))
    with col_a: ay = st.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"])
    with col_y: yil = st.selectbox("Yıl", list(range(2026, 1920, -1)), index=36)
    
    kardes_sirasi = st.number_input("Kaçıncı çocuksunuz?", min_value=1, step=1)
    aile_hikayesi = st.selectbox("Ağır bir aile kaderi var mı?", ["Evet", "Hayır", "Bilmiyorum"])
    tikaniklik = st.selectbox("Tıkanıklık alanı", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    submit = st.form_submit_button("Dizimi Başlat")

if submit:
    if not email or not email_gecerli_mi(email):
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    else:
        placeholder = st.empty()
        for step in ["Kökler taranıyor...", "Atasal bağlar inceleniyor...", "Analiz mühürleniyor..."]:
            with placeholder.container():
                st.info(step)
                time.sleep(2)
        placeholder.empty()

        try:
            # GÜÇLENDİRİLMİŞ VE KESİN PROMPT
            prompt_metni = f"""
            Sen Serap Hano'sun. Derin bir Sistem Dizimi rehberisin. 
            Kullanıcı: {kardes_sirasi}. çocuk, Tıkanıklık: {tikaniklik}, Aile Kaderi: {aile_hikayesi}.

            TALİMATLAR:
            1. SADECE TÜRKÇE yaz. Asla yabancı kelime kullanma.
            2. 'analiz' alanına en az 200 kelimelik, edebi ve sistemik derinliği olan bir metin yaz.
            3. 'isik' ve 'golge' alanlarına doğrudan kısa maddeler yaz.
            4. JSON yapısını asla bozma.

            JSON YAPISI:
            {{
                "isik": ["Özellik 1", "Özellik 2"],
                "golge": ["Özellik 1", "Özellik 2"],
                "analiz": "Uzun analiz metni buraya...",
                "soru": "Sarsıcı sistemik soru buraya...",
                "cta": "Davet cümlesi buraya..."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_metni}],
                response_format={"type": "json_object"}
            )
            
            res_data = json.loads(completion.choices[0].message.content)

            # --- SONUÇLARI GÖSTER ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız Belirlendi")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Işık Tarafın**")
                isiklar = veriyi_al(res_data, 'isik')
                if isinstance(isiklar, list):
                    for i in isiklar: st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
                else: st.markdown(f'<div class="success-box">{isiklar}</div>', unsafe_allow_html=True)
            
            with c2:
                st.write("🟠 **Gölge Tarafın**")
                golgeler = veriyi_al(res_data, 'golge')
                if isinstance(golgeler, list):
                    for g in golgeler: st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)
                else: st.markdown(f'<div class="error-box">{golgeler}</div>', unsafe_allow_html=True)

            # Ana Analiz Metni
            st.markdown(f'<div class="main-text">{veriyi_al(res_data, "analiz")}</div>', unsafe_allow_html=True)
            
            # Soru
            st.warning(f"🔍 **Sana Özel Soru:** {veriyi_al(res_data, 'soru')}")
            
            # Davet (CTA)
            cta_final = veriyi_al(res_data, 'cta')
            st.markdown(f"<h3 style='text-align: center; color: #2e7d32; padding: 25px; border: 2px dashed #4caf50; border-radius: 15px; background: #f1f8e9;'>🎯 {cta_final}</h3>", unsafe_allow_html=True)
            
            # --- KAYIT ---
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, "dogum": f"{gun} {ay} {yil}", 
                    "sira": str(kardes_sirasi), "tikaniklik": tikaniklik
                }, timeout=5)
            except: pass

            st.balloons()

        except Exception as e:
            st.error(f"Analiz sırasında bir enerji düğümü oluştu: {e}")
