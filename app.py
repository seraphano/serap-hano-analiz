import streamlit as st
from groq import Groq
import json
import time
import re
import requests
from datetime import date

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
    .main-text { font-size: 19px; line-height: 2.1; color: #2c3e50; background: #fff; padding: 35px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 25px; white-space: pre-wrap; box-shadow: 0 4px 15px rgba(0,0,0,0.02); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın bilgeliğine hoş geldin.")

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Ruhsal ve Sistemik Kayıtlarınızı Açın")
    email = st.text_input("E-posta adresiniz:", placeholder="analiziniz buraya gönderilecek...")
    
    col_c, col_y = st.columns(2)
    with col_c:
        cinsiyet = st.selectbox("Cinsiyetiniz:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
    with col_y:
        dogum_tarihi = st.date_input("Doğum Tarihiniz", 
                                     min_value=date(1920, 1, 1), 
                                     max_value=date.today(),
                                     value=date(1990, 1, 1))

    dogum_saati = st.time_input("Doğum Saatiniz (Yaklaşık)")

    st.write("---")
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz? (Düşük, kürtaj ve kayıpları sayarak)", min_value=1, step=1)
    
    aile_evlilik = st.selectbox("Ebeveynlerinizin evlilik temeli nedir?", 
                                ["Severek evlendiler", "Görücü usulü", "Zorunlu / Mantık evliliği", "Bilmiyorum"])
    
    dislanan_biri = st.selectbox("Ailenizde dışlanmış, hakkı yenmiş veya adı hiç anılmayan biri var mı?", 
                                 ["Evet, var", "Hayır, yok", "Emin değilim"])
    
    agir_yazgi = st.selectbox("Aile geçmişinde ağır bir yazgı (İntihar, erken kayıp, iflas, göç) mevcut mu?", 
                              ["Evet, büyük travmalar var", "Hayır, sakin bir geçmiş", "Bazı zorluklar var"])

    kisisel_travma = st.selectbox("Geçmişinizde derin iz bırakan bir depresyon veya travma yaşadınız mı?",
                                  ["Evet, yaşadım", "Hayır, yaşamadım", "Belirsiz"])
    
    tikaniklik = st.selectbox("Şifalanmasını ve açılmasını istediğiniz yaşam alanı:", 
                              ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    submit = st.form_submit_button("Sistemik Analizi Başlat")

if submit:
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
    
    if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    elif yas < 15:
        st.warning(f"Sistemik alan analizi 15 yaş ve üzeri bireyler için tasarlanmıştır. (Yaşınız: {yas})")
    else:
        placeholder = st.empty()
        for step in ["Kökler taranıyor...", "Atasal bağlar inceleniyor...", "Sistemik alan mühürleniyor..."]:
            with placeholder.container():
                st.info(step)
                time.sleep(1.2)
        placeholder.empty()

        try:
            # --- YAŞ SKALASI VE PROMPT SİHRİ ---
            prompt_metni = f"""
            ROL: Sen Serap Hano'sun. %100 saf Türkçe konuşan, asla yabancı kelime kullanmayan bilge bir rehbersin.
            KULLANICI: {yas} yaşında {cinsiyet}, {kardes_sirasi}. çocuk. Alan: {tikaniklik}.
            
            YAŞ SKALASI TALİMATI:
            - 15-20: Yaşamın eşiğinde, kimlik ve aidiyet arayışında bir genç olarak yorumla.
            - 20-30: Kendi yolunu çizme, köklerden kopma ve bireyselleşme çabasıyla yorumla.
            - 30-45: İnşa etme, aile kurma ve kariyerde 'yerini alma' sancılarıyla yorumla.
            - 45-60: Olgunluk, hasat vakti ve köklerle barışma dönemi olarak yorumla.
            - 60+: Bilgelik, aktarım ve ruhsal huzur odaklı yorumla.

            DİL VE İMLA KURALLARI (HAYATİ):
            1. SADECE TÜRKÇE. 'necessary', 'only', 'provide', 'power' gibi kelimeler KESİNLİKLE YASAK.
            2. Çince veya yabancı karakter kullanımı YASAK.
            3. Verileri (yas, saat, alan) metin içinde rakamla tekrarlama; onları hissettir.
            
            JSON ÇIKTI:
            {{
                "isik": ["Sistemik Güç 1", "Sistemik Güç 2"],
                "golge": ["Sistemik Yük 1", "Sistemik Yük 2"],
                "analiz": "En az 250 kelimelik, edebi, sadece 'sen' diliyle yazılmış Türkçe analiz.",
                "soru": "Ruhsal bir soru.",
                "cta": "Serap Hano Akademi daveti."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen usta bir Türk edebiyatçısın. İngilizce veya yabancı kelime kullanman imkansızdır. Tüm karakterlerin Türkçe alfabe ile uyumlu olmalıdır."},
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"}
            )
            
            res_data = json.loads(completion.choices[0].message.content)

            # --- EKRAN TASARIMI ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız ve Atasal Kayıtlarınız")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Sistemik Işığın**")
                for i in res_data.get('isik', []): st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
            with c2:
                st.write("🟠 **Sistemik Gölgen**")
                for g in res_data.get('golge', []): st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

            # Metin temizleme (Eğer hala kaçak varsa diye önlem)
            analiz_temiz = res_data.get('analiz', '')
            analiz_temiz = re.sub(r'[^\x00-\x7f\x80-\xffüÜğĞıİşŞçÇöÖ]', '', analiz_temiz) # Yabancı karakterleri temizler

            st.markdown(f'<div class="main-text">{analiz_temiz}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Ruhuna Soru:** {res_data.get('soru', '')}")
            
            # --- KART VE PAYLAŞIM ---
            tilsim_kartlari = {
                "Sağlık & Enerji": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-saglik.webp",
                "Özgüven & Özdeğer": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-ozguven-ozdeger.webp",
                "Kariyer": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-kariyer.webp",
                "Para & Bereket": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-para-bereket.webp",
                "İlişkiler": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-iliskiler.webp"
            }
            
            st.markdown("---")
            if tikaniklik in tilsim_kartlari:
                st.image(tilsim_kartlari[tikaniklik], use_container_width=True)
            
            st.balloons()

            # Arka Plan Kaydı
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, "detay": f"Yas:{yas}, Cin:{cinsiyet}, Alan:{tikaniklik}",
                    "analiz": analiz_temiz, "soru": res_data.get('soru', '')
                }, timeout=10)
            except: pass

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
