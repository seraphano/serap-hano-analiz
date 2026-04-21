import streamlit as st
from groq import Groq
import json
import datetime

# --- BAĞLANTI AYARLARI ---
# Not ettiğin API anahtarını buraya tırnakların içine yapıştır
API_KEY = "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"

try:
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error(f"Bağlantı hatası: {e}")

# --- SAYFA AYARLARI VE TASARIM ---
st.set_page_config(page_title="Serap Hano - Köklerin Gizemi", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 8px solid #4caf50; margin-bottom: 15px; color: #2e7d32; font-weight: bold; }
    .error-box { background-color: #fff3e0; padding: 20px; border-radius: 15px; border-left: 8px solid #ff9800; margin-bottom: 15px; color: #e65100; font-weight: bold; }
    .main-text { font-size: 18px; line-height: 1.7; color: #333; font-style: italic; background: #fff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.markdown("### Ruhsal ve Sistemik Analiz Rehberi")

# --- GİRİŞ FORMU ---
with st.form("analiz_formu"):
    st.write("Bilgilerinizi girerek köklerinizdeki gizemi aralayın.")
    
    # Tarih formatını ve sınırlarını ayarladık
    dogum_tarihi = st.date_input(
        "Doğum Tarihiniz (Gün/Ay/Yıl)",
        min_value=datetime.date(1920, 1, 1),
        max_value=datetime.date.today(),
        value=datetime.date(1990, 1, 1),
        format="DD/MM/YYYY" 
    )
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz? (Düşük/Kürtaj dahil)", min_value=1, step=1)
    aile_hikayesi = st.selectbox("Ailenizde göç, erken kayıp veya ağır bir kader var mı?", ["Evet", "Hayır", "Bilmiyorum"])
    tikaniklik = st.selectbox("Şu an en çok hangi alanda tıkanıklık hissediyorsunuz?", ["İlişkiler", "Bereket & Para", "Kariyer", "Ruhsal Yorgunluk"])
    
    submit = st.form_submit_button("Analizi Başlat")

# --- ANALİZ MANTIĞI ---
if submit:
    with st.spinner("Sistemik alan taranıyor, köklerinize bağlanılıyor..."):
        try:
            # GİZEMSEL VE DERİN PROMPT
            prompt_metni = f"""
            Sen bir uzman Sistem Dizimi ve Doğum Dizimi rehberisin. 
            Kullanıcı Bilgileri: 
            Doğum Tarihi: {dogum_tarihi.strftime('%d/%m/%Y')}
            Kardeş Sırası: {kardes_sirasi}
            Aile Hikayesi: {aile_hikayesi}
            Tıkanıklık: {tikaniklik}

            Bu verilere dayanarak, sarsıcı, derin ve gizemli bir analiz yap. 
            Cevabı SADECE şu JSON yapısında ver (başka açıklama ekleme):
            {{
                "isik": ["Güç Etiketi 1", "Güç Etiketi 2"],
                "golge": ["Gölge Etiketi 1", "Gölge Etiketi 2"],
                "analiz": "Derin ve sarsıcı analiz paragrafı (Kullanıcıya 'sen' diye hitap et).",
                "soru": "Ebeveynlerine sorman gereken gizemli ve derin bir soru.",
                "cta": "Serap Hano Akademi'den seans veya eğitim almaya teşvik eden etkileyici bir cümle."
            }}
            """
            
            # Yeni güncel model: llama-3.3-70b-versatile
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "user", "content": prompt_metni}],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(completion.choices[0].message.content)

            # --- SONUÇLARIN GÖSTERİLMESİ ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("🌿 **Işık Tarafın**")
                for i in data.get('isik', []):
                    st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown("🟠 **Gölge Tarafın**")
                for g in data.get('golge', []):
                    st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{data.get("analiz", "")}</div>', unsafe_allow_html=True)
            
            st.warning(f"🔍 **Atalarına Sor:** {data.get('soru', '')}")
            
            st.markdown(f"### 🎯 {data.get('cta', '')}")
            st.balloons()

        except Exception as e:
            st.error(f"Sistem bir düğüme rastladı: {e}")
