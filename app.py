import streamlit as st
from groq import Groq
import json
import time
import re
import requests
import html
from datetime import date
import urllib.parse

# 1. KRİTİK: Page config her zaman ilk sırada olmalı
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

# --- CSS TASARIM VE GİZLEME ---
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

# --- BAĞLANTI KONTROLÜ ---
client = None
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]
    else:
        st.error("Sistem ayarları (API Key) eksik. Lütfen kontrol edin.")
except Exception as e:
    st.error(f"Bağlantı hatası: {e}")

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın bilgeliğine hoş geldin.")

# --- FORM BÖLÜMÜ ---
with st.form("analiz_formu"):
    st.write("### Ruhsal ve Sistemik Kayıtlarınızı Açın")
    email = st.text_input("E-posta adresiniz:", placeholder="analiziniz kayıt altına alınacak...")
    
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
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz? (Düşük, kürtaj ve kayıpları dahil ederek)", min_value=1, step=1)
    
    aile_evlilik = st.selectbox("Ebeveynlerinizin evlilik temeli nedir?", 
                                ["Severek evlendiler", "Görücü usulü", "Zorunlu / Mantık evliliği", "Bilmiyorum"])
    
    dislanan_biri = st.selectbox("Ailenizde dışlanmış, hakkı yenmiş veya adı hiç anılmayan biri var mı?", 
                                 ["Evet, var", "Hayır, yok", "Emin değilim"])
    
    agir_yazgi = st.selectbox("Aile geçmişinde ağır bir yazgı (İntihar, erken kayıp, iflas, göç) mevcut mu?", 
                              ["Evet, büyük travmalar var", "Hayır, sakin bir geçmiş", "Bazı zorluklar var"])

    kisisel_travma = st.selectbox("Geçmişinizde derin iz bırakan bir depresyon veya travma yaşadınız mı?",
                                  ["Evet, yaşadım", "Hayır, yaşamadım", "Belirsiz"])
    
    tikaniklik = st.selectbox("Şifalanmasını istediğiniz alan:", 
                              ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    kvkk_onay = st.checkbox("Verilerimin analiz edilmesi ve kaydedilmesine (KVKK) onay veriyorum.")
    
    submit = st.form_submit_button("Sistemik Analizi Başlat")

# --- ANALİZ SÜRECİ ---
if submit:
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
    
    if not client:
        st.error("API bağlantısı kurulamadı.")
    elif not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    elif not kvkk_onay:
        st.warning("Devam etmek için KVKK onayını işaretlemeniz gerekmektedir.")
    elif yas < 15:
        st.warning(f"Sistemik analizler 15 yaş ve üzeri için uygundur. Yaşınız: {yas}")
    else:
        placeholder = st.empty()
        placeholder.info("Kökler taranıyor, sistemik alan mühürleniyor...")

        try:
            # TÜM VERİLERİN PROMPT'A EKLENDİĞİ MASTER TALİMAT
            prompt_metni = f"""
            KULLANICI BİLGİLERİ (BUNLARI ANALİZ ET AMA RAKAM OLARAK TEKRARLAMA):
            - Yaş/Cinsiyet: {yas} yaşında {cinsiyet}
            - Kardeş Sırası: {kardes_sirasi}. çocuk (Sistem dizimi hiyerarşisi için önemli)
            - Doğum Saati: {dogum_saati}
            - Ebeveyn İlişkisi: {aile_evlilik}
            - Ailede Dışlanan/Hakkı Yenen: {dislanan_biri}
            - Atasal Yazgı: {agir_yazgi}
            - Kişisel Travma Geçmişi: {kisisel_travma}
            - Odaklanılan Tıkanıklık: {tikaniklik}

            GÖREV:
            Sen Serap Hano'sun. Bilge, mistik ve uzman bir Sistem Dizimi rehberisin. 
            Bu verileri birleştirerek 'Sen' diliyle, edebi, sarsıcı ve şifalı bir analiz yap.
            Yaş skalasına göre (15-25: arayış, 25-45: inşa, 45-60: hasat, 60+: bilgelik) tonlamanı ayarla.
            Asla İngilizce veya yabancı karakter kullanma.

            SADECE ŞU JSON FORMATINDA CEVAP VER:
            {{
                "isik": ["Sistemik Güç 1", "Sistemik Güç 2"],
                "golge": ["Taşınan Yük 1", "Taşınan Yük 2"],
                "analiz": "En az 250 kelimelik derin analiz metni...",
                "soru": "Ruhsal yüzleşme sorusu...",
                "cta": "Serap Hano Akademi davet cümlesi..."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen %100 Türkçe konuşan, usta bir edebiyatçı ve sistem dizimi uzmanısın. JSON dışında karakter üretme."},
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"},
                timeout=25
            )
            
            # JSON PARSE VE DOĞRULAMA (1. Madde Çözümü)
            try:
                res_data = json.loads(completion.choices[0].message.content)
                # Anahtar kontrolü
                for key in ["isik", "golge", "analiz", "soru", "cta"]:
                    if key not in res_data: res_data[key] = "..."
            except (json.JSONDecodeError, KeyError):
                st.error("Analiz motoru geçici bir hata verdi, lütfen formu tekrar gönderin.")
                st.stop()

            placeholder.empty()

            # --- EKRAN ÇIKTILARI (XSS Korumalı) ---
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

            # Analiz metni
            st.markdown(f'<div class="main-text">{html.escape(res_data.get("analiz", ""))}</div>', unsafe_allow_html=True)
            
            # Soru ve CTA
            st.warning(f"🔍 **Ruhuna Soru:** {html.escape(res_data.get('soru', ''))}")
            
            cta = res_data.get('cta', '')
            if cta:
                st.markdown(f"<div style='text-align: center; border: 2px dashed #4caf50; padding: 25px; border-radius: 15px; background: #f1f8e9; color: #2e7d32; font-weight: bold;'>🎯 {html.escape(cta)}</div>", unsafe_allow_html=True)

            # --- KART EŞLEŞTİRME ---
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
                
                # Paylaşım linki
                share_msg = urllib.parse.quote(f"Köklerin Gizemi analizimi yaptım! Ruhumun bugünkü tılsımı: {tikaniklik}. Sen de denemelisin: https://seraphano-analiz.streamlit.app")
                st.markdown(f"<div style='text-align: center; margin-top: 15px;'><a href='https://api.whatsapp.com/send?text={share_msg}' target='_blank' style='background-color: #25D366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 30px; font-weight: bold;'>🌿 WhatsApp'ta Paylaş</a></div>", unsafe_allow_html=True)

            st.balloons()

            # --- VERİ KAYDI (Google Scripts) ---
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, 
                    "detay": f"Yas:{yas}, Cin:{cinsiyet}, Sira:{kardes_sirasi}, Evlilik:{aile_evlilik}, Dışlanan:{dislanan_biri}, Yazgı:{agir_yazgi}, Travma:{kisisel_travma}",
                    "tikaniklik": tikaniklik,
                    "analiz": res_data.get('analiz', ''),
                    "soru": res_data.get('soru', '')
                }, timeout=15)
            except Exception as log_e:
                print(f"Kayıt Hatası: {log_e}") # Loglara basar ama kullanıcıyı durdurmaz

        except Exception as e:
            st.error(f"Sistemik alanda bir enerji yoğunluğu oluştu, lütfen birazdan tekrar deneyin.")
            print(f"Hata Detayı: {e}")
