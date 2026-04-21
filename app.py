import streamlit as st
from groq import Groq
import json

# --- BAĞLANTI ---
# Kendi anahtarını aşağıya yapıştır
API_KEY = "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"

try:
    client = Groq(api_key=API_KEY)
except:
    st.error("API Anahtarı bulunamadı veya hatalı.")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Serap Hano - Köklerin Gizemi", layout="centered")

# Görsel Stil (Senin gönderdiğin tarzda kutucuklar için)
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 8px solid #4caf50; margin-bottom: 15px; color: #2e7d32; font-weight: bold; }
    .error-box { background-color: #fff3e0; padding: 20px; border-radius: 15px; border-left: 8px solid #ff9800; margin-bottom: 15px; color: #e65100; font-weight: bold; }
    .main-text { font-size: 18px; line-height: 1.6; color: #333; font-style: italic; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.markdown("### Sistemik Analiz ve Aile Dizimi Rehberi")
st.write("Lütfen bilgileri eksiksiz doldurun. Bu bilgiler tamamen size özel bir analiz oluşturmak için kullanılır.")

# --- FORM ---
with st.form("analiz_formu"):
    dogum_tarihi = st.date_input("Doğum Tarihiniz")
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz? (Düşük/Kürtaj dahil)", min_value=1, step=1)
    aile_hikayesi = st.selectbox("Ailenizde göç, erken kayıp veya iflas gibi bir kader var mı?", ["Evet", "Hayır", "Bilmiyorum"])
    tikaniklik = st.selectbox("Hayatınızın hangi alanında bir düğüm hissediyorsunuz?", ["İlişkiler", "Bereket & Para", "Kariyer", "Sağlık & Enerji"])
    
    submit = st.form_submit_button("Sanal Dizimi Başlat")

# --- ANALİZ MANTIĞI ---
if submit:
    with st.spinner("Sistemik kayıtlar taranıyor, lütfen bekleyin..."):
        try:
            # GİZEMSEL PROMPT
            prompt_metni = f"""
            Sen bir Aile Dizimi ve Ruhsal Rehbersin. 
            Veriler: Doğum {dogum_tarihi}, Sıra: {kardes_sirasi}, Aile Kaderi: {aile_hikayesi}, Tıkanıklık: {tikaniklik}.
            
            Bu kişiye özel, derin, gizemli ve yüzleştirici bir analiz yap. 
            Cevabı SADECE şu JSON formatında ver:
            {{
                "isik": ["Güç1", "Güç2"],
                "golge": ["Zayıflık1", "Zayıflık2"],
                "analiz": "Derin ve sarsıcı bir paragraf.",
                "soru": "Ebeveynlere sorulacak sarsıcı bir soru.",
                "cta": "Serap Hano Akademi seans yönlendirme cümlesi."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt_metni}],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(completion.choices[0].message.content)

            # --- SONUÇLARI GÖSTER ---
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("🌿 **Işık Tarafın**")
                for i in data['isik']:
                    st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown("🟠 **Gölge Tarafın**")
                for g in data['golge']:
                    st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{data["analiz"]}</div>', unsafe_allow_html=True)
            st.warning(f"**Atalarına Sor:** {data['soru']}")
            
            st.markdown(f"### 🎯 {data['cta']}")
            st.balloons() # Başarı kutlaması

        except Exception as e:
            st.error(f"Sistem bir düğüme rastladı: {e}")
