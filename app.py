import streamlit as st
from groq import Groq
import json
import time
import re
import requests
import html
from datetime import date
import urllib.parse

# 1. Page config
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 18px; border-radius: 12px; border-left: 6px solid #4caf50; margin-bottom: 10px; color: #2e7d32; font-size: 15px; }
    .error-box { background-color: #fff3e0; padding: 18px; border-radius: 12px; border-left: 6px solid #ff9800; margin-bottom: 10px; color: #e65100; font-size: 15px; }
    .main-text { font-size: 19px; line-height: 2.1; color: #2c3e50; background: #fff; padding: 35px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 25px; white-space: pre-wrap; box-shadow: 0 4px 15px rgba(0,0,0,0.02); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- BAĞLANTI ---
client = None
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]
else:
    st.error("Sistem ayarları eksik!")

st.title("✨ Köklerin Gizemi")
st.write("Atasal bağların ve ruhsal haritanın sistemik analizi.")

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
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz? (Kayıplar/Düşükler dahil)", min_value=1, step=1)
    aile_evlilik = st.selectbox("EBEVEYNLERİNİZİN evlilik temeli nedir?", ["Severek evlendiler", "Görücü usulü", "Mantık/Zorunlu evlilik", "Bilmiyorum"])
    dislanan_biri = st.selectbox("AİLENİZDE dışlanmış veya hakkı yenen biri var mı?", ["Evet, var", "Hayır, yok", "Emin değilim"])
    agir_yazgi = st.selectbox("AİLE GEÇMİŞİNDE ağır bir yazgı (İntihar, göç, iflas, erken ölüm)?", ["Evet, var", "Hayır, yok", "Bazı zorluklar var"])
    kisisel_travma = st.selectbox("SİZİN geçmişinizde derin bir travma/depresyon oldu mu?", ["Evet", "Hayır", "Belirsiz"])
    tikaniklik = st.selectbox("Açılmasını ve şifalanmasını istediğiniz alan:", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    kvkk_onay = st.checkbox("Verilerimin sistemik analiz için işlenmesine onay veriyorum.")
    submit = st.form_submit_button("Dizimi Başlat")

# --- ANALİZ MOTORU ---
if submit:
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
    
    if not email or "@" not in email:
        st.error("Geçerli bir e-posta girin.")
    elif not kvkk_onay:
        st.warning("Devam etmek için onay vermelisiniz.")
    elif yas < 15:
        st.warning(f"Analiz 15 yaş ve üzeri içindir. Yaşınız: {yas}")
    else:
        placeholder = st.empty()
        placeholder.info("Kökler taranıyor, sistemik alan mühürleniyor...")

        try:
            # DOĞUM SAATİ ENERJİ ANALİZİ (İşlevsel veri kullanımı)
            saat_notu = ""
            if dogum_saati.hour < 6: saat_notu = "Gece yarısı/şafak doğumu; gizli kalmış aile sırlarını taşıma potansiyeli."
            elif dogum_saati.hour < 12: saat_notu = "Sabah doğumu; yeni başlangıçlar ve sistemik liderlik enerjisi."
            elif dogum_saati.hour < 18: saat_notu = "Gündüz doğumu; toplumsal görünürlük ve dışa dönük yaşam yükleri."
            else: saat_notu = "Akşam/Gece doğumu; bilinçaltı derinliği ve ruhsal arabuluculuk."

            # SİSTEMİK MİMAR PROMPT
            prompt_metni = f"""
            SİSTEMİK VERİ TABLOSU:
            1. DANIŞAN: {yas} yaşında {cinsiyet}, {kardes_sirasi}. çocuk.
            2. ANNE-BABA EVLİLİĞİ (DANIŞANIN DEĞİL): {aile_evlilik}
            3. AİLEDE DIŞLANAN BİREY (DANIŞANIN DEĞİL): {dislanan_biri}
            4. ATASAL YAZGI: {agir_yazgi}
            5. KİŞİSEL TRAVMA: {kisisel_travma}
            6. TIKANIKLIK ALANI: {tikaniklik}
            7. ENERJİ ALANI (SAAT): {saat_notu}

            SİSTEMİK ANALİZ KURALLARI:
            - ÖZNE KONTROLÜ: Ebeveyn evliliğini veya dışlanan birini sakın DANIŞAN yaşadı gibi yazma. Onlar köklerdir. Danışan bu köklerin meyvesidir.
            - BAĞLANTI: Tıkanıklık alanı ile Atasal yazgı arasında metaforik bir bağ kur. (Örn: "Parada daralıyorsan, sisteminde göçle her şeyini kaybeden o atanın yasına sadık kalıyor olabilirsin.")
            - YASAKLI KELİMELER: "İç ışık", "gizemi", "yolculuk", "mucize", "mümkün", "only", "possible".
            - ÜSLUP: Serap Hano gibi bilge, sarsıcı, sadece "SEN" diyen, 3. tekil şahıstan nefret eden bir dil.

            JSON ÇIKTI YAPISI:
            {{
                "isik": ["...", "..."],
                "golge": ["...", "..."],
                "analiz": "150-200 kelimelik, sarsıcı, edebi, köklere dokunan Türkçe analiz.",
                "soru": "Ruhsal bir yüzleşme sorusu.",
                "cta": "Serap Hano Akademi davet cümlesi."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen sadece Türkçe konuşan usta bir Sistem Dizimi uzmanısın. Kullanıcı verilerini birbirine karıştırmadan, sistemik bir mantıkla analiz edersin. İngilizce kelime kullanırsan sistem çöker."},
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            # JSON GÜVENLİK DUVARI
            try:
                res_data = json.loads(completion.choices[0].message.content)
            except:
                st.error("Sistemik alan şu an çok yoğun, lütfen tekrar deneyin.")
                st.stop()

            placeholder.empty()

            # --- EKRAN TASARIMI ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız ve Atasal Kayıtlarınız")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Sistemik Işığın**")
                for i in res_data.get('isik', ['Güç taranıyor...']): 
                    st.markdown(f'<div class="success-box">{html.escape(i)}</div>', unsafe_allow_html=True)
            with c2:
                st.write("🟠 **Sistemik Gölgen (Atasal Yükün)**")
                for g in res_data.get('golge', ['Yük taranıyor...']): 
                    st.markdown(f'<div class="error-box">{html.escape(g)}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{html.escape(res_data.get("analiz", ""))}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Ruhuna Soru:** {html.escape(res_data.get('soru', ''))}")
            
            cta = res_data.get('cta', '')
            if cta:
                st.markdown(f"<div style='text-align: center; border: 2px dashed #4caf50; padding: 25px; border-radius: 15px; color: #2e7d32; font-weight: bold;'>🎯 {html.escape(cta)}</div>", unsafe_allow_html=True)

            # --- KART VE WHATSAPP ---
            tilsim_kartlari = {
                "Sağlık & Enerji": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-saglik.webp",
                "Özgüven & Özdeğer": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-ozguven-ozdeger.webp",
                "Kariyer": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-kariyer.webp",
                "Para & Bereket": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-para-bereket.webp",
                "İlişkiler": "http://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-iliskiler.webp"
            }
            if tikaniklik in tilsim_kartlari:
                st.image(tilsim_kartlari[tikaniklik], use_container_width=True)
                share_msg = urllib.parse.quote(f"Serap Hano Akademi'de 'Köklerin Gizemi' analizimi yaptım! ✨ Sen de denemelisin: https://seraphano-analiz.streamlit.app")
                st.markdown(f"<div style='text-align: center; margin-top: 15px;'><a href='https://api.whatsapp.com/send?text={share_msg}' target='_blank' style='background-color: #25D366; color: white; padding: 10px 25px; text-decoration: none; border-radius: 30px; font-weight: bold;'>🌿 WhatsApp'ta Paylaş</a></div>", unsafe_allow_html=True)

            st.balloons()

            # Google Sheets Kaydı
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, "tikaniklik": tikaniklik,
                    "detay": f"Yas:{yas}, Cin:{cinsiyet}, Sira:{kardes_sirasi}, Yazgi:{agir_yazgi}",
                    "analiz": res_data.get('analiz', ''), "soru": res_data.get('soru', '')
                }, timeout=15)
            except: pass

        except Exception as e:
            st.error("Bir enerji yoğunluğu oluştu, lütfen tekrar deneyin.")
