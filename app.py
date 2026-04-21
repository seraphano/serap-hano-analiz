import streamlit as st
from groq import Groq
import json
import time

# --- BAĞLANTI ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error("API Anahtarı bulunamadı.")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

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
st.write("Sistemik alanın bilgeliğine yolculuk başlıyor.")

# --- TARİH AYARLARI ---
aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
gunler = list(range(1, 32))
yillar = list(range(2026, 1919, -1))

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Bilgilerinizi Mühürleyin")
    
    email = st.text_input(
        "Ruhsal frekansınızın sistemle doğru eşleşmesi ve analizin size özel mühürlenmesi için geçerli e-posta adresiniz gereklidir.", 
        placeholder="ornek@mail.com"
    )
    
    col_g, col_a, col_y = st.columns(3)
    with col_g: gun = st.selectbox("Doğum Günü", gunler)
    with col_a: ay = st.selectbox("Ay", aylar)
    with col_y: yil = st.selectbox("Yıl", yillar, index=36)
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz? (Kayıplar dahil)", min_value=1, step=1)
    aile_hikayesi = st.selectbox("Ailenizde göç, erken kayıp, iflas veya ağır bir kader var mı?", ["Evet", "Hayır", "Bilmiyorum"])
    tikaniklik = st.selectbox("Hayatınızda düğümlenen ana alan", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    submit = st.form_submit_button("Dizimi Başlat")

if submit:
    if not email or "@" not in email:
        st.error("Analizin mühürlenmesi için geçerli bir e-posta adresi gereklidir.")
    else:
        placeholder = st.empty()
        steps = [
            "Kökler taranıyor, sisteme bağlanılıyor...",
            "Atasal bağlar ve hiyerarşi inceleniyor...",
            "Dolaşıklıklar ve hiddet alanları tespit ediliyor...",
            "Analiz ruhsal frekansınıza mühürleniyor..."
        ]
        
        for step in steps:
            with placeholder.container():
                st.info(step)
                time.sleep(2.5)
        
        placeholder.empty()

        try:
            prompt_metni = f"""
            Sen, Bert Hellinger ekolünden gelen bir Sistemik Dizim uzmanısın. 
            Bilgiler: Doğum {gun} {ay} {yil}, {kardes_sirasi}. çocuk, Tıkanıklık: {tikaniklik}, Aile Kaderi: {aile_hikayesi}.
            
            Kural: Sadece Türkçe konuş. İngilizce kelime kullanma.
            
            Cevabı SADECE şu JSON yapısında ver:
            {{
                "isik": ["Sistemik Güç 1", "Sistemik Güç 2"],
                "golge": ["Ruhsal Yük 1", "Ruhsal Yük 2"],
                "analiz": "Derin sistemik analiz paragrafı.",
                "soru": "Atalarına sorman gereken soru.",
                "cta": "Serap Hano seans daveti."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_metni}],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(completion.choices[0].message.content)

            st.markdown("---")
            st.subheader("Ruhsal Haritanız Belirdi")
            
            # --- DÜZELTİLEN KUTUCUK MANTIĞI ---
            col1, col2 = st.columns(2)
            
            # Işık Tarafı Koruması
            with col1:
                st.write("🌿 **Işık Tarafın**")
                isik_verisi = data.get('isik', [])
                if isinstance(isik_verisi, str): isik_verisi = [isik_verisi] # Eğer yazıysa listeye çevir
                for i in isik_verisi:
                    st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
            
            # Gölge Tarafı Koruması
            with col2:
                st.write("🟠 **Gölge Tarafın**")
                golge_verisi = data.get('golge', [])
                if isinstance(golge_verisi, str): golge_verisi = [golge_verisi] # Eğer yazıysa listeye çevir
                for g in golge_verisi:
                    st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{data.get("analiz", "")}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Atalarına Sor:** {data.get('soru', '')}")
            
            st.markdown("""
                <div class="systemic-note">
                "Alan her an değişir. Ancak ilk analiz, ruhun o anki en saf frekansıdır. 
                Lütfen sonuçları sindirmek için kendine zaman tanı."
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"### 🎯 {data.get('cta', '')}")
            st.balloons()

        except Exception as e:
            st.error("Sistem şu an çok yoğun, lütfen tekrar deneyin.")
