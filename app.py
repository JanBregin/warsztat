import streamlit as st
import json
import base64

# 🔴 TUTAJ WPISZ SWÓJ NOWY ADRES (np. https://super-warsztat.streamlit.app)
MOJ_ADRES_APLIKACJI = "https://TUTAJ_WPISZ_SWOJ_NOWY_ADRES.streamlit.app"

st.set_page_config(page_title="Warsztat - Status Naprawy", page_icon="🔧", layout="centered")

def encode_data(data_dict):
    json_str = json.dumps(data_dict)
    return base64.urlsafe_b64encode(json_str.encode()).decode()

def decode_data(encoded_str):
    try:
        json_str = base64.urlsafe_b64decode(encoded_str.encode()).decode()
        return json.loads(json_str)
    except:
        return None

query_params = st.query_params

if "view" in query_params:
    # WIDOK DLA KLIENTA
    encoded_str = query_params["view"]
    data = decode_data(encoded_str)
    
    if data:
        st.title("📋 Raport Stanu Pojazdu")
        st.subheader(f"🚗 {data.get('auto', 'Samochód')}")
        st.caption(f"Numer rejestracyjny: {data.get('nr_rej', 'Brak')}")
        st.write("---")
        
        def wyświetl_status(komponent, status):
            if "dobry" in status.lower() or "ok" in status.lower():
                st.success(f"✅ **{komponent}:** {status}")
            elif "wymiany" in status.lower() or "pilne" in status.lower():
                st.error(f"🚨 **{komponent}:** {status}")
            else:
                st.warning(f"⚠️ **{komponent}:** {status}")

        wyświetl_status("Hamulce", data.get('hamulce', 'Brak danych'))
        wyświetl_status("Olej silnikowy", data.get('olej', 'Brak danych'))
        wyświetl_status("Zawieszenie", data.get('zawieszenie', 'Brak danych'))
        wyświetl_status("Opony", data.get('opony', 'Brak danych'))
        
        if data.get('uwagi'):
            st.write("---")
            st.info(f"💬 **Uwagi mechanika:**\n\n{data.get('uwagi')}")
            
        st.write("---")
        st.caption("Dziękujemy za skorzystanie z naszych usług!")
    else:
        st.error("Błąd! Link jest nieprawidłowy.")

else:
    # WIDOK DLA MECHANIKA
    st.title("🔧 Panel Mechanika")
    st.write("Wprowadź dane pojazdu, aby wygenerować link dla klienta.")
    
    with st.form("mechanic_form"):
        auto = st.text_input("Marka i model", placeholder="np. Audi A4 B8")
        nr_rej = st.text_input("Numer rejestracyjny", placeholder="np. WI 12345")
        
        st.write("---")
        hamulce = st.selectbox("Stan hamulców", ["Stan dobry (OK)", "Do wymiany wkrótce", "Wymiana PILNA!"])
        olej = st.selectbox("Olej i filtry", ["Stan dobry (OK)", "Do wymiany", "Wymieniono podczas wizyty"])
        zawieszenie = st.selectbox("Zawieszenie", ["Stan dobry (OK)", "Wykryto luzy (do naprawy)", "Wymaga pilnej naprawy"])
        opony = st.selectbox("Stan opon", ["Stan dobry (OK)", "Bieżnik na wykończeniu", "Zalecana wymiana"])
        
        uwagi = st.text_area("Dodatkowe uwagi / co zostało zrobione")
        
        skonfiguruj = st.form_submit_button("Generuj Link dla Klienta")
        
        if skonfiguruj:
            paczka_danych = {
                "auto": auto,
                "nr_rej": nr_rej,
                "hamulce": hamulce,
                "olej": olej,
                "zawieszenie": zawieszenie,
                "opony": opony,
                "uwagi": uwagi
            }
            
            kod = encode_data(paczka_danych)
            
            # Tworzymy pełny, gotowy link
            czysty_url = MOJ_ADRES_APLIKACJI.strip("/")
            pelny_link = f"{czysty_url}/?view={kod}"
            
            st.success("🎉 Link wygenerowany pomyślnie!")
            st.write("Skopiuj poniższy link i wyślij go klientowi (SMS / WhatsApp):")
            
            # Okienko z linkiem, które na iPhonie można łatwo skopiować jednym kliknięciem
            st.code(pelny_link)
