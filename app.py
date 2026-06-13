import streamlit as st
import json
import base64

# Ustawienia strony - mobilny wygląd
st.set_page_config(page_title="Warsztat - Status Naprawy", page_icon="🔧", layout="centered")

# Funkcje do kodowania i dekodowania danych w URL (zastępuje bazę danych)
def encode_data(data_dict):
    json_str = json.dumps(data_dict)
    return base64.urlsafe_b64encode(json_str.encode()).decode()

def decode_data(encoded_str):
    try:
        json_str = base64.urlsafe_b64decode(encoded_str.encode()).decode()
        return json.loads(json_str)
    except:
        return None

# Odczytanie parametrów z linku
query_params = st.query_params

if "view" in query_params:
    # -------------------------------------------------------------
    # WIDOK DLA KLIENTA (gdy ktoś wejdzie przez wygenerowany link)
    # -------------------------------------------------------------
    encoded_str = query_params["view"]
    data = decode_data(encoded_str)
    
    if data:
        st.title("📋 Raport Stanu Pojazdu")
        st.subheader(f"🚗 {data.get('auto', 'Samochód')}")
        st.caption(f"Numer rejestracyjny: {data.get('nr_rej', 'Brak')}")
        st.write("---")
        
        # Funkcja do ładnego wyświetlania statusów z kolorami
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
        st.caption("Dziękujemy za skorzystanie z naszych usług! Twój Warsztat.")
    else:
        st.error("Błąd! Link jest nieprawidłowy lub uszkodzony.")

else:
    # -------------------------------------------------------------
    # WIDOK DLA MECHANIKA (gdy otwierasz czystą aplikację)
    # -------------------------------------------------------------
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
            # Pakujemy dane do słownika
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
            
            st.success("🎉 Link wygenerowany!")
            
            # Instrukcja dla mechanika
            st.write("Kopiuj końcówkę linku i doklej ją do adresu swojej strony na telefonie:")
            st.code(f"?view={kod}")
            
            st.info("💡 Jak to będzie działać w sieci?\nJeśli Twoja apka będzie wisieć pod adresem `https://warsztat.streamlit.app`, to pełny link dla klienta to:\n"
                    f"`https://warsztat.streamlit.app/?view={kod}`")