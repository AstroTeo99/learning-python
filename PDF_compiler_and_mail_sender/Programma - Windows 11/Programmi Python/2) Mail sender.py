import yagmail
import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FATTURE_DIR = os.path.join(BASE_DIR, "Fatture")

def normalizza_stringa(stringa):
    return ' '.join(stringa.split())

def formatta_nome(nome):
    return ' '.join(parola.capitalize() for parola in nome.split())

def invia_email(destinatario, oggetto, corpo_html, allegato_path):
    try:
        gmail_password = os.getenv("GMAIL_PASSWORD") #GMAIL_PASSWORD sarebbe la variabile d'ambiente impostata sul proprio computer come password del proprio account Gmail con il quale si vuole inviare la mail (questo è stato fatto per rendere più sicuro il processo).
        
        if not gmail_password:
            print("Errore: la variabile d'ambiente GMAIL_PASSWORD non è impostata correttamente.")
            return
        
        yag = yagmail.SMTP("email@gmail.com", gmail_password) #Inserire la propria email.
        
        yag.send(
            to=destinatario,
            subject=oggetto,
            contents=corpo_html,
            attachments=allegato_path
        )
        print(f"Email inviata con successo a {destinatario}")
    except Exception as e:
        print(f"Errore nell'invio dell'email: {e}")

def invia_fatture_intervallo():
    excel_path = os.path.join(BASE_DIR, 'dati_fattura.xlsm')
    df = pd.read_excel(excel_path, skiprows=2)

    try:
        numero_iniziale = int(input("Da quale numero di fattura vuoi inviare la mail? "))
        numero_finale = int(input("Fino a quale numero di fattura vuoi che invii le mail? "))
    except ValueError:
        print("Errore: inserisci solo numeri interi.")
        return

    riga_iniziale = df[df.iloc[:, 8] == numero_iniziale].index
    riga_finale = df[df.iloc[:, 8] == numero_finale].index

    if not riga_iniziale.empty and not riga_finale.empty:
        nome_inizio = formatta_nome(normalizza_stringa(df.iloc[riga_iniziale[0], 0]))
        path_inizio = os.path.join(FATTURE_DIR, f"Fatt. n. {numero_iniziale} - {nome_inizio}.pdf")
        
        nome_fine = formatta_nome(normalizza_stringa(df.iloc[riga_finale[0], 0]))
        path_fine = os.path.join(FATTURE_DIR, f"Fatt. n. {numero_finale} - {nome_fine}.pdf")

        print(f"Confermi l'invio delle mail dalla numero {numero_iniziale} - {nome_inizio}, con allegato \"{path_inizio}\" - "
              f"alla numero {numero_finale} - {nome_fine}, con allegato \"{path_fine}\"?")
        
        conferma = input("Confermi? (Y/N): ").strip().upper()
        
        if conferma == 'Y':
            for idx in df.index:
                numero_fattura = df.iloc[idx, 8]
                if numero_iniziale <= numero_fattura <= numero_finale:
                    nome_cognome_excel = normalizza_stringa(df.iloc[idx, 0])
                    nome_cognome_formattato = formatta_nome(nome_cognome_excel)
                    email_cliente = df.iloc[idx, 9]
                    nome_file_pdf = os.path.join(FATTURE_DIR, f"Fatt. n. {numero_fattura} - {nome_cognome_excel}.pdf")
                    
                    if os.path.exists(nome_file_pdf):
                        corpo_html = f"""<!DOCTYPE html><html lang="it"><head><meta charset="UTF-8"><title>Anteprima Email</title></head><body style="margin:0;padding:0;font-family:Arial,sans-serif;font-size:12pt;color:#333;line-height:1.2;">Gentile {nome_cognome_formattato},<br><br>in allegato la sua fattura.<br>Cordiali saluti,<br><br>Il team XXX.<br><br>---<br><br><p style="font-size:10px;color:#666;line-height:1.5;margin:0;padding:0;">Le informazioni, i dati e le notizie contenute nella presente comunicazione e i relativi allegati sono di natura privata e come tali possono essere riservate e sono, comunque, destinate esclusivamente ai destinatari indicati in epigrafe.<br>La diffusione, distribuzione e/o la copiatura del documento trasmesso da parte di qualsiasi soggetto diverso dal destinatario è proibita, sia ai sensi dell’art. 616 c.p., sia ai sensi del Regolamento (UE) 2016/679 e del Decreto legislativo 10 agosto 2018, n. 101. Se avete ricevuto questo messaggio per errore, vi preghiamo di distruggerlo e di darcene immediata comunicazione anche inviando un messaggio di ritorno all’indirizzo e-mail del mittente.<br><br><em>Pensa all'ambiente, stampa questa mail solo se necessario.<br><br><br></em></p></body></html>"""

                        invia_email(
                            destinatario=email_cliente,
                            oggetto="Fattura",
                            corpo_html=corpo_html,
                            allegato_path=nome_file_pdf
                        )
                    else:
                        print(f"Il file PDF {nome_file_pdf} non esiste. Email non inviata per la fattura n. {numero_fattura}.")
            print("Invio completato.")
        else:
            print("Invio annullato.")
    else:
        print("Errore: intervallo di fatture non valido. Controlla i numeri inseriti e riprova.")

if __name__ == "__main__":
    invia_fatture_intervallo()
