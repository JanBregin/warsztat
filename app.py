import streamlit as st
import json
import base64
import urllib.parse

# Adres Twojej aplikacji wpisany na stałe:
MOJ_ADRES_APLIKACJI = "https://warsztat-status-naprawy-janek.streamlit.app/"
TELEFON_WARSZTATU = "48500600700"  # <-- Tutaj wpisz prawdziwy numer Janka

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
        
        # PASEK POSTĘPU NAPRAWY DLA KLIENTA
        st.subheader("⏳ Aktualny status prac")
        status_klienta = data.get('status', 'W kolejce')
        procenty = {"W kolejce": 10, "Diagnoza / Rozkręcanie": 35, "Naprawa w toku": 65, "Testy końcowe": 85, "Gotowe do odbioru! 🎉": 100}
        wartosc_procent = procenty.get(status_klienta, 10)
        st.progress(wartosc_procent / 100)
        
        if status_klienta == "Gotowe do odbioru! 🎉":
            st.success(f"🟢 **Status: {status_klienta}**")
        else:
            st.info(f"Etap: **{status_klienta}**")
        
        if data.get('odbior'):
            st.warning(f"🕒 **Planowany odbiór pojazdu:** {data.get('odbior')}")
            
        st.write("---")
        st.subheader("🔍 Stan techniczny podzespołów")
        
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
            
        # 💰 SEKCOJA: KOSZTORYS I ROZBICIE CZĘŚCI
        st.write("---")
        st.subheader("💰 Podsumowanie Kosztów")
        st.write("⚙️ **Wyszczególnienie użytych części:**")
        
        czesci_lista = data.get('czesci', [])
        suma_czesci = 0.0
        
        if czesci_lista:
            for czesc in czesci_lista:
                st.write(f"• {czesc['nazwa']}: **{float(czesc['cena']):,.2f} PLN**".replace(",", " "))
                suma_czesci += float(czesc['cena'])
        else:
            st.write("*Brak wyszczególnionych części (lub wliczone w usługę)*")
            
        st.write(" ")
        c_robocizna = float(data.get('koszt_robocizny', 0))
        suma_total = suma_czesci + c_robocizna
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Łącznie za części", value=f"{suma_czesci:,.2f} PLN".replace(",", " "))
        with col2:
            st.metric(label="Robocizna / Usługa", value=f"{c_robocizna:,.2f} PLN".replace(",", " "))
            
        st.subheader(f"Razem do zapłaty: {suma_total:,.2f} PLN".replace(",", " "))
        
        # Sekcja akceptacji - chowa się, gdy auto jest już naprawione i gotowe
        if status_klienta != "Gotowe do odbioru! 🎉":
            st.write("---")
            st.subheader("✍️ Akceptacja naprawy online")
            st.write("Jeśli zgadzasz się na zakres prac i kosztorys, potwierdź zamówienie poniżej.")
            
            chce_fakture = st.toggle("Chcę otrzymać fakturę VAT (na firmę)")
            
            faktura_dodatek_sms = ""
            if chce_fakture:
                firma_klient = st.text_input("Pełna nazwa firmy")
                nip_klient = st.text_input("Numer NIP")
                if firma_klient or nip_klient:
                    faktura_dodatek_sms = f"\n\n📄 DANE DO FAKTURY VAT:\n• Firma: {firma_klient}\n• NIP: {nip_klient}"
                else:
                    faktura_dodatek_sms = f"\n\n📄 [Klient poprosił o fakturę VAT, brak danych]"

            tekst_akceptacji = (
                f"Cześć! Akceptuję koszty i zakres naprawy mojego samochodu {data.get('auto')} ({data.get('nr_rej')}).\n"
                f"Kwota podsumowania: {suma_total:,.2f} PLN.{faktura_dodatek_sms}\n"
                f"Proszę o informację, kiedy auto będzie gotowe do odbioru! 👍"
            )
            tekst_akceptacji_url = urllib.parse.quote(tekst_akceptacji)
            link_do_mechanika = f"https://wa.me/{TELEFON_WARSZTATU}?text={tekst_akceptacji_url}"
            
            st.write(" ")
            st.link_button("✅ AKCEPTUJĘ NAPRAWĘ I KOSZTY", link_do_mechanika, type="primary")
        else:
            st.write("---")
            st.success("🚗 Samochód pomyślnie przeszedł wszystkie testy końcowe i oczekuje na odbiór w warsztacie!")
            
        st.caption("Dziękujemy za zaufanie!")
    else:
        st.error("Błąd! Link jest nieprawidłowy.")

else:
    # =============================================================
    # WIDOK DLA MECHANIKA (Panel Janka)
    # =============================================================
    st.title("🔧 Panel Mechanika")
    st.write("Wprowadź dane pojazdu, szczegóły naprawy oraz koszty.")
    
    with st.form("mechanic_form"):
        st.subheader("📝 Dane podstawowe")
        auto = st.text_input("Marka i model", placeholder="np. Audi A4 B8")
        nr_rej = st.text_input("Numer rejestracyjny", placeholder="np. WI 12345")
        telefon = st.text_input("Numer telefonu klienta", placeholder="np. 500600700")
        
        st.write("---")
        st.subheader("📊 Status i Czas")
        status = st.selectbox("Aktualny status naprawy", ["W kolejce", "Diagnoza / Rozkręcanie", "Naprawa w toku", "Testy końcowe", "Gotowe do odbioru! 🎉"])
        odbior = st.text_input("Planowany czas odbioru", placeholder="np. Dzisiaj o 16:30")
        
        st.write("---")
        st.subheader("🔍 Stan techniczny")
        hamulce = st.selectbox("Stan hamulców", ["Stan dobry (OK)", "Do wymiany wkrótce", "Wymiana PILNA!"])
        olej = st.selectbox("Olej i filtry", ["Stan dobry (OK)", "Do wymiany", "Wymieniono podczas wizyty"])
        zawieszenie = st.selectbox("Zawieszenie", ["Stan dobry (OK)", "Wykryto luzy", "Wymaga pilnej naprawy"])
        opony = st.selectbox("Stan opon",
