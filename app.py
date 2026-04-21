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
    .success-box { background-color: #e8f5e9; padding: 18px; border-radius: 12px; border-left: 6px solid #4caf50; margin-bottom: 10px; color: #2e7d32; font-size: 15px; }
    .error-box { background-color: #fff3e0; padding: 18px; border-radius: 12px; border-left: 6px solid #ff9800; margin-bottom: 10px; color: #e65100; font-size: 15px; }
    .main-text { font-size: 18px; line-height: 1.9; color: #333; background: #fff; padding: 30px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 25px; white-space: pre-wrap; }
    .systemic-note { font-size: 14px; color: #777; font-style: italic; text-align: center; margin-top: 30px; padding: 15px; border-top: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın bilgeliğine hoş geldin.")

# --- DİL MUHAFIZI ---
def turkcelestir(metin):
    sozluk = {
        "experiences": "deneyimler", "experience": "deneyim",
        "life": "yaşam", "decision": "karar", "decisions": "kararlar",
        "sometimes": "bazen", "health": "sağlık", "výběirlerini": "seçimlerini",
        "výběr": "seçim", "important": "önemli", "factor": "faktör"
    }
    for ing, tr in sozluk.items():
        metin = re.sub(rf'\b{ing}\b', tr, metin, flags=re.IGNORECASE)
    return metin

def veriyi_al(data, key):
    val = data.get(key, "")
    if isinstance(val, list):
        return [turkcelestir(str(next(iter(i.values())) if isinstance(i, dict) else i)) for i in val]
    if isinstance(val, dict):
        return turkcelestir(str(next(iter(val.values()), "")))
    return turkcelestir(str(val))

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
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz?", min_value=1, step=1)
    aile_hikayesi = st.selectbox("Aile geçmişinizde (göç, erken kayıp, iflas vb.) derin iz bırakan bir olay var mı?", ["Evet", "Hayır", "Bilmiyorum"])
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
            # KRİTİK: PROMPT İÇİNE 'JSON' KELİMESİ EKLENDİ
            prompt_metni = f"""
            Sen Serap Hano'sun. Bilge ve samimi bir Sistem Dizimi rehberisin. 
            Kullanıcı Bilgileri: {kardes_sirasi}. çocuk, Tıkanıklık: {tikaniklik}, Aile Kaderi: {aile_hikayesi}.

            BU ANALİZİ BİR JSON FORMATINDA VERMELİSİN.
            
            KURALLAR:
            1. %100 TÜRKÇE yaz. Asla yabancı kelime kullanma.
            2. "Bir bireyin yaşamını..." gibi mesafeli başlama. Kalbe hitap et.
            3. 'analiz' alanı en az 200 kelime olsun. Derin ve edebi olsun.
            
            JSON OBJESİ ŞU ANAHTARLARI İÇERMELİDİR:
            {{
                "isik": ["Özellik 1", "Özellik 2"],
                "golge": ["Özellik 1", "Özellik 2"],
                "analiz": "Derin ruhsal analiz metni...",
                "soru": "Sana özel o can alıcı soru...",
                "cta": "Serap Hano Akademi davet cümlesi..."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_metni}],
                response_format={"type": "json_object"}
            )
            
            res_data = json.loads(completion.choices[0].message.content)

            # --- SONUÇLAR ---
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

            st.markdown(f'<div class="main-text">{veriyi_al(res_data, "analiz")}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Sana Özel Soru:** {veriyi_al(res_data, 'soru')}")
            
            cta_text = veriyi_al(res_data, 'cta')
            st.markdown(f"<h3 style='text-align: center; color: #2e7d32; padding: 25px; border: 2px dashed #4caf50; border-radius: 15px; background: #f1f8e9;'>🎯 {cta_text}</h3>", unsafe_allow_html=True)
            
# --- 🃏 RUH KARTI VE PAYLAŞIM ALANI ---
            tilsim_kartlari = {
                "Sağlık & Enerji": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-saglik.webp",
                "Özgüven & Özdeğer": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-ozguven-ozdeger.webp",
                "Kariyer": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-kariyer.webp",
                "Para & Bereket": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-para-bereket.webp",
                "İlişkiler": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-iliskiler.webp"
            }
            
            st.markdown("---")
            st.markdown("<h2 style='text-align: center; color: #2e7d32;'>✨ Ruhunun Bugünkü Tılsımı</h2>", unsafe_allow_html=True)
            
            if tikaniklik in tilsim_kartlari:
                st.image(tilsim_kartlari[tikaniklik], use_container_width=True)
                st.markdown(f"""
                    <div style='text-align: center; padding: 15px; background-color: #f1f8e9; border-radius: 10px; color: #2e7d32; font-weight: bold;'>
                        Bu kart, {tikaniklik} alanındaki dönüşümün için sana rehberlik edecek sembolleri taşıyor.
                    </div>
                """, unsafe_allow_html=True)

                # --- 📱 SOSYAL MEDYA BUTONLARI ---
                import urllib.parse
                share_text = f"Serap Hano Akademi'de Köklerin Gizemi analizimi yaptım! ✨ Sen de denemelisin: https://seraphano-analiz.streamlit.app"
                safe_text = urllib.parse.quote(share_text)
                
                wa_url = f"https://api.whatsapp.com/send?text={safe_text}"
                fb_url = f"https://www.facebook.com/sharer/sharer.php?u=https://seraphano-analiz.streamlit.app"
                
                st.markdown(f"""
                    <div style='display: flex; justify-content: center; gap: 10px; margin: 20px 0;'>
                        <a href="{wa_url}" target="_blank" style="background-color: #25D366; color: white; padding: 10px 15px; text-decoration: none; border-radius: 10px; font-size: 14px; font-weight: bold;">WhatsApp</a>
                        <a href="{fb_url}" target="_blank" style="background-color: #1877F2; color: white; padding: 10px 15px; text-decoration: none; border-radius: 10px; font-size: 14px; font-weight: bold;">Facebook</a>
                        <button onclick="navigator.clipboard.writeText('https://seraphano-analiz.streamlit.app'); alert('Link kopyalandı! Instagram hikayende paylaşabilirsin ✨');" style="background-color: #E1306C; color: white; padding: 10px 15px; border: none; border-radius: 10px; font-size: 14px; font-weight: bold; cursor: pointer;">Instagram (Link)</button>
                    </div>
                """, unsafe_allow_html=True)

            # --- 🎈 ÖNCE BALONLAR (HIZLI ÇALIŞIR) ---
            st.balloons()

            # --- 💾 SONRA ARKA PLAN KAYDI (SESSİZCE ÇALIŞIR) ---
            try:
                analiz_metni = veriyi_al(res_data, "analiz")
                soru_metni = veriyi_al(res_data, 'soru')
                requests.post(SCRIPT_URL, json={
                    "email": email, 
                    "dogum": f"{gun} {ay} {yil}", 
                    "sira": str(kardes_sirasi), 
                    "tikaniklik": tikaniklik,
                    "analiz": analiz_metni,
                    "soru": soru_metni
                }, timeout=10)
            except:
                pass
        except Exception as e:
            st.error(f"Enerji alanında bir karışıklık oldu: {e}")
