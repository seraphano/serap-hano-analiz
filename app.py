import streamlit as st
from groq import Groq
import json
import time
import re
import requests
import html
from datetime import date
import urllib.parse

# 1. Page Config
st.set_page_config(page_title="Serap Hano Akademi | Ruhun Aynası", layout="centered")

# --- CSS: ŞİİRSEL VE DERİN TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .main-text { 
        font-size: 21px; 
        line-height: 2.4; 
        color: #1a252f; 
        background: #ffffff; 
        padding: 50px; 
        border-radius: 40px; 
        border: none; 
        margin-bottom: 30px; 
        white-space: pre-wrap; 
        box-shadow: 0 20px 60px rgba(0,0,0,0.05);
        font-family: 'Georgia', serif;
    }
    .success-box, .error-box { 
        padding: 25px; 
        border-radius: 20px; 
        margin-bottom: 15px; 
        font-size: 17px; 
        border: none;
        box-shadow: 0 10px 20px rgba(0,0,0,0.02);
    }
    .success-box { background-color: #f4faf6; color: #2d5a3f; border-left: 10px solid #4caf50; }
    .error-box { background-color: #fff9f2; color: #855d21; border-left: 10px solid #ff9800; }
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
st.write("Sadece verilerin değil, senin hikayenin sessiz yankıları.")

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Ruhsal Kayıtlarını Aç")
    email = st.text_input("E-posta adresin:", placeholder="analizin buraya mühürlenecek...")
    
    col_c, col_y = st.columns(2)
    with col_c:
        cinsiyet = st.selectbox("Cinsiyetin:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
    with col_y:
        dogum_tarihi = st.date_input("Doğum Tarihin", min_value=date(1920, 1, 1), value=date(1990, 1, 1))

    dogum_saati = st.time_input("Doğum Saatin (Yaklaşık)")

    st.write("---")
    kardes_sirasi = st.number_input("Kaçıncı çocuksun? (Düşük/Kayıplar dahil)", min_value=1, step=1)
    aile_evlilik = st.selectbox("EBEVEYNLERİNİN evliliği?", ["Severek evlendiler", "Görücü usulü", "Mantık/Zorunlu evlilik", "Bilmiyorum"])
    dislanan_biri = st.selectbox("AİLEDE dışlanan/hakkı yenen biri var mı?", ["Evet, var", "Hayır, yok", "Emin değilim"])
    agir_yazgi = st.selectbox("AİLEDE ağır bir yazgı (İntihar, iflas, erken ölüm)?", ["Evet, var", "Hayır, yok", "Bazı zorluklar var"])
    kisisel_travma = st.selectbox("SİZİN geçmişinizde derin bir travma/depresyon oldu mu?", ["Evet", "Hayır", "Belirsiz"])
    tikaniklik = st.selectbox("Şifalanmasını istediğin alan:", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    kvkk_onay = st.checkbox("Ruhsal kayıtlarımın işlenmesine ve analiz edilmesine onay veriyorum.")
    submit = st.form_submit_button("Dizimi Başlat")

if submit:
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
    
    if not email or "@" not in email:
        st.error("Lütfen geçerli bir e-posta girin.")
    elif not kvkk_onay:
        st.warning("Onay vermeden dizim başlayamaz.")
    else:
        placeholder = st.empty()
        placeholder.info("Kuantum alan taranıyor, sessiz hikayeler toplanıyor...")

        try:
            # Enerji İmzası
            saat_notu = ""
            if dogum_saati.hour < 6: saat_notu = "Şafak öncesinin derin sessizliği; saklıyı görme ve kökleri şifalandırma gücü."
            elif dogum_saati.hour < 12: saat_notu = "Sabahın yükselen iradesi; tıkanıklıkları cesaretle dönüştürme potansiyeli."
            else: saat_notu = "Gecenin bilinçaltı rehberliği; ruhsal köprüler kurma ve sezgisel derinlik."

            # V13 - PSİKOLOJİK PROJEKSİYON PROMPT
            prompt_metni = f"""
            ROL: Sen usta bir Sistem Dizimi uzmanı Serap Hano'sun. Bilge, şiirsel, sarsıcı ve insanın ruhuna dokunan bir dille konuşuyorsun. 
            AMACIN: Danışanın verilerini (rakamları/seçenekleri) asla tekrar etmeden, onlara 'Beni biri sonunda gerçekten gördü' hissini yaşatmak.
            
            KÖK MEKANİZMALARI (DANIŞANIN DEĞİL, SİSTEMİN VERİLERİ):
            - Ebeveyn Evliliği: {aile_evlilik} (Bu, danışanın sevgi şablonudur)
            - Ailede Dışlanan: {dislanan_biri} (Bu, danışanın taşıdığı görünmez ah'tır)
            - Atasal Yazgı: {agir_yazgi} (Bu, danışanın kariyer/para/ilişki kilididir)
            
            DANIŞAN MEKANİZMALARI:
            - Profil: {yas} yaşında {cinsiyet}, {kardes_sirasi}. çocuk.
            - Tıkanıklık: {tikaniklik}, Enerji: {saat_notu}

            METİN AKIŞI (ZORUNLU 4 AŞAMA):
            1. GÖRÜLME: Danışanın uzun süredir sakladığı o 'güçlü durma' veya 'sessizleşme' yorgunluğunu anlat.
            2. YARA: Verileri metaforlara dönüştür. (Görücü usulü evlilik = 'Sevgisiz kurulmuş bir bağın gölgesinde duygularını feda etmeyi öğrenmek')
            3. ÇATIŞMA: Tıkanıklık alanının ({tikaniklik}) aslında hangi atasal yasa sadık kaldığını fısılda. 
            4. ÇÖZÜLME: Sarsıcı bir umutla bitir. 'Bu yük senin değil, artık bırakabilirsin.'

            YASAKLAR:
            - ASLA rakam (27, 45, 2. çocuk vb.) ve veri isimlerini (görücü usulü, tıkanıklık vb.) olduğu gibi yazma.
            - 'yolculuk', 'iç ışık', 'gizem', 'mucize', 'mümkün', 'enerji', 'frekans' kelimelerini kullanma.
            - Robotik, düzgün paragraflar yerine; kısa, ritmik ve nefes alan cümleler kur.

            JSON ÇIKTI:
            {{
                "isik": ["...", "..."],
                "golge": ["...", "..."],
                "analiz": "130-180 kelimelik, sarsıcı, şiirsel, duygusal kırılma yaratan Türkçe metin.",
                "soru": "Ruhsal bir yüzleşme sorusu.",
                "cta": "Serap Hano Akademi davet cümlesi."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen %100 Türkçe konuşan bilge bir ruhsal rehbersin. Kullanıcı verilerini psikolojik mekanizmalara dönüştürürsün. İngilizce kelime kullanamazsın."},
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"},
                temperature=0.65 # Yaratıcılık ve 'insani' dokunuş için artırıldı
            )
            
            res_data = json.loads(completion.choices[0].message.content)
            placeholder.empty()

            # --- EKRAN ---
            st.markdown("---")
            st.subheader("Ruhsal Haritan ve Atasal Mirasın")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Sana Miras Kalan Güç**")
                for i in res_data.get('isik', []): st.markdown(f'<div class="success-box">{html.escape(i)}</div>', unsafe_allow_html=True)
            with c2:
                st.write("🟠 **Dönüşmeyi Bekleyen Yük**")
                for g in res_data.get('golge', []): st.markdown(f'<div class="error-box">{html.escape(g)}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{html.escape(res_data.get("analiz", ""))}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Ruhuna Soru:** {html.escape(res_data.get('soru', ''))}")
            
            cta = res_data.get('cta', '')
            if cta:
                st.markdown(f"<div style='text-align: center; border: 2px dashed #4caf50; padding: 30px; border-radius: 20px; color: #2e7d32; font-weight: bold; background: #f1f8e9;'>🎯 {html.escape(cta)}</div>", unsafe_allow_html=True)

            # --- KART VE PAYLAŞIM ---
            tilsim_kartlari = {
                "Sağlık & Enerji": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-saglik.webp",
                "Özgüven & Özdeğer": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-ozguven-ozdeger.webp",
                "Kariyer": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-kariyer.webp",
                "Para & Bereket": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-para-bereket.webp",
                "İlişkiler": "https://www.seraphano.com/wp-content/uploads/2026/04/tilsimli-kartlar-iliskiler.webp"
            }
            if tikaniklik in tilsim_kartlari:
                st.image(tilsim_kartlari[tikaniklik], use_container_width=True)
                share_msg = urllib.parse.quote(f"Köklerin Gizemi analizimi yaptım! ✨ Sen de denemelisin: https://seraphano-analiz.streamlit.app")
                st.markdown(f"<div style='text-align: center; margin-top: 15px;'><a href='https://api.whatsapp.com/send?text={share_msg}' target='_blank' style='background-color: #25D366; color: white; padding: 12px 25px; text-decoration: none; border-radius: 30px; font-weight: bold;'>🌿 WhatsApp'ta Paylaş</a></div>", unsafe_allow_html=True)

            st.balloons()

            # Kayıt
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, "tikaniklik": tikaniklik,
                    "analiz": res_data.get('analiz', ''), "soru": res_data.get('soru', '')
                }, timeout=15)
            except: pass

        except Exception as e:
            st.error("Bir enerji yoğunluğu oluştu, lütfen formu tekrar gönderin.")
