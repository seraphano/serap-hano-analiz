import streamlit as st
from groq import Groq
import json
import requests
import html
from datetime import date
import urllib.parse
import random

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
    .success-box { 
        background-color: #f4faf6; color: #2d5a3f; border-left: 10px solid #4caf50; 
    }
    .error-box { 
        background-color: #fff9f2; color: #855d21; border-left: 10px solid #ff9800; 
    }
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
if "soru_hakki" not in st.session_state:
    st.session_state.soru_hakki = 3

if "analiz_bitti" not in st.session_state:
    st.session_state.analiz_bitti = False
st.write("Sadece verilerin değil, senin hikayenin sessiz yankıları.")

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Ruhsal Kayıtlarını Aç")
    email = st.text_input("E-posta adresin:", placeholder="analizin buraya mühürlenecek...")
    
    col_c, col_y = st.columns(2)
    with col_c:
        cinsiyet = st.selectbox(
            "Cinsiyetin:", 
            ["Kadın", "Erkek", "Belirtmek İstemiyorum"]
        )
    with col_y:
        dogum_tarihi = st.date_input(
            "Doğum Tarihin", 
            min_value=date(1920, 1, 1), 
            value=date(1990, 1, 1)
        )

    dogum_saati = st.time_input("Doğum Saatin (Yaklaşık)")

    st.write("---")
    kardes_sirasi = st.number_input(
        "Kaçıncı çocuksun? (Düşük/Kayıplar dahil)", 
        min_value=1, step=1
    )
    aile_evlilik = st.selectbox(
        "EBEVEYNLERİNİN evliliği?", 
        ["Severek evlendiler", "Görücü usulü", "Mantık/Zorunlu evlilik", "Bilmiyorum"]
    )
    dislanan_biri = st.selectbox(
        "AİLEDE dışlanan/hakkı yenen biri var mı?", 
        ["Evet, var", "Hayır, yok", "Emin değilim"]
    )
    agir_yazgi = st.selectbox(
        "AİLEDE ağır bir yazgı (İntihar, iflas, erken ölüm)?", 
        ["Evet, var", "Hayır, yok", "Bazı zorluklar var"]
    )
    kisisel_travma = st.selectbox(
        "SİZİN geçmişinizde derin bir travma/depresyon oldu mu?", 
        ["Evet", "Hayır", "Belirsiz"]
    )
    tikaniklik = st.selectbox(
        "Şifalanmasını istediğin alan:", 
        ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"]
    )
    
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
            if dogum_saati.hour < 6: 
                saat_notu = (
                    "Şafak öncesinin derin sessizliği; "
                    "saklıyı görme ve kökleri şifalandırma gücü."
                )
            elif dogum_saati.hour < 12: 
                saat_notu = (
                    "Sabahın yükselen iradesi; "
                    "tıkanıklıkları cesaretle dönüştürme potansiyeli."
                )
            else: 
                saat_notu = (
                    "Gecenin bilinçaltı rehberliği; "
                    "ruhsal köprüler kurma ve sezgisel derinlik."
                )

            # --- TIKANIKLIĞA ÖZEL ACIMASIZ ODAK ---
            odak_talimati = ""
            if tikaniklik == "İlişkiler":
                odak_talimati = (
                    "İlişkisel Kader Haritası: Bu kişinin en uyumlu olduğu insan tiplerini değil, "
                    "'neden hep aynı yarayı taşıyanları çektiğini' analiz et. Ailedeki sevgisizlik "
                    "veya dışlanma döngüsünün onun partner seçimlerini nasıl kilitlediğini "
                    "acımasızca dürüst bir dille yüzleştir."
                )
            elif tikaniklik == "Para & Bereket":
                odak_talimati = (
                    "Zenginlik ve Bolluk Kodu: Bu kişinin parasal büyümesini engelleyen görünmez "
                    "sadakat yeminini deşifre et. Atalarındaki iflas veya kıtlık bilincinin onun "
                    "'fazlasını hak etmeme' inancını nasıl yarattığını vurucu bir şekilde ortaya çıkar."
                )
            elif tikaniklik == "Kariyer":
                odak_talimati = (
                    "Profesyonel Kader Dedektörü: Bu kişinin karar alma tarzındaki korkuları analiz et. "
                    "Potansiyelini gerçekleştirmesini engelleyen asıl şeyin yeteneksizlik değil, "
                    "'aileden daha başarılı olma korkusu' veya 'görünmez kalma çabası' olduğunu anlat."
                )
            elif tikaniklik == "Özgüven & Özdeğer":
                odak_talimati = (
                    "Hayat Yolunun Çözücüsü: Gizli zayıflıklarını ve maskelerini düşür. Kendi değerini "
                    "dışarıdan onay bekleyerek aramasının altındaki o ilk reddedilişi (kardeş sırası "
                    "veya ebeveyn bağı üzerinden) bul ve önüne koy."
                )
            elif tikaniklik == "Sağlık & Enerji":
                odak_talimati = (
                    "Ruhun Amacının Keşfedicisi: Bedeninin aslında ruhunun taşıyamadığı hangi atasal "
                    "yükleri taşıdığını göster. Ağrılarının veya enerjisizliğinin aslında 'kime ait "
                    "olduğunu' ona şiirsel ama net bir şekilde söyle."
                )

            # V14 - DİNAMİK VE ACIMASIZ PROJEKSİYON PROMPT
            prompt_metni = (
                "ROL: Sen usta bir Sistem Dizimi uzmanı Serap Hano'sun. Bilge, şiirsel, sarsıcı ve "
                "insanın ruhuna dokunan bir dille konuşuyorsun. \n"
                "AMACIN: Danışanın verilerini asla tekrar etmeden, onlara 'Beni biri sonunda "
                "gerçekten gördü' hissini yaşatmak.\n\n"
                "KÖK MEKANİZMALARI:\n"
                f"- Ebeveyn Evliliği: {aile_evlilik}\n"
                f"- Ailede Dışlanan: {dislanan_biri}\n"
                f"- Atasal Yazgı: {agir_yazgi}\n\n"
                "DANIŞAN MEKANİZMALARI:\n"
                f"- Profil: {yas} yaşında {cinsiyet}, {kardes_sirasi}. çocuk.\n"
                f"- Gündem: {tikaniklik}, Enerji: {saat_notu}\n\n"
                "ÖZEL GÖREVİN:\n"
                f"{odak_talimati}\n\n"
                "METİN AKIŞI:\n"
                "1. GÖRÜLME: Saklanan yorgunluğu anlat.\n"
                "2. YARA: Kök verilerini metaforlara dönüştür ve özel görevinle bağla.\n"
                f"3. ÇATIŞMA: Tıkanıklık alanının ({tikaniklik}) hangi atasal yasa sadık kaldığını fısılda.\n"
                "4. ÇÖZÜLME: Sarsıcı bir umutla bitir.\n\n"
                "YASAKLAR:\n"
                "- ASLA rakam ve veri isimlerini olduğu gibi yazma.\n"
                "- 'yolculuk', 'iç ışık', 'gizem', 'mucize', 'mümkün', 'enerji' kelimelerini kullanma.\n"
                "- Robotik paragraflar yerine; kısa, ritmik cümleler kur.\n\n"
                "EK GÖREVLER:\n"
"- Kullanıcıya gelecekteki halinden bir mektup yaz.\n"
"- Kullanıcının hayatını sinema fragmanı gibi anlat.\n"
"- Ruh yaşını açıklayan kısa bir yorum üret.\n"
"- Tamamen sembolik aile hikayesi oluştur.\n"
"- Bunları gerçek bilgi gibi değil metaforik anlat.\n\n"
               "JSON ÇIKTI:\n"
"{\n"
'  "isik": ["madde","madde"],\n'
'  "golge": ["madde","madde"],\n'
'  "analiz": "metin",\n'
'  "soru": "soru",\n'
'  "cta": "cta",\n'
'  "gelecek_mektubu": "7 yıl sonraki halinden gelen mektup",\n'
'  "hayat_fragmani": "Netflix tarzı hayat fragmanı",\n'
'  "ruh_yasi_yorumu": "ruh yaşını açıklayan metin",\n'
'  "sembolik_aile_hikayesi": "tamamen sembolik aile anlatısı"\n'
"}"
            )
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "Sen %100 Türkçe konuşan bilge bir ruhsal rehbersin. "
                            "Kullanıcı verilerini psikolojik mekanizmalara dönüştürürsün. "
                            "İngilizce kelime kullanamazsın."
                        )
                    },
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"},
                temperature=0.65 
            )
            
            res_data = json.loads(completion.choices[0].message.content)
            placeholder.empty()

            # --- EKRAN ---
            st.markdown("---")
            st.subheader("Ruhsal Haritan ve Atasal Mirasın")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Sana Miras Kalan Güç**")
                for i in res_data.get('isik', []): 
                    st.markdown(f'<div class="success-box">{html.escape(i)}</div>', unsafe_allow_html=True)
            with c2:
                st.write("🟠 **Dönüşmeyi Bekleyen Yük**")
                for g in res_data.get('golge', []): 
                    st.markdown(f'<div class="error-box">{html.escape(g)}</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div class="main-text">{html.escape(res_data.get("analiz", ""))}</div>', 
                unsafe_allow_html=True
            )
            st.warning(f"🔍 **Ruhuna Soru:** {html.escape(res_data.get('soru', ''))}")
            
            cta = res_data.get('cta', '')
            if cta:
                st.markdown(
                    f"<div style='text-align: center; border: 2px dashed #4caf50; padding: 30px; "
                    f"border-radius: 20px; color: #2e7d32; font-weight: bold; background: #f1f8e9;'>"
                    f"🎯 {html.escape(cta)}</div>", 
                    unsafe_allow_html=True
                )

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
                
                mesaj = "Köklerin Gizemi analizimi yaptım! ✨ Sen de denemelisin: https://seraphano-analiz.streamlit.app"
                share_msg = urllib.parse.quote(mesaj)
                
                st.markdown(
                    f"<div style='text-align: center; margin-top: 15px;'>"
                    f"<a href='https://api.whatsapp.com/send?text={share_msg}' "
                    f"target='_blank' style='background-color: #25D366; color: white; "
                    f"padding: 12px 25px; text-decoration: none; border-radius: 30px; "
                    f"font-weight: bold;'>🌿 WhatsApp'ta Paylaş</a></div>", 
                    unsafe_allow_html=True
                )
st.markdown("---")
st.subheader("⏳ Ruh Yaşın")

ruh_yasi = yas + random.randint(7, 24)

st.metric(
    "Hissedilen Ruh Yaşı",
    ruh_yasi
)

st.info(
    res_data.get(
        "ruh_yasi_yorumu",
        ""
    )
)
            st.balloons()

            # Kayıt
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, "tikaniklik": tikaniklik,
                    "analiz": res_data.get('analiz', ''), "soru": res_data.get('soru', '')
                }, timeout=15)
            except: 
                pass

        except Exception as e:
            st.error("Bir enerji yoğunluğu oluştu, lütfen formu tekrar gönderin.")
