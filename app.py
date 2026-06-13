import streamlit as st
import json
import base64
import urllib.parse

# 🔴 CONFIG: Dane Twojego warsztatu (wpisane na stałe)
MOJ_ADRES_APLIKACJI = "https://warsztat-status-naprawy-janek.streamlit.app/"
TELEFON_WARSZTATU = "48502826967"  # <-- Tutaj wpisz prawdziwy numer Janka, gdy będziecie gotowi

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
    # =============================================================
    # WIDOK DLA KLIENTA (Otwiera klient po kliknięciu w link)
    # =============================================================
    encoded_str = query_params["view"]
    data = decode_data(encoded_str)
    
    if data:
        st.title("📋 Raport Stanu Pojazdu")
        st.subheader(f"🚗 {data.get('auto', 'Samochód')}")
        st.caption(f"Numer rejestracyjny: {data.get('nr_rej', 'Brak')}")
        st.write("---")
        
        # 🟢 NOWOŚĆ: PASEK POSTĘPU NAPRAWY DLA KLIENTA
        st.subheader("⏳ Aktualny status prac")
        status_klienta = data.get('status', 'W kolejce')
        
        # Logika graficznego paska postępu
        procenty = {"W kolejce": 10, "Diagnoza / Rozkręcanie": 35, "Naprawa w toku": 65, "Testy końcowe": 85, "Gotowe do odbioru! 🎉": 100}
        wartosc_procent = procenty.get(status_klienta, 10)
        
        st.progress(wartosc_procent / 100)
        st.info(f"Etap: **{status_klienta}**")
        
        # 🟢 NOWOŚĆ: PLANOWANY ODBIÓR DLA KLIENTA
        if data.get('odbior'):
            st.warning(f"🕒 **Planowany odbiór pojazdu:** {data.get('odbior')}")
            
        st.write("---")
        st.subheader("🔍 Stan techniczny podzespołów")
        
        # Statusy z kolorami
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
            
        # 💰 SEKCOJA: KOSZTORYS DLA KLIENTA
        st.write("---")
        st.subheader("💰 Podsumowanie Kosztów")
        
        c_czesci = float(data.get('koszt_czesci', 0))
        c_robocizna = float(data.get('koszt_robocizny', 0))
        suma = c_czesci + c_robocizna
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Części", value=f"{c_czesci:,.2f} PLN".replace(",", " "))
        with col2:
            st.metric(label="Robocizna", value=f"{c_robocizna:,.2f} PLN".replace(",", " "))
            
        st.subheader(f"Razem do zapłaty: {suma:,.2f} PLN".replace(",", " "))
        
        # AKCEPTACJA NAPRAWY ONLINE PRZEZ KLIENTA
        st.write("---")
        st.subheader("✍️ Akceptacja naprawy online")
        st.write("Jeśli zgadzasz się na powyższy kosztorys i zakres prac, kliknij przycisk poniżej. "
                 "Wyśle to automatyczne potwierdzenie do warsztatu.")
        
        tekst_akceptacji = (
            f"Cześć! Akceptuję koszty i zakres naprawy mojego samochodu {data.get('auto')} ({data.get('nr_rej')}).\n"
            f"Kwota podsumowania: {suma:,.2f} PLN.\n"
            f"Proszę o informację, kiedy auto będzie gotowe do odbioru! 👍"
        )
        tekst_akceptacji_url = urllib.parse.quote(tekst_akceptacji)
        link_do_mechanika = f"https://wa.me/{TELEFON_WARSZTATU}?text={tekst_akceptacji_url}"
        
        st.link_button("✅ AKCEPTUJĘ NAPRAWĘ I KOSZTY", link_do_mechanika, type="primary")
        
        st.write("---")
        st.caption("Dziękujemy za zaufanie! W razie pytań prosimy o kontakt z warsztatem.")
    else:
        st.error("Błąd! Link jest nieprawidłowy.")

else:
    # =============================================================
    # WIDOK DLA MECHANIKA (Widzi tylko Janek)
    # =============================================================
    st.title("🔧 Panel Mechanika")
    st.write("Wprowadź dane pojazdu, status oraz wycenę, aby wygenerować link.")
    
    with st.form("mechanic_form"):
        st.subheader("📝 Dane pojazdu i klienta")
        auto = st.text_input("Marka i model", placeholder="np. Audi A4 B8")
        nr_rej = st.text_input("Numer rejestracyjny", placeholder="np. WI 12345")
        telefon = st.text_input("Numer telefonu klienta (np. 500600700)", placeholder="Bez kierunkowego +48")
        
        st.write("---")
        # 🟢 NOWOŚĆ: SEKCOJA STATUSU I CZASU ODBIORU DLA JANKA
        st.subheader("📊 Status i Czas")
        status = st.selectbox("Aktualny status naprawy", ["W kolejce", "Diagnoza / Rozkręcanie", "Naprawa w toku", "Testy końcowe", "Gotowe do odbioru! 🎉"])
        odbior = st.text_input("Planowany czas odbioru", placeholder="np. Dzisiaj o 16:30 / Jutro do południa")
        
        st.write("---")
        st.subheader("🔍 Stan techniczny")
        hamulce = st.selectbox("Stan hamulców", ["Stan dobry (OK)", "Do wymiany wkrótce", "Wymiana PILNA!"])
        olej = st.selectbox("Olej i filtry", ["Stan dobry (OK)", "Do wymiany", "Wymieniono podczas wizyty"])
        zawieszenie = st.selectbox("Zawieszenie", ["Stan dobry (OK)", "Wykryto luzy (do naprawy)", "Wymaga pilnej naprawy"])
        opony = st.selectbox("Stan opon", ["Stan dobry (OK)", "Bieżnik na wykończeniu", "Zalecana wymiana"])
        
        uwagi = st.text_area("Dodatkowe uwagi / co zostało zrobione")
        
        st.write("---")
        st.subheader("💵 Kosztorys (PLN)")
        koszt_czesci = st.number_input("Koszt części", min_value=0.0, step=50.0, value=0.0)
        koszt_robocizny = st.number_input("Koszt robocizny", min_value=0.0, step=50.0, value=0.0)
        
        skonfiguruj = st.form_submit_button("Generuj Link i Gotową Wiadomość")
        
        if skonfiguruj:
            paczka_danych = {
                "auto": auto,
                "nr_rej": nr_rej,
                "status": status,
                "odbior": odbior,
                "hamulce": hamulce,
                "olej": olej,
                "zawieszenie": zawieszenie,
                "opony": opony,
                "uwagi": uwagi,
                "koszt_czesci": koszt_czesci,
                "koszt_robocizny": koszt_robocizny
            }
            
            kod = encode_data(paczka_danych)
            czysty_url = MOJ_ADRES_APLIKACJI.strip("/")
            pelny_link = f"{czysty_url}/?view={kod}"
            
            st.success("🎉 Wszystko przygotowane!")
            
            # Dostosowanie wiadomości na WhatsApp z uwzględnieniem statusu
            dodatek_status = f" Aktualny status: {status}."
            if odbior:
                dodatek_status += f" Planowany odbiór: {odbior}."
                
            tekst_wiadomosci = (
                f"Cześć! Twój samochód {auto} ({nr_rej}) został przyjęty do serwisu.{dodatek_status} "
                f"Cyfrowy raport stanu pojazdu oraz podsumowanie kosztów znajdziesz tutaj: {pelny_link}"
            )
            tekst_url = urllib.parse.quote(tekst_wiadomosci)
            
            czysty_telefon = "".join(filter(str.isdigit, telefon))
            if len(czysty_telefon) == 9:
                czysty_telefon = "48" + czysty_telefon
                
            if czysty_telefon:
                wa_url = f"https://wa.me/{czysty_telefon}?text={tekst_url}"
            else:
                wa_url = f"https://api.whatsapp.com/send?text={tekst_url}"
            
            st.link_button("📱 Wyślij raport przez WhatsApp", wa_url, type="primary")
            st.write("Alternatywnie możesz skopiować sam link ręcznie:")
            st.code(pelny_link)
