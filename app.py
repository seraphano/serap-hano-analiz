import streamlit as st
from groq import Groq
import json
import datetime # Tarih ayarları için bu eklendi

# --- BAĞLANTI ---
API_KEY = "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"

try:
    client = Groq(api_key=API_KEY)
except:
    st.error("API Anahtarı bulunamadı.")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Serap Hano - Köklerin Gizemi", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 8px solid #4caf50; margin-bottom: 15px; color: #2e7d32; font-weight: bold; }
    .error-box { background-color: #fff3e0; padding: 20px; border-radius: 15px; border-left: 8px solid #ff9800; margin-bottom: 15px; color: #e65100; font-weight: bold; }
    .main-text { font-size: 18px; line-height: 1.6; color: #333; font-style: italic; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.write("Lütfen bilgileri eksiksiz doldurun.")

# --- FORM ---
with st.form("analiz_formu"):
    # TAKVİM AYARI BURADA DÜZELTİLDİ:
    dogum_tarihi = st.date_input(
        "Doğum Tarihiniz",
        min_value=datetime.date(1920, 1, 1), # En eski 1920
        max_value=datetime.date.today(),      # En yeni bugün
        value=datetime.date(1990, 1, 1)      # Başlangıçta 1990 görünsün
    )
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz? (Kayıplar dahil)", min_value=1, step=1)
    aile_hikayesi = st.selectbox("Ailenizde ağır bir kader öyküsü var mı?", ["Evet", "Hayır", "Bilmiyorum"])
    tikaniklik = st.selectbox("Hangi alanda düğüm hissediyorsunuz?", ["İlişkiler", "Bereket & Para", "Kariyer", "Sağlık"])
    
    submit = st.form_submit_button("Sanal Dizimi Başlat")

# --- ANALİZ MANTIĞI ---
if submit:
    with st.spinner("Sistemik kayıtlar taranıyor..."):
        try:
            prompt_metni = f"Doğum: {dogum_tarihi}, Sıra: {kardes_sirasi}, Aile: {aile_hikayesi}, Tıkanıklık: {tikaniklik} verilerine göre derin bir aile dizimi analizi yap."
            
            # JSON formatında sarsıcı bir cevap istiyoruz
            prompt_talimati = f"""
            {prompt_metni}
            Cevabı SADECE şu JSON yapısında ver:
            {{
                "isik": ["Güç1", "Güç2"],
                "golge": ["Gölge1", "Gölge2"],
                "analiz": "Derin paragraf",
                "soru": "Soru",
                "cta": "Eğitime davet cümlesi"
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt_talimati}],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(completion.choices[0].message.content)

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Işık Tarafın**")
                for i in data['isik']:
                    st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
            with c2:
                st.write("🟠 **Gölge Tarafın**")
                for g in data['golge']:
                    st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{data["analiz"]}</div>', unsafe_allow_html=True)
            st.warning(f"**Atalarına Sor:** {data['soru']}")
            st.markdown(f"### 🎯 {data['cta']}")
            st.balloons()

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
