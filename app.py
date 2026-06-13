import streamlit as st
import json
import base64
import urllib.parse
import os
import requests
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time

# Adres Twojej aplikacji wpisany na stałe:
MOJ_ADRES_APLIKACJI = "https://warsztat-status-naprawy-janek.streamlit.app/"
TELEFON_WARSZTATU = "48500600700"  # <-- Tutaj wpisz prawdziwy numer Janka

st.set_page_config(page_title="Warsztat - Status Naprawy", page_icon="🔧", layout="centered")

# Funkcja pobierająca polskie czcionki do PDF z oficjalnego repozytorium Google
@st.cache_data
def pobierz_czcionki():
    pulpit_regular = "Roboto-Regular-v2.ttf"
    pulpit_bold = "Roboto-Bold-v2.ttf"
    if not os.path.exists(pulpit_regular):
        r = requests.get("https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf")
        if r.status_code == 200: 
            with open(pulpit_regular, "wb") as f: f.write(r.content)
    if not os.path.exists(pulpit_bold):
        r = requests.get("https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Bold.ttf")
        if r.status_code == 200: 
            with open(pulpit_bold, "wb") as f: f.write(r.content)
    return pulpit_regular, pulpit_bold

# Funkcja generująca plik PDF
def generuj_pdf(data, suma_total, suma_czesci, c_robocizna):
    reg, bld = pobierz_czcionki()
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Roboto", "", reg)
    pdf.add_font("Roboto", "B", bld)
    
    pdf.set_font("Roboto", "B", 20)
    pdf.cell(0, 12, "RAPORT STANU POJAZDU", align="C")
    pdf.ln(12)
    pdf.set_font("Roboto", "", 10)
    pdf.cell(0, 6, "Cyfrowy Certyfikat Serwisowy", align="C")
    pdf.ln(12)
    
    pdf.set_font("Roboto", "B", 14)
    pdf.cell(0, 8, f"🚗 Pojazd: {data.get('auto', 'Nie podano')}")
    pdf.ln(8)
    pdf.set_font("Roboto", "", 11)
    pdf.cell(0, 6, f"Numer rejestracyjny: {data.get('nr_rej', 'Nie podano')}")
    pdf.ln(6)
    pdf.cell(0, 6, f"Status naprawy: {data.get('status', 'W kolejce')}")
    pdf.ln(6)
    if data.get('odbior'):
        pdf.cell(0, 6, f"Planowany odbiór: {data.get('odbior')}")
        pdf.ln(6)
    if data.get('nastepny_olej'):
        pdf.cell(0, 6, f"Następny olej przy: {data.get('nastepny_olej'):,} km".replace(",", " "))
        pdf.ln(6)
    pdf.ln(4)
    
    pdf.set_font("Roboto", "B", 14)
    pdf.cell(0, 8, "🔍 Wyniki weryfikacji technicznej:")
    pdf.ln(8)
    pdf.set_font("Roboto", "", 11)
    pdf.cell(0, 6, f"• Hamulce: {data.get('hamulce', 'Brak danych')}")
    pdf.ln(6)
    pdf.cell(0, 6, f"• Olej silnikowy: {data.get('olej', 'Brak danych')}")
    pdf.ln(6)
    pdf.cell(0, 6, f"• Zawieszenie: {data.get('zawieszenie', 'Brak danych')}")
    pdf.ln(6)
    pdf.cell(0, 6, f"• Opony: {data.get('opony', 'Brak danych')}")
    pdf.ln(8)
    
    if data.get('uwagi'):
        pdf.set_font("Roboto", "B", 12)
        pdf.cell(0, 6, "💬 Uwagi i zalecenia mechanika:")
        pdf.ln(6)
        pdf.set_font("Roboto", "", 11)
        pdf.multi_cell(0, 6, data.get('uwagi'))
        pdf.ln(6)
        
    pdf.set_font("Roboto", "B", 14)
    pdf.cell(0, 8, "💰 Szczegółowy kosztorys:")
    pdf.ln(8)
    pdf.set_font("Roboto", "", 11)
    
    czesci_lista = data.get('czesci', [])
    if czesci_lista:
        for czesc in czesci_lista:
            pdf.cell(0, 6, f"  - {czesc['nazwa']}: {float(czesc['cena']):,.2f} PLN")
            pdf.ln(6)
    
    pdf.ln(4)
    pdf.cell(0, 6, f"Suma za części: {suma_czesci:,.2f} PLN")
    pdf.ln(6)
    pdf.cell(0, 6, f"Koszt robocizny / usługi: {c_robocizna:,.2f} PLN")
    pdf.ln(8)
    pdf.set_font("Roboto", "B", 13)
    pdf.cell(0, 10, f"RAZEM DO ZAPŁATY: {suma_total:,.2f} PLN")
    pdf.ln(10)
    
    return pdf.output()

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
    # WIDOK DLA KLIENTA
    # =============================================================
    encoded_str = query_params["view"]
    data = decode_data(encoded_str)
    
    if data:
        st.title("📋 Raport Stanu Pojazdu")
        st.subheader(f"🚗 {data.get('auto', 'Samochód')}")
        st.caption(f"Numer rejestracyjny: {data.get('nr_rej', 'Brak')}")
        st.write("---")
        
        # PASEK POSTĘPU
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
            
        if data.get('nastepny_olej'):
            st.metric(label="🛢️ Następna wymiana oleju przy przebiegu", value=f"{data.get('nastepny_olej'):,} km".replace(",", " "))
            
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
            
        # KOSZTORYS
        st.write("---")
        st.subheader("💰 Podsumowanie Kosztów")
        
        czesci_lista = data.get('czesci', [])
        suma_czesci = 0.0
        if czesci_lista:
            for czesc in czesci_lista:
                st.write(f"• {czesc['nazwa']}: **{float(czesc['cena']):,.2f} PLN**".replace(",", " "))
                suma_czesci += float(czesc['cena'])
        
        c_robocizna = float(data.get('koszt_robocizny', 0))
        suma_total = suma_czesci + c_robocizna
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Łącznie za części", value=f"{suma_czesci:,.2f} PLN".replace(",", " "))
        with col2:
            st.metric(label="Robocizna / Usługa", value=f"{c_robocizna:,.2f} PLN".replace(",", " "))
            
        st.subheader(f"Razem do zapłaty: {suma_total:,.2f} PLN".replace(",", " "))
        
        # PDF
        st.write("---")
        try:
            pdf_data = generuj_pdf(data, suma_total, suma_czesci, c_robocizna)
            st.download_button(label="📥 Pobierz oficjalny raport PDF", data=bytes(pdf_data), file_name=f"Raport_{data.get('nr_rej', 'serwis')}.pdf", mime="application/pdf", use_container_width=True)
        except Exception as e:
            st.error(f"Nie udało się wygenerować pliku PDF: {e}")
        
        # Akceptacja
        if status_klienta != "Gotowe do odbioru! 🎉":
            st.write("---")
            st.subheader("✍️ Akceptacja naprawy online")
            chce_fakture = st.toggle("Chcę otrzymać fakturę VAT (na firmę)")
            faktura_dodatek_sms = ""
            if chce_fakture:
                firma_klient = st.text_input("Pełna nazwa firmy")
                nip_klient = st.text_input("Numer NIP")
                if firma_klient or nip_klient:
                    faktura_dodatek_sms = f"\n\n📄 DANE DO FAKTURY VAT:\n• Firma: {firma_klient}\n• NIP: {nip_klient}"

            tekst_akceptacji = (
                f"Cześć! Akceptuję koszty i zakres naprawy mojego samochodu {data.get('auto')} ({data.get('nr_rej')}).\n"
                f"Kwota podsumowania: {suma_total:,.2f} PLN.{faktura_dodatek_sms}\n"
                f"Proszę o informację, kiedy auto będzie gotowe do odbioru! 👍"
            )
            tekst_akceptacji_url = urllib.parse.quote(tekst_akceptacji)
            link_do_mechanika = f"https://wa.me/{TELEFON_WARSZTATU}?text={tekst_akceptacji_url}"
            st.link_button("✅ AKCEPTUJĘ NAPRAWĘ I KOSZTY", link_do_mechanika, type="primary", use_container_width=True)
            
        st.caption("Dziękujemy za zaufanie!")
else:
    # =============================================================
    # WIDOK DLA MECHANIKA
    # =============================================================
    st.title("🔧 Panel Mechanika")
    
    with st.form("mechanic_form"):
        st.subheader("📝 Dane podstawowe")
        auto = st.text_input("Marka i model", placeholder="np. Audi A4 B8")
        nr_rej = st.text_input("Numer rejestracyjny", placeholder="np. WI 12345")
        telefon = st.text_input("Numer telefonu klienta", placeholder="np. 500600700")
        
        st.write("---")
        st.subheader("📊 Status i Czas")
        status = st.selectbox("Aktualny status naprawy", ["W kolejce", "Diagnoza / Rozkręcanie", "Naprawa w toku", "Testy końcowe", "Gotowe do odbioru! 🎉"])
        col_data, col_godzina = st.columns(2)
        with col_data: wybrana_data = st.date_input("Planowana data odbioru", value=datetime.now())
        with col_godzina: wybrana_godzina = st.time_input("Planowana godzina", value=time(16, 0))
        
        st.write("---")
        st.subheader("🛢️ Serwis olejowy")
        col_przebieg, col_interwal = st.columns(2)
        with col_przebieg:
            przebieg = st.number_input("Aktualny przebieg auta (km)", min_value=0, value=150000, step=1000)
        with col_interwal:
            interwal = st.selectbox("Interwał kolejnej wymiany", [10000, 12000, 15000], index=2)
        
        st.write("---")
        st.subheader("🔍 Stan techniczny")
        hamulce = st.selectbox("Stan hamulców", ["Stan dobry (OK)", "Do wymiany wkrótce", "Wymiana PILNA!"])
        olej = st.selectbox("Olej i filtry", ["Stan dobry (OK)", "Do wymiany", "Wymieniono podczas wizyty"])
        zawieszenie = st.selectbox("Zawieszenie", ["Stan dobry (OK)", "Wykryto luzy", "Wymaga pilnej naprawy"])
        opony = st.selectbox("Stan opon", ["Stan dobry (OK)", "Bieżnik na wykończeniu", "Zalecana wymiana"])
        uwagi = st.text_area("Dodatkowe uwagi / co zostało zrobione")
        
        st.write("---")
        st.subheader("⚙️ Wykaz i koszt użytych części")
        init_df = pd.DataFrame([{"Nazwa części": "", "Cena (PLN)": 0.0}])
        tabela_czesci = st.data_editor(init_df, num_rows="dynamic", use_container_width=True)
                
        st.write(" ")
        koszt_robocizny = st.number_input("Koszt robocizny / usługi", min_value=0.0, step=50.0, value=0.0)
        
        skonfiguruj = st.form_submit_button("Generuj Link i Zapisz w Bazie")
        
        if skonfiguruj:
            odbior_tekst = f"{wybrana_data.strftime('%d.%m.%Y')} o godz. {wybrana_godzina.strftime('%H:%M')}"
            nastepny_olej_calc = przebieg + interwal
            
            czesci_dane = []
            for _, row in tabela_czesci.iterrows():
                nazwa_raw = str(row["Nazwa części"]).strip()
                if nazwa_raw:
                    czesci_dane.append({"nazwa": nazwa_raw, "cena": float(row["Cena (PLN)"])})
            
            paczka_danych = {
                "auto": auto, "nr_rej": nr_rej, "status": status, "odbior": odbior_tekst,
                "nastepny_olej": nastepny_olej_calc, "hamulce": hamulce, "olej": olej,
                "zawieszenie": zawieszenie, "opony": opony, "uwagi": uwagi, "czesci": czesci_dane,
                "koszt_robocizny": koszt_robocizny
            }
            
            kod = encode_data(paczka_danych)
            pelny_link = f"{MOJ_ADRES_APLIKACJI.strip(' /')}/?view={kod}"
            
            suma_czesci_calc = sum(float(c['cena']) for c in czesci_dane)
            suma_total_calc = suma_czesci_calc + float(koszt_robocizny)
            
            # 🟢 AUTOMATYCZNY ZAPIS DO BAZY GOOGLE SHEETS (POPRAWIONY IMPORT)
            try:
                from streamlit_gsheets import GSheetsConnection
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                nowy_wiersz = {
                    "Data zapisu": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "Pojazd": auto, "Rejestracja": nr_rej, "Telefon": telefon, "Status": status,
                    "Aktualny przebieg": przebieg, "Nastepny olej przy": nastepny_olej_calc,
                    "Koszt razem (PLN)": suma_total_calc, "Link do raportu": pelny_link
                }
                
                try:
                    existing_df = conn.read(worksheet="Sheet1", ttl=0)
                    updated_df = pd.concat([existing_df, pd.DataFrame([nowy_wiersz])], ignore_index=True)
                except:
                    updated_df = pd.DataFrame([nowy_wiersz])
                
                conn.update(worksheet="Sheet1", data=updated_df)
                st.toast("🗄️ Dane pomyślnie zapisane w bazie Google Sheets!")
            except Exception as e:
                st.sidebar.warning(f"Baza danych niedostępna (wymaga konfiguracji Secrets): {e}")
            
            st.success("🎉 Link wygenerowany pomyślnie!")
            
            if status == "Gotowe do odbioru! 🎉":
                tekst_wiadomosci = f"🎯 Dobre wieści! Twój samochód {auto} ({nr_rej}) jest już GOTOWY DO ODBIORU! 🎉\n\n💰 Koszt: {suma_total_calc:,.2f} PLN.\n📋 Raport: {pelny_link}"
            else:
                tekst_wiadomosci = f"Cześć! Twój samochód {auto} ({nr_rej}) został sprawdzony. Status: {status}. Link do akceptacji kosztów: {pelny_link}"
                
            tekst_url = urllib.parse.quote(tekst_wiadomosci)
            czysty_telefon = "".join(filter(str.isdigit, telefon))
            if len(czysty_telefon) == 9: czysty_telefon = "48" + czysty_telefon
            wa_url = f"https://wa.me/{czysty_telefon}?text={tekst_url}" if czysty_telefon else f"https://api.whatsapp.com/send?text={tekst_url}"
            
            st.link_button("📱 Wyślij raport przez WhatsApp", wa_url, type="primary")
            st.code(pelny_link)
