import streamlit as st
from groq import Groq
import json
import time
import re
import requests
import html
from datetime import date
import urllib.parse

# 1. Page config her zaman ilk sırada
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

# --- TASARIM VE GİZLEME ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 18px; border-radius: 12px; border-left: 6px solid #4caf50; margin-bottom: 10px; color: #2e7d32; font-size: 15px; }
    .error-box { background-color: #fff3e0; padding: 18px; border-radius: 12px; border-left: 6px solid #ff9800; margin-bottom: 10px; color: #e65100; font-size: 15px; }
    .main-text { font-size: 19px; line-height: 2.0; color: #2c3e50; background: #fff; padding: 35px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 25px; white-space: pre-wrap; box-shadow: 0 4px 15px rgba(0,0,0,0.02); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- BAĞLANTI ---
client = None
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]
else:
    st.error("API anahtarı eksik!")

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın bilgeliğine hoş geldin.")

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Ruhsal ve Atasal Kayıtlarınızı Açın")
    email = st.text_input("E-posta adresiniz:", placeholder="analiziniz mühürlenecek...")
    
    col_c, col_y = st.columns(2)
    with col_c:
        cinsiyet = st.selectbox("Cinsiyetiniz:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
    with col_y:
        dogum_tarihi = st.date_input("Doğum Tarihiniz", min_value=date(1920, 1, 1), value=date(1990, 1, 1))

    dogum_saati = st.time_input("Doğum Saatiniz (Yaklaşık)")

    st.write("---")
    kardes_sirasi = st.number_input("Kaçıncı çocuksunuz? (Kayıplar dahil)", min_value=1, step=1)
    aile_evlilik = st.selectbox("Ebeveynlerinizin evlilik temeli?", ["Severek evlendiler", "Görücü usulü", "Mantık evliliği", "Bilmiyorum"])
    dislanan_biri = st.selectbox("Ailede dışlanan veya hakkı yenen biri var mı?", ["Evet, var", "Hayır, yok", "Emin değilim"])
    agir_yazgi = st.selectbox("Aile geçmişinde ağır yazgı (İntihar, erken kayıp, göç, iflas)?", ["Evet, var", "Hayır, yok", "Bazı zorluklar var"])
    kisisel_travma = st.selectbox("Kişisel bir travma geçmişiniz var mı?", ["Evet", "Hayır", "Belirsiz"])
    tikaniklik = st.selectbox("Şifalanmasını istediğiniz alan:", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    kvkk_onay = st.checkbox("Verilerimin işlenmesine ve kaydedilmesine onay veriyorum.")
    submit = st.form_submit_button("Dizimi Başlat")

# --- ANALİZ ---
if submit:
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
    
    if not email or not re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', email.lower()):
        st.error("Geçerli bir e-posta girin.")
    elif not kvkk_onay:
        st.warning("KVKK onayını işaretleyin.")
    elif yas < 15:
        st.warning("Analiz 15 yaş ve üzeri içindir.")
    else:
        placeholder = st.empty()
        placeholder.info("Kökler taranıyor, analiz mühürleniyor...")

        try:
            # GÜÇLENDİRİLMİŞ SİSTEM MESAJI VE PROMPT
            prompt_metni = f"""
            SANA VERİLEN VERİLER:
            - Yaş: {yas}, Cinsiyet: {cinsiyet}, Kardeş Sırası: {kardes_sirasi}
            - Doğum Saati: {dogum_saati}, Evlilik: {aile_evlilik}
            - Dışlanan: {dislanan_biri}, Yazgı: {agir_yazgi}, Travma: {kisisel_travma}
            - Tıkanıklık: {tikaniklik}

            GÖREV:
            Sen Serap Hano'sun. %100 Türkçe konuşan bilge bir rehbersin. 
            Bu verileri metaforlarla birleştirip 'Sen' diliyle sarsıcı bir analiz yap. 
            Kayıp/dışlanma varsa bunu tıkanıklıkla bağla. 

            ÖNEMLİ YASAKLAR:
            - ASLA "Sen {yas} yaşındasın" veya "{kardes_sirasi}. çocuksun" gibi verileri rakamla yazma.
            - ASLA "kişinin", "bireyin" deme. Sadece "SEN" de.
            - İngilizce veya yabancı karakter (loading, sâu, possible, possible vb.) kullanımı KESİNLİKLE YASAK.
            
            ÖRNEK ÜSLUP:
            "Kariyerindeki bu duraksama aslında senin değil, köklerinde hakkı teslim edilmemiş o atasının sessiz çığlığı..."

            JSON ÇIKTI:
            {{
                "isik": ["...", "..."],
                "golge": ["...", "..."],
                "analiz": "120-180 kelimelik, sarsıcı, edebi ve samimi Türkçe metin.",
                "soru": "Bir ruhsal yüzleşme sorusu.",
                "cta": "Serap Hano Akademi davet cümlesi."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen %100 Türkçe konuşan usta bir edebiyatçısın. Sadece JSON formatında, Türk alfabesi kullanarak cevap verirsin. İngilizce kelime kullanımı sistem hatasına yol açar."},
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"},
                temperature=0.4 # Yaratıcılığı kısıtlayıp hata riskini azaltır
            )
            
            res_data = json.loads(completion.choices[0].message.content)
            placeholder.empty()

            # --- EKRAN ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız ve Atasal Kayıtlarınız")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Sistemik Işığın**")
                for i in res_data.get('isik', []): 
                    st.markdown(f'<div class="success-box">{html.escape(i)}</div>', unsafe_allow_html=True)
            with c2:
                st.write("🟠 **Sistemik Gölgen**")
                for g in res_data.get('golge', []): 
                    st.markdown(f'<div class="error-box">{html.escape(g)}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{html.escape(res_data.get("analiz", ""))}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Ruhuna Soru:** {html.escape(res_data.get('soru', ''))}")
            
            cta = res_data.get('cta', '')
            if cta:
                st.markdown(f"<div style='text-align: center; border: 2px dashed #4caf50; padding: 25px; border-radius: 15px; color: #2e7d32; font-weight: bold;'>🎯 {html.escape(cta)}</div>", unsafe_allow_html=True)

            # --- KART VE PAYLAŞIM ---
            tilsim_kartlari = {
                "Sağlık & Enerji": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-saglik.webp",
                "Özgüven & Özdeğer": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-ozguven-ozdeger.webp",
                "Kariyer": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-kariyer.webp",
                "Para & Bereket": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-para-bereket.webp",
                "İlişkiler": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-iliskiler.webp"
            }
            if tikaniklik in tilsim_kartlari:
                st.image(tilsim_kartlari[tikaniklik], use_container_width=True)
                share_msg = urllib.parse.quote(f"Köklerin Gizemi analizimi yaptım! ✨ Sen de denemelisin: https://seraphano-analiz.streamlit.app")
                st.markdown(f"<div style='text-align: center; margin-top: 15px;'><a href='https://api.whatsapp.com/send?text={share_msg}' target='_blank' style='background-color: #25D366; color: white; padding: 10px 25px; text-decoration: none; border-radius: 30px; font-weight: bold;'>🌿 WhatsApp'ta Paylaş</a></div>", unsafe_allow_html=True)

            st.balloons()

            # Kayıt (Google Scripts)
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, "tikaniklik": tikaniklik,
                    "detay": f"Yas:{yas}, Cin:{cinsiyet}, Sira:{kardes_sirasi}, Yazgi:{agir_yazgi}",
                    "analiz": res_data.get('analiz', ''), "soru": res_data.get('soru', '')
                }, timeout=15)
            except: pass

        except Exception as e:
            st.error("Bir enerji yoğunluğu oluştu, lütfen tekrar deneyin.")
