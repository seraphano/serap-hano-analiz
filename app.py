import streamlit as st
from groq import Groq
import json

# --- BAĞLANTI ---
API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

# --- TÜRKÇE TARİH AYARLARI ---
aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
gunler = list(range(1, 32))
yillar = list(range(2026, 1919, -1))

# Stil
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 8px solid #4caf50; margin-bottom: 15px; color: #2e7d32; font-weight: bold; }
    .error-box { background-color: #fff3e0; padding: 20px; border-radius: 15px; border-left: 8px solid #ff9800; margin-bottom: 15px; color: #e65100; font-weight: bold; }
    .main-text { font-size: 18px; line-height: 1.8; color: #333; background: #fff; padding: 25px; border-radius: 12px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın derinliklerine hoş geldiniz.")

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Doğum Bilgileriniz")
    col_g, col_a, col_y = st.columns(3)
    with col_g: gun = st.selectbox("Gün", gunler, index=0)
    with col_a: ay = st.selectbox("Ay", aylar, index=0)
    with col_y: yil = st.selectbox("Yıl", yillar, index=36) # 1990 varsayılan
    
    kardes_sirasi = st.number_input("Kaçıncı çocuksunuz? (Kayıplar dahil)", min_value=1, step=1)
    tikaniklik = st.selectbox("Tıkanıklık alanı", ["İlişkiler", "Para & Bereket", "Kariyer", "Sağlık"])
    
    # STRATEJİK EKLEME: E-posta (İsteğe bağlı veya zorunlu yapabilirsin)
    email = st.text_input("Analiz sonucunu yedeklemek için e-posta adresiniz (Opsiyonel)")
    
    submit = st.form_submit_button("Sanal Dizimi Başlat")

if submit:
    with st.spinner("Sistemik kayıtlar taranıyor, bu işlem ruhsal bir hazırlık gerektirir..."):
        try:
            prompt_metni = f"""
            Sen uzman bir Aile Dizimi rehberisin. {gun} {ay} {yil} doğumlu, {kardes_sirasi}. çocuk olan ve {tikaniklik} sorunu yaşayan biri için analiz yap.
            
            KRİTİK KURALLAR:
            1. SADECE TÜRKÇE KONUŞ. 'Experience', 'world', 'liderlik yeteneği experience etmek' gibi İngilizce kelimeleri ASLA kullanma.
            2. Analiz derin, ruhsal ve sarsıcı olsun.
            3. Cevabı SADECE şu JSON yapısında ver:
            {{
                "isik": ["Güç 1", "Güç 2"],
                "golge": ["Zayıflık 1", "Zayıflık 2"],
                "analiz": "Kesinlikle İngilizce kelime içermeyen, tamamen Türkçe derin analiz paragrafı.",
                "soru": "Atalarına sorman gereken soru.",
                "cta": "Serap Hano Akademi seans daveti."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_metni}],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(completion.choices[0].message.content)

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                for i in data['isik']: st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
            with c2:
                for g in data['golge']: st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{data["analiz"]}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Atalarına Sor:** {data['soru']}")
            st.success(f"🎯 {data['cta']}")
            st.balloons()

        except Exception as e:
            st.error(f"Sistemik bir düğüm: {e}")
