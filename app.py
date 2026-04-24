import streamlit as st
from groq import Groq
import json
import time
import re
import requests
from datetime import date

# 1. KURAL: page_config her zaman en başta olmalı (5. Madde çözümü)
st.set_page_config(page_title="Serap Hano Akademi | Analiz Rehberi", layout="centered")

# --- BAĞLANTI VE GÜVENLİK ---
client = None
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]
    else:
        st.error("API anahtarı bulunamadı. Lütfen secrets ayarlarını kontrol edin.")
except Exception as e:
    st.error(f"Bağlantı hatası: {e}")

# --- TASARIM (CSS) ---
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
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz? (Kayıplar dahil)", min_value=1, step=1)
    
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
    
    # 8. Madde: KVKK Onayı
    kvkk_onay = st.checkbox("Verilerimin analiz edilmesi ve kaydedilmesine (KVKK) onay veriyorum.")
    
    submit = st.form_submit_button("Sistemik Analizi Başlat")

if submit:
    # Kontroller
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year
    
    if not client:
        st.error("Sistem şu an çalışmıyor, lütfen yöneticiyle iletişime geçin.")
    elif not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    elif not kvkk_onay:
        st.warning("Devam etmek için lütfen kullanım şartlarını onaylayın.")
    elif yas < 15:
        st.warning(f"Analiz 15 yaş ve üzeri için uygundur. (Yaşınız: {yas})")
    else:
        placeholder = st.empty()
        placeholder.info("Sistemik alan mühürleniyor, lütfen bekleyin...")

        try:
            # 4, 9, 13. Maddeler: Tüm verilerin prompt'a girmesi ve skalalar
            prompt_metni = f"""
            KULLANICI VERİLERİ (ASLA RAKAMLA TEKRARLAMA, SADECE ANALİZ ET):
            - Yaş: {yas}, Cinsiyet: {cinsiyet}
            - Kardeş Sırası: {kardes_sirasi}
            - Doğum Saati: {dogum_saati}
            - Anne-Baba Evliliği: {aile_evlilik}
            - Ailede Dışlanan Biri: {dislanan_biri}
            - Ağır Yazgı/Travma: {agir_yazgi}
            - Kişisel Travma: {kisisel_travma}
            - Odaklanılan Tıkanıklık: {tikaniklik}

            ANALİZ REHBERİ (YAŞA GÖRE):
            15-25: Kimlik ve aidiyet. 25-45: İnşa ve yerleşme. 45-60: Hasat ve barışma. 60+: Bilgelik.

            FORMAT: Sadece JSON dön. Dil: %100 Türkçe, edebi ve samimi (Sadece 'SEN').
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen usta bir Sistem Dizimi uzmanı Serap Hano'sun. Bilge, mistik ve keskin tespitler yaparsın. Asla İngilizce kelime kullanmazsın."},
                    {"role": "user", "content": prompt_metni}
                ],
                response_format={"type": "json_object"}
            )
            
            # 1. Madde: JSON Fallback (Kırılma riski yönetimi)
            try:
                res_data = json.loads(completion.choices[0].message.content)
            except json.JSONDecodeError:
                st.error("Analiz motorunda bir hata oluştu, lütfen tekrar deneyin.")
                st.stop()

            placeholder.empty()

            # --- SONUÇLARI GÖSTER ---
            st.markdown("---")
            st.subheader("Ruhsal Haritanız ve Atasal Kayıtlarınız")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Sistemik Işığın**")
                for i in res_data.get('isik', []): st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
            with c2:
                st.write("🟠 **Sistemik Gölgen**")
                for g in res_data.get('golge', []): st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{res_data.get("analiz", "")}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Ruhuna Soru:** {res_data.get('soru', '')}")
            
            # 11. Madde: CTA Alanını göster
            cta = res_data.get('cta', '')
            if cta:
                st.markdown(f"<div style='text-align: center; border: 2px dashed #4caf50; padding: 20px; border-radius: 15px;'><b>🎯 {cta}</b></div>", unsafe_allow_html=True)
            
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

            st.balloons()

            # Arka Plan Kaydı
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, 
                    "detay": f"Yas:{yas}, Cin:{cinsiyet}, Yazgi:{agir_yazgi}, Travma:{kisisel_travma}",
                    "analiz": res_data.get('analiz', ''),
                    "soru": res_data.get('soru', '')
                }, timeout=10)
            except: pass

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
