import streamlit as st
from groq import Groq
import json
import time # Bekleme süresi için eklendi

# --- BAĞLANTI ---
API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

# Tasarım
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 8px solid #4caf50; margin-bottom: 15px; color: #2e7d32; font-weight: bold; }
    .error-box { background-color: #fff3e0; padding: 20px; border-radius: 15px; border-left: 8px solid #ff9800; margin-bottom: 15px; color: #e65100; font-weight: bold; }
    .main-text { font-size: 18px; line-height: 1.8; color: #333; background: #fff; padding: 25px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 20px; }
    .systemic-note { font-size: 14px; color: #666; font-style: italic; text-align: center; margin-top: 30px; padding: 15px; border-top: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın derinliklerine yolculuk başlıyor.")

# --- TÜRKÇE TARİH AYARLARI ---
aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
gunler = list(range(1, 32))
yillar = list(range(2026, 1919, -1))

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Bilgilerinizi Girin")
    
    email = st.text_input("Analizinizin kaybolmaması için e-posta adresiniz", placeholder="ornek@mail.com")
    
    col_g, col_a, col_y = st.columns(3)
    with col_g: gun = st.selectbox("Doğum Günü", gunler)
    with col_a: ay = st.selectbox("Ay", aylar)
    with col_y: yil = st.selectbox("Yıl", yillar, index=36)
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz?", min_value=1, step=1)
    tikaniklik = st.selectbox("Hayatınızda düğümlenen alan", ["İlişkiler", "Para & Bereket", "Kariyer", "Ruhsal Yorgunluk"])
    
    submit = st.form_submit_button("Sanal Dizimi ve Analizi Başlat")

if submit:
    if not email or "@" not in email:
        st.error("Lütfen geçerli bir e-posta adresi girin. Analiz sonuçlarını sizinle eşleştirmemiz gerekiyor.")
    else:
        with st.spinner("Sistemik alan taranıyor, köklerinizdeki kayıtlar hesaplanıyor..."):
            # PSİKOLOJİK BEKLEME SÜRESİ
            time.sleep(6) 
            
            try:
                prompt_metni = f"""
                Sen uzman bir Aile Dizimi rehberisin. {gun} {ay} {yil} doğumlu, {kardes_sirasi}. çocuk olan ve {tikaniklik} yaşayan biri için analiz yap.
                
                TALİMATLAR:
                1. SADECE TÜRKÇE KONUŞ. İngilizce kelime kullanma.
                2. Analiz derin, ruhsal ve sarsıcı olsun.
                3. JSON formatında ver: isik (liste), golge (liste), analiz (paragraf), soru (string), cta (string).
                """
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_metni}],
                    response_format={"type": "json_object"}
                )
                
                data = json.loads(completion.choices[0].message.content)

                # --- SONUÇLARI GÖSTER ---
                st.markdown("---")
                st.subheader("Ruhsal Haritanız Belirdi")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("🌿 **Işık Tarafın**")
                    for i in data['isik']: st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
                with col2:
                    st.write("🟠 **Gölge Tarafın**")
                    for g in data['golge']: st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="main-text">{data["analiz"]}</div>', unsafe_allow_html=True)
                st.warning(f"🔍 **Atalarına Sor:** {data['soru']}")
                
                # SİSTEMİK MESAJ BURADA
                st.markdown(f"""
                    <div class="systemic-note">
                    "Alan her an değişir. Ancak ilk analiz, ruhun o anki en saf frekansıdır. 
                    Lütfen sonuçları sindirmek için kendine zaman tanı."
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"### 🎯 {data['cta']}")
                st.balloons()

            except Exception as e:
                st.error(f"Sistemik bir düğüm oluştu, lütfen tekrar deneyin.")
