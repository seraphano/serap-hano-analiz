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
    .main-text { font-size: 18px; line-height: 1.9; color: #333; background: #fff; padding: 30px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 25px; white-space: pre-wrap; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın bilgeliğine hoş geldin.")

# --- YARDIMCI FONKSİYONLAR ---
def veriyi_al(data, key):
    val = data.get(key, "")
    return str(val)

def email_gecerli_mi(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Ruhsal ve Sistemik Kayıtlarınızı Açın")
    email = st.text_input("E-posta adresiniz:", placeholder="analiziniz buraya gönderilecek...")
    
    col_c, col_y = st.columns(2)
    with col_c:
        cinsiyet = st.selectbox("Cinsiyetiniz:", ["Kadın", "Erkek", "Belirtmek İstemiyorum"])
    with col_y:
        # Doğum yılı sorununu burada çözdük: 1920'ye kadar izin veriyor
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
    if not email or not email_gecerli_mi(email):
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    else:
        # Yaş hesaplama
        yas = date.today().year - dogum_tarihi.year
        
        placeholder = st.empty()
        for step in ["Kökler taranıyor...", "Atasal bağlar inceleniyor...", "Sistemik alan mühürleniyor..."]:
            with placeholder.container():
                st.info(step)
                time.sleep(1.5)
        placeholder.empty()

        try:
            # --- GELİŞMİŞ SİSTEMİK PROMPT ---
            prompt_metni = f"""
            Sen Serap Hano'sun. Bilge, derin ve sarsıcı tespitler yapan bir Sistem Dizimi rehberisin. 
            Kullanıcı Bilgileri:
            - Cinsiyet: {cinsiyet}, Yaş: {yas}
            - Kardeş Sırası: {kardes_sirasi}
            - Doğum Saati: {dogum_saati}
            - Ebeveyn Evliliği: {aile_evlilik}, Dışlanan: {dislanan_biri}
            - Aile Yazgısı: {agir_yazgi}, Kişisel Travma: {kisisel_travma}
            - Tıkanıklık Alanı: {tikaniklik}

            ANALİZ KURALLARI (ÇOK KRİTİK):
            1. DİL: Sadece 'SEN' diye hitap et. Asla 'Siz' deme.
            2. ROBOTİK GİRİŞTEN KAÇIN: "Ebeveynlerinizin severek evlenmiş olması..." gibi kullanıcının seçtiği cümleyi tekrarlayarak başlama. 
            3. DERİNLİK: Kişinin yaşına ({yas}) ve cinsiyetine ({cinsiyet}) göre bir olgunluk seviyesi belirle. 
            4. BAĞLANTI: Veriler arasında köprü kur. Örneğin; erken bir kayıp varsa ve tıkanıklık paraysa, paranın bu yası tutmak için bir engel olduğunu anlat.
            5. HAYRET UYANDIR: Analizi okuduğunda kullanıcı "Bunu nasıl bildi?" desin. Doğum saatini mizacına yedir.

            JSON FORMATINDA CEVAP VER:
            {{
                "isik": ["Sistemik Gücün 1", "Sistemik Gücün 2"],
                "golge": ["Taşıdığın Yük 1", "Taşıdığın Yük 2"],
                "analiz": "En az 250 kelimelik, edebi, sarsıcı ve sadece 'sen' diliyle yazılmış analiz...",
                "soru": "Ruhunu uyandıracak o can alıcı soru...",
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
            st.subheader("Ruhsal Haritanız ve Atasal Kayıtlarınız")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("🌿 **Sistemik Işığın**")
                for i in res_data.get('isik', []): st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
            
            with c2:
                st.write("🟠 **Sistemik Gölgen (Taşıdığın Yük)**")
                for g in res_data.get('golge', []): st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{res_data.get("analiz", "")}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Ruhuna Soru:** {res_data.get('soru', '')}")
            
            st.markdown(f"<h3 style='text-align: center; color: #2e7d32; padding: 25px; border: 2px dashed #4caf50; border-radius: 15px; background: #f1f8e9;'>🎯 {res_data.get('cta', '')}</h3>", unsafe_allow_html=True)
            
            # --- 🃏 RUH KARTI VE PAYLAŞIM ---
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
                st.markdown("<div style='text-align: center; font-weight: bold;'>Bu kart senin için bir rehberdir.</div>", unsafe_allow_html=True)

                import urllib.parse
                share_text = f"Serap Hano Akademi'de Köklerin Gizemi analizimi yaptım! ✨ Sen de denemelisin: https://seraphano-analiz.streamlit.app"
                safe_text = urllib.parse.quote(share_text)
                wa_url = f"https://api.whatsapp.com/send?text={safe_text}"
                st.markdown(f"<div style='text-align: center; margin-top:20px;'><a href='{wa_url}' target='_blank' style='background-color: #25D366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 10px;'>WhatsApp'ta Paylaş</a></div>", unsafe_allow_html=True)

            st.balloons()

            # --- 💾 ARKA PLAN KAYDI ---
            try:
                requests.post(SCRIPT_URL, json={
                    "email": email, 
                    "detay": f"Yas:{yas}, Cin:{cinsiyet}, Sira:{kardes_sirasi}",
                    "tikaniklik": tikaniklik,
                    "analiz": res_data.get('analiz', ''),
                    "soru": res_data.get('soru', '')
                }, timeout=10)
            except: pass

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
