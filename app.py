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
        # Takvimi Türkçeleştirmek için label ve kısıtlamalar
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
    if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    else:
        yas = date.today().year - dogum_tarihi.year
        
        placeholder = st.empty()
        for step in ["Kökler taranıyor...", "Atasal bağlar inceleniyor...", "Sistemik alan mühürleniyor..."]:
            with placeholder.container():
                st.info(step)
                time.sleep(1.5)
        placeholder.empty()

        try:
            # --- YENİLENMİŞ "ROBOT OLMAYAN" PROMPT ---
            prompt_metni = f"""
            ROL: Sen Serap Hano'sun. Bilge, mistik ve sistem dizimi konusunda uzman bir rehbersin.
            KULLANICI VERİLERİ: {yas} yaşında {cinsiyet}, {kardes_sirasi}. çocuk. Evlilik: {aile_evlilik}, Dışlanan: {dislanan_biri}, Yazgı: {agir_yazgi}, Travma: {kisisel_travma}, Saat: {dogum_saati}, Alan: {tikaniklik}.

            KATI KURALLAR:
            1. ASLA "Sen 45 yaşında bir erkeksin" veya "Görücü usulü evlilik nedeniyle" gibi veri tekrarları yapma. Kullanıcı bu verileri zaten biliyor.
            2. BU VERİLERİ ANALİZİN İÇİNE GİZLE. Örneğin; yaşından yola çıkarak "Hayatının bu olgunluk döneminde..." de. Saatinden yola çıkarak "Güneşin henüz doğduğu o anki enerji..." de ama saati rakamla yazma.
            3. DİL: Sadece 'SEN' diye hitap et. %100 Türkçe yaz. Asla İngilizce kelime kullanma. İmla kusursuz olsun.
            4. HİKAYE KUR: Eğer ailede dışlanan biri varsa, bunu direkt söyleme; "Köklerinde adı anılmayanların sessizliği, senin bugünkü {tikaniklik} yolculuğunda bir gölge gibi duruyor" de.
            5. ROBOTİK GİRİŞLERİ YASAKLA: Direkt ruhuna dokunarak başla.

            JSON ÇIKTI:
            {{
                "isik": ["Gizil bir güç örneği", "Bir ruhsal yetenek"],
                "golge": ["Taşınan sistemik yük", "Dönüşmesi gereken enerji"],
                "analiz": "En az 250 kelimelik, edebi, sarsıcı ve tamamen insani bir dille yazılmış analiz metni.",
                "soru": "Ruhsal bir yüzleşme sorusu.",
                "cta": "Serap Hano Akademi daveti."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_metni}],
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

            st.markdown(f'<div class="main-text">{res_data.get("analiz", "")}</div>', unsafe_allow_html=True)
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
                    "analiz": res_data.get('analiz', ''), "soru": res_data.get('soru', '')
                }, timeout=10)
            except: pass

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
