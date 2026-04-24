import streamlit as st
from groq import Groq
import json
import time
import re
import requests

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
    .systemic-note { font-size: 14px; color: #777; font-style: italic; text-align: center; margin-top: 30px; padding: 15px; border-top: 1px solid #eee; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Köklerin Gizemi")
st.write("Sistemik alanın bilgeliğine hoş geldin.")

# --- DİL MUHAFIZI ---
def turkcelestir(metin):
    sozluk = {
        "experiences": "deneyimler", "experience": "deneyim",
        "life": "yaşam", "decision": "karar", "decisions": "kararlar",
        "sometimes": "bazen", "health": "sağlık"
    }
    for ing, tr in sozluk.items():
        metin = re.sub(rf'\b{ing}\b', tr, metin, flags=re.IGNORECASE)
    return metin

def veriyi_al(data, key):
    val = data.get(key, "")
    if isinstance(val, list):
        return [turkcelestir(str(next(iter(i.values())) if isinstance(i, dict) else i)) for i in val]
    if isinstance(val, dict):
        return turkcelestir(str(next(iter(val.values()), "")))
    return turkcelestir(str(val))

def email_gecerli_mi(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

# --- FORM ---
with st.form("analiz_formu"):
    st.write("### Ruhsal ve Sistemik Kayıtlarınızı Açın")
    email = st.text_input("E-posta adresiniz:", placeholder="analiziniz buraya gönderilecek...")
    
    col1, col2 = st.columns(2)
    with col1:
        dogum_tarihi = st.date_input("Doğum Tarihiniz", min_value=None)
    with col2:
        dogum_saati = st.time_input("Doğum Saatiniz (Yaklaşık)")

    st.write("---")
    
    kardes_sirasi = st.number_input("Annenizin kaçıncı çocuğusunuz? (Düşük, kürtaj ve kayıpları sayarak)", min_value=1, step=1)
    
    aile_evlilik = st.selectbox("Ebeveynlerinizin evlilik temeli nedir?", 
                                ["Severek evlendiler", "Görücü usulü", "Zorunlu / Mantık evliliği", "Bilmiyorum"])
    
    dislanan_biri = st.selectbox("Ailenizde dışlanmış, hakkı yenmiş veya adı hiç anılmayan biri var mı?", 
                                 ["Evet, var", "Hayır, yok", "Emin değilim ama hissediyorum"])
    
    agir_yazgi = st.selectbox("Aile geçmişinde ağır bir yazgı (İntihar, erken kayıp, iflas, göç) mevcut mu?", 
                              ["Evet, büyük travmalar var", "Hayır, sakin bir geçmiş", "Bazı zorluklar var"])

    kisisel_travma = st.selectbox("Geçmişinizde derin iz bırakan bir depresyon veya travma yaşadınız mı?",
                                  ["Evet, yaşadım", "Hayır, yaşamadım", "Hatırlamak istemiyorum / Belirsiz"])
    
    tikaniklik = st.selectbox("Şifalanmasını ve açılmasını istediğiniz yaşam alanı:", 
                              ["İlişkiler", "Para & Bereket", "Kariyer", "Özgüven & Özdeğer", "Sağlık & Enerji"])
    
    submit = st.form_submit_button("Sistemik Analizi Başlat")

if submit:
    if not email or not email_gecerli_mi(email):
        st.error("Lütfen geçerli bir e-posta adresi girin.")
    else:
        placeholder = st.empty()
        for step in ["Kökler taranıyor...", "Atasal bağlar inceleniyor...", "Sistemik alan mühürleniyor..."]:
            with placeholder.container():
                st.info(step)
                time.sleep(2)
        placeholder.empty()

        try:
            # --- DERİN SİSTEMİK PROMPT ---
            prompt_metni = f"""
            Sen Serap Hano'sun. Bilge, samimi ve sarsıcı tespitler yapabilen bir Sistem Dizimi rehberisin. 
            Kullanıcı Bilgileri:
            - Kardeş Sırası: {kardes_sirasi}
            - Doğum Saati: {dogum_saati}
            - Ebeveyn Evliliği: {aile_evlilik}
            - Dışlanan Biri: {dislanan_biri}
            - Aile Yazgısı: {agir_yazgi}
            - Kişisel Travma: {kisisel_travma}
            - Tıkanıklık Alanı: {tikaniklik}

            GÖREVİN:
            Bu verileri bir 'sistem dedektifi' gibi birleştirerek hayret uyandırıcı bir analiz yap. 
            'Belki' veya 'Olabilir' gibi zayıf kelimeler kullanma. 
            Örnek: Eğer dışlanan biri varsa ve tıkanıklık paraysa; bu paranın o kişinin iade-i itibarı için sistem tarafından kilitlendiğini vurgula.
            Doğum saatini 'mizaç ve enerji alanı' (gece gizemi, öğle görünürlüğü gibi) olarak analize yedir.

            JSON FORMATINDA CEVAP VER:
            {{
                "isik": ["Sistemik Gücün 1", "Sistemik Gücün 2"],
                "golge": ["Taşıdığın Yük 1", "Taşıdığın Yük 2"],
                "analiz": "En az 250 kelimelik, edebi derinliği yüksek, sarsıcı ve şifalı analiz metni...",
                "soru": "Ruhun uykusunu kaçıracak o can alıcı soru...",
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
                isiklar = veriyi_al(res_data, 'isik')
                if isinstance(isiklar, list):
                    for i in isiklar: st.markdown(f'<div class="success-box">{i}</div>', unsafe_allow_html=True)
                else: st.markdown(f'<div class="success-box">{isiklar}</div>', unsafe_allow_html=True)
            
            with c2:
                st.write("🟠 **Sistemik Gölgen (Taşıdığın Yük)**")
                golgeler = veriyi_al(res_data, 'golge')
                if isinstance(golgeler, list):
                    for g in golgeler: st.markdown(f'<div class="error-box">{g}</div>', unsafe_allow_html=True)
                else: st.markdown(f'<div class="error-box">{golgeler}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="main-text">{veriyi_al(res_data, "analiz")}</div>', unsafe_allow_html=True)
            st.warning(f"🔍 **Ruhuna Soru:** {veriyi_al(res_data, 'soru')}")
            
            cta_text = veriyi_al(res_data, 'cta')
            st.markdown(f"<h3 style='text-align: center; color: #2e7d32; padding: 25px; border: 2px dashed #4caf50; border-radius: 15px; background: #f1f8e9;'>🎯 {cta_text}</h3>", unsafe_allow_html=True)
            
            # --- 🃏 RUH KARTI VE PAYLAŞIM ALANI ---
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
                st.markdown(f"""
                    <div style='text-align: center; padding: 15px; background-color: #f1f8e9; border-radius: 10px; color: #2e7d32; font-weight: bold;'>
                        Bu kart, {tikaniklik} alanındaki dönüşümün için sana rehberlik edecek sembolleri taşıyor.
                    </div>
                """, unsafe_allow_html=True)

                # --- 📱 SOSYAL MEDYA PAYLAŞIM ---
                import urllib.parse
                share_text = f"Serap Hano Akademi'de Köklerin Gizemi analizimi yaptım! ✨ Sen de denemelisin: https://seraphano-analiz.streamlit.app"
                safe_text = urllib.parse.quote(share_text)
                
                wa_url = f"https://api.whatsapp.com/send?text={safe_text}"
                fb_url = f"https://www.facebook.com/sharer/sharer.php?u=https://seraphano-analiz.streamlit.app"
                
                st.markdown(f"""
                    <div style='display: flex; justify-content: center; gap: 10px; margin: 20px 0;'>
                        <a href="{wa_url}" target="_blank" style="background-color: #25D366; color: white; padding: 10px 15px; text-decoration: none; border-radius: 10px; font-size: 14px; font-weight: bold;">WhatsApp</a>
                        <a href="{fb_url}" target="_blank" style="background-color: #1877F2; color: white; padding: 10px 15px; text-decoration: none; border-radius: 10px; font-size: 14px; font-weight: bold;">Facebook</a>
                        <button onclick="navigator.clipboard.writeText('https://seraphano-analiz.streamlit.app'); alert('Link kopyalandı! Instagram hikayende paylaşabilirsin ✨');" style="background-color: #E1306C; color: white; padding: 10px 15px; border: none; border-radius: 10px; font-size: 14px; font-weight: bold; cursor: pointer;">Instagram (Link)</button>
                    </div>
                """, unsafe_allow_html=True)

            # --- 🎈 BALONLAR ---
            st.balloons()

            # --- 💾 ARKA PLAN KAYDI ---
            try:
                analiz_metni = veriyi_al(res_data, "analiz")
                soru_metni = veriyi_al(res_data, 'soru')
                requests.post(SCRIPT_URL, json={
                    "email": email, 
                    "detay": f"Sira:{kardes_sirasi}, Evlilik:{aile_evlilik}, Dislanan:{dislanan_biri}",
                    "tikaniklik": tikaniklik,
                    "analiz": analiz_metni,
                    "soru": soru_metni
                }, timeout=10)
            except:
                pass

        except Exception as e:
            st.error(f"Sistemik alanda bir karışıklık oluştu: {e}")
