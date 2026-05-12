import streamlit as st
from groq import Groq
import json
import time
import re
import requests
import html
from datetime import date
import urllib.parse

# 1. Page Config (Zorunlu olarak en üstte)
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

# --- GÖRSEL TASARIM VE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfcfb; }
    .success-box { background-color: #e8f5e9; padding: 22px; border-radius: 18px; border-left: 8px solid #4caf50; margin-bottom: 15px; color: #2e7d32; font-size: 16px; font-weight: 500; }
    .error-box { background-color: #fff3e0; padding: 22px; border-radius: 18px; border-left: 8px solid #ff9800; margin-bottom: 15px; color: #e65100; font-size: 16px; font-weight: 500; }
    .main-text { font-size: 20px; line-height: 2.3; color: #2c3e50; background: #fff; padding: 45px; border-radius: 30px; border: 1px solid #eee; margin-bottom: 30px; white-space: pre-wrap; box-shadow: 0 15px 40px rgba(0,0,0,0.04); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- BAĞLANTI ---
client = None
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]
else:
    st.error("Sistem ayarları (Secrets) bulunamadı!")

st.title("✨ Köklerin Gizemi")
st.write("Sistemik mirasın ve ruhsal tıkanıklıkların bilge analizi.")

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Ruhsal Kayıtlarınızı Açın")
    email = st.text_input("E-posta adresiniz:", placeholder="analiziniz mühürlenecek...")
    
    col_c, col_y = st.columns(2)
    with col_c:
        cinsiyet = st.selectbox("Cinsiyetiniz:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
    with col_y:
        dogum_tarihi = st.date_input("Doğum Tarihiniz", min_value=date(1920, 1, 1), value=date(1990, 1, 1))

    dogum_saati = st.time_input("Doğum Saatiniz (Yaklaşık)")

    st.write("---")
    kardes_sirasi = st.number_input("Kaçıncı çocuksunuz? (Kayıplar/Düşükler dahil)", min_value=1, step=1)
    aile_evlilik = st.selectbox("EBEVEYNLERİNİZİN evlilik temeli?", ["Severek evlendiler", "Görücü usulü", "Mantık/Zorunlu evlilik", "Bilmiyorum"])
    dislanan_biri = st.selectbox("AİLENİZDE dışlanmış veya hakkı yenen biri var mı?", ["Evet, var", "Hayır, yok", "Emin değilim"])
    agir_yazgi = st.selectbox("AİLE GEÇMİŞİNDE ağır bir yazgı (İntihar, göç, iflas, erken ölüm)?", ["Evet, var", "Hayır, yok", "Bazı zorluklar var"])
    kisisel_travma = st.selectbox("Geçmişinizde derin bir travma/depresyon oldu mu?", ["Evet", "Hayır", "Belirsiz"])
    tikaniklik = st.selectbox("Şifalanmasını istediğiniz alan:", ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    kvkk_onay = st.checkbox("Verilerimin sistemik analiz için işlenmesine onay veriyorum.")
    submit = st.form_submit_button("Dizimi Başlat")

# --- ANALİZ MOTORU ---
if submit:
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
    
    if not email or "@" not in email:
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    elif not kvkk_onay:
        st.warning("Devam etmek için KVKK onayını işaretlemelisiniz.")
    else:
        placeholder = st.empty()
        placeholder.info("Sistemik alan mühürleniyor, bilge rehber analizi hazırlıyor...")

        try:
            # Enerji İmzası
            saat_anlami = ""
            if dogum_saati.hour < 6: saat_anlami = "Şafak öncesi; aile sırlarını aydınlatma ve kadim yasları şifalandırma gücü."
            elif dogum_saati.hour < 12: saat_anlami = "Sabahın yükselen ışığı; tıkanıklıkları eylem ve cesaretle aşma potansiyeli."
            else: saat_anlami = "Akşamın derinliği; ruhsal rehberlik ve bilinçaltı köprüleri kurma misyonu."

            # PROMPT - "Umut ve Mekanizma" Odaklı
            prompt_metni = f"""
            ROL: Sen Serap Hano'sun. Bilge, şifacı, edebi bir dil kullanan ve danışana umut veren bir Sistem Dizimi uzmanısın.
            
            KULLANICI VERİLERİ (BUNLARI ASLA TEKRARLAMA):
            - Yaş/Cinsiyet: {yas}/{cinsiyet}, Sira: {kardes_sirasi}
            - Kökler: {aile_evlilik}, Dışlanan: {dislanan_biri}, Yazgı: {agir_yazgi}
            - Şahsi: {kisisel_travma}, Tıkanıklık: {tikaniklik}, Saat: {saat_anlami}

            ANALİZ STRATEJİSİ:
            1. ROBOTİK TEKRAR YASAKTIR: "27 yaşındasın", "Görücü usulü evlilik seçtiğin için", "{tikaniklik} yaşıyorsun" gibi verileri aynen yazma. 
            2. MEKANİZMAYI HİKAYELEŞTİR: Verileri birleştirip tek bir paragrafta şifa dolu bir hikaye yaz. 
               Örn: "Sevgisiz kurulmuş bir bağın gölgesinde, sen bugün aşkı bir görev gibi taşıyor olabilirsin. Ama bu miras senin kaderin değil, sadece fark edilmeyi bekleyen bir kilit."
            3. UMUT VER: Metnin sonu mutlaka ferahlık, umut ve şifalanma vaadiyle bitmeli. Danışan kendini "çözülmüş" ve "umutlu" hissetmeli.
            4. YASAKLAR: "yolculuk", "iç ışık", "gizem", "mucize", "mümkün", "only", "possible", "yönlendirebilir".
            5. DİL: Sadece 'SEN'. Akıcı, sarsıcı ve bilge bir Türkçe.

            JSON ÇIKTI:
            {{
                "isik": ["Sana miras kalan o gizli güç 1", "Ruhsal yeteneğin 2"],
                "golge": ["Bugün seni yoran o atasal yük 1", "Dönüşmesi gereken miras 2"],
                "analiz": "120-170 kelimelik, hikayeleştirilmiş, umut dolu, mekanizma odaklı ve sarsıcı analiz metni.",
                "soru": "Ruhunu uyandıracak o derin soru.",
                "cta": "Serap Hano Akademi davet cümlesi."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen %100 Türkçe konuşan bilge bir şifacısın. Kullanıcı verilerini papağan gibi tekrarlamaz, onları birer şifa hikayesine dönüştürürsün. İngilizce kelime kullanamazsın."},
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"},
                temperature=0.45
            )
            
            res_data = json.loads(completion.choices[0].message.content)
            placeholder.empty()

            # --- EKRAN ÇIKTISI ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız ve Atasal Kayıtlarınız")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Atasal Gücün (Işık)**")
                for i in res_data.get('isik', []): 
                    st.markdown(f'<div class="success-box">{html.escape(i)}</div>', unsafe_allow_html=True)
            with c2:
                st.write("🟠 **Atasal Mirasın (Gölge)**")
                for g in res_data.get('golge', []): 
                    st.markdown(f'<div class="error-box">{html.escape(g)}</div>', unsafe_allow_html=True)

            # Analiz Metni
            st.markdown(f'<div class="main-text">{html.escape(res_data.get("analiz", ""))}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Ruhuna Soru:** {html.escape(res_data.get('soru', ''))}")
            
            cta = res_data.get('cta', '')
            if cta:
                st.markdown(f"<div style='text-align: center; border: 2px dashed #4caf50; padding: 25px; border-radius: 15px; color: #2e7d32; font-weight: bold; background: #f1f8e9;'>🎯 {html.escape(cta)}</div>", unsafe_allow_html=True)

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
                share_msg = urllib.parse.quote(f"Serap Hano Akademi'de Köklerin Gizemi analizimi yaptım! ✨ Sen de denemelisin: https://seraphano-analiz.streamlit.app")
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
