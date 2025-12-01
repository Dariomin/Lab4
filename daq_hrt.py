""" Faccio da capo il codice, in modo da capire meglio
    ogni singola stringa
"""
# === MODULI IMPORTATI === 
import time
import serial

t0 = time.time() # restituisce il tempo dal 1971 fino al momento in cui  viene eseguito il codice
sleep_time = 0.400 # in secondi, è il tempo di "stop" che posso inserire nel codice
acquisition_time = 20 # (s)
pattern = "AAAA0"

# ==== VARIABILI GLOBALI ====
discardEnable = True # da disattivare appena trovo i dati vanno bene

resto = ""
lista_dati = []

# === DEFINIZIONE DELL'OGGETTO DATO ===
    
class Dato:
    def __init__(self, hex_string, time):
        self.hex_string = hex_string
        self.time = time
        
        if len(hex_string) >= 12:
            self.hr = hex_string[4:8]
            self.temp = hex_string[8:12]
            
        else:
            self.hr = "DATO NON VALIDO"
            self.temp = "DATO NON VALIDO"
        
        
    def get_data(self):
         return f"Attributi dell'oggetto:\nDato: HR = {self.hr} , T  = {self.temp}"
     
    def get_time(self):
        return f"Tempo di Acquisizione = {self.time}"
        


# === FUNZIONE DI SCARTO PER I PRIMI DATI === 
def Discard(buffer, discardEnable):
    if discardEnable:
        print("Procedura per scartare i dati in corso...")
        position = buffer.find(pattern)
        
        # .find() restituisce -1 se non trova l'elemento
        
        if position != -1: # == se l'ha trovato
            print(f"Trovato patter {pattern} in {buffer} nella posizion {position}")
            print(f"Dati scartati {buffer[:position]}")
            
            # aggiorno il buffer per la prima volta
            
            buffer = buffer[position:]
            
            print(f"Buffer aggiornato: {buffer}")
            
            # una volta trovato il primo dato, disabilito il processo di scarto dei dati
            
            discardEnable = False
            return buffer, discardEnable
        else:
            return buffer, discardEnable
            
            
# def incatena_dati_incompleti(dato_incompleto, time_dato_incompleto):
#     # dopo 400 ms dalla prima acquisizione, arriva un altro dato.
#     # devo dunque imporre che questa funzione si abilita SOLO se sono passati 400 ms dalla prima acquisizione.

gm = time.gmtime()

""" gm restituisce:

    time.struct_time(tm_year=2025, tm_mon=11,
                    tm_mday=18, tm_hour=11,
                    tm_min=35, tm_sec=45, 
                    tm_wday=1, tm_yday=322, 
                    tm_isdst=0)
                    
    quindi un formato anno - mese - giorno - ora - min - sec - giorno della settimana - giorno dell'anno - bho """
              
              
# sono attributi, alla fine. Li esplicito      
ty = gm.tm_year
tmon = gm.tm_mon
tday = gm.tm_mday 
thour = gm.tm_hour + 1 # In Italy, with solar time, we have UTC+1, with legal time UTC+21
tmin = gm.tm_min
tsec = gm.tm_sec  

# Nome del file che si andrà a creare nel momento dell'acquisizione

file_name = f"Gruppo03_{ty}-{tmon}-{tday}T{thour}-{tmin}-{tsec}"

# === INIZIALIZZO LA SERIALE 

ser = serial.Serial(port="/dev/ttyUSB1", baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0)
# ser = serial.Serial(port="COM3", baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0)

ser.reset_input_buffer() # svuoto l'input della seriale, ossia il buffer (variabile temporanea)

if ser.isOpen():
	print("La porta è aperta correttamente")
else:
	ser.close()
	ser.open()
	print("la porta è stata chiusa e riaperta")
 
start = time.time()

















with open(file_name, "w") as file:
    while (time.time() - start < acquisition_time):
        print("ACQUISIZIONE DATI IN CORSO...")
        time.sleep(sleep_time)
        data_coming = ser.in_waiting 
        
        # numero di bytes presenti nel buffer
        
        print(f"Numero di bytes presenti nel buffer: {data_coming}")
        
        if data_coming > 0: # se sono presenti bytes di dati
            daq_time = time.time() # tempo di acquisizione per la prima stringa di dati
            data = ser.read(data_coming) 
            
            if data: # se la stringa non è vuota
                print(f"Dati in arrivo [{data}]")
                hex_string = ''.join(f"{b:02X}" for b in data) 
                
                # questo vuol dire ogni "b" == dato che leggi, convertilo in formato
                # f"{} == formato esadecimale 02X usando due cifre
                
                buffer = resto + hex_string
                
                            
                # - all'inizio resto è una stringa vuota.
                
                # - nel caso in cui ci sia da attribuire un resto, come ad esempio se len(str) < 12, che sia il
                #   dato singolo oppure l'ultima parte di un dato con len > 12, allora al buffer successivo verrà
                #   aggiunto un resto, ossia la parte rimanente del dato corrente.
                #   In tal caso "resto" verrà aggiornato col dato rimanente
                
                            
                print(f"Dati presenti nel buffer: {buffer}")
                
                # non è detto che vadano bene, quindi:
                    
                buffer_temp, discardEnable = Discard(buffer, discardEnable)
                
                if discardEnable and buffer_temp == buffer:
                    print("Nessun pattern trovato. Svuoto il buffer")
                    buffer = ""
                else:
                    buffer = buffer_temp
                    print(f"Dato rimanente rilevato: {buffer}")
                
                # primo set di dati che abbiamo, che sarà del tipo AAAA0YYYXXXXAAA0YY
                # oppure AAAA0YYYX
                
                
                
                # === INIZIO PROCEDURA PER TROVARE I PATTERN ALL'INTERNO DELLA STRINGA === 
                
                index = buffer.find(pattern)
                posizioni = []
                
                while index != -1:
                    posizioni.append(index)
                    index = buffer.find(pattern, index +1) 
                    
                    # mi restituirà una lista del tipo posizioni = [0, 12, 24]
                
                print(f"trovati {len(posizioni)} pattern")
            
                if posizioni: # mi assicura che la lista degli indici non sia vuota
                    
                    # === CASO IN CUI ABBIA STRINGA CON SOLO UN PATTERN ===
                    
                    if len(posizioni) == 1: 
                        
                        # non è detto che sia un dato intero e basta..
                        # può anche essere che è tipo AAAA06761987AAA
                        # qui trova solo un pattern, ma devo concatenare ciò che rimane
                        
                        idx1 = posizioni[0]
                        if len(buffer[idx1:]) >= 12:
                            if len(buffer[idx1 : idx1 + 12]) == 12:
                                oggetto =  Dato(buffer[idx1 : idx1 + 12], daq_time)       
                                lista_dati.append(oggetto)
                                print(f"Dato {oggetto} valido")
                                print(f"Dato unico trovato. Valori: HR = {oggetto.hr}, T = {oggetto.temp}, t = {oggetto.time}")
                                # ora lo trascrivo sul file testo
                                file.write(f"{oggetto.hr},{oggetto.temp},{oggetto.time}\n")
                                file.flush() # forzo il codice a scrivere sul file prima che la porta si chiuda
                        
                                buffer_residuo = buffer[(idx1 + 12):]
                                resto = buffer_residuo 
                                
                                print(f"Dato salvato {oggetto} salvato. Aggiunto in memoria la stringa {resto} da unire con quella successiva")
                                # l'idea è di conservarlo in memoria per dopo, per poi aspettare il dato successivo
                            else:
                                print("Errore da parte della seriale. La stringa è più lunga del previsto")
                                # non saprei come continuare però
                            
                        if len(buffer[idx1:]) < 12:
                            resto = buffer[idx1:]
                            print(f"Dato {buffer[idx1:]} incompleto. Aggiunto in memoria la stringa {resto} da unire con quella successiva")
                            
                            
                    if len(posizioni) > 1:
                        
                    # === CASO IN CUI ABBIA STRINGA CON PIU' PATTERN ===
                    # Tutto ciò che NON riguarda l'ultimo pattern, lo salvo nel file
                    # posizioni = [0, 12, 24]
                    # for pos in [0, 12]
                        j = 0
                        n = 1
                        count_data = 1
                        for pos in range(len(posizioni) -1):
                            singolo_dato = buffer[posizioni[pos] : posizioni[pos+1]] # per esempio, da 0 a 12, o da 12 a 24
                            if len(singolo_dato) == 12:
                                # check ulteriore nel caso in cui ci sia un bug nella seriale
                                singolo_dato_valido = Dato(singolo_dato, daq_time + sleep_time*(j/n))
                                print(f"Dato {singolo_dato_valido} valido")
                                print(f"Dato {count_data}: HR = {singolo_dato_valido.hr}, T = {singolo_dato_valido.temp}, t = {singolo_dato_valido.time}")
                                file.write(f"{count_data},{singolo_dato_valido.hr},{singolo_dato_valido.temp},{singolo_dato_valido.time}\n")
                                file.flush() # forzo il codice a scrivere sul file prima che la porta si chiuda
                                j += 1
                                n += 1
                                count_data += 1
                            else:
                                print("Dato non valido. Errore da parte della seriale")
                            
                    # === MI OCCUPO DELL'ULTIMO DATO, EVENTUALMENTE DA RICOSTRUIRE ===
                        last_buffer = buffer[posizioni[-1]:]
                        len_last_buffer = len(last_buffer)
                    
                        if len_last_buffer == 12:
                            object =  Dato(last_buffer, daq_time)       
                            lista_dati.append(object)
                            print(f"Dato {object} valido")
                            print(f"Dato univo trovato. Valori: HR = {object.hr}, T = {object.temp}, t = {object.time}")
                            file.write(f"{object.hr},{object.temp},{object.time}\n")
                            file.flush() # forzo il codice a scrivere sul file prima che la porta si chiuda
                            
                        if len_last_buffer < 12:
                            print(f"dato rimanente {last_buffer}. In attesa del dato successivo per incatenamento...")
                            resto = last_buffer
                        
                        else:
                            print("Resto da concatenare non valido. Errore da parte della seriale.\nEseguo reset del resto")
                            resto = ""            
ser.close()
               
                            
                            
                            
                            
                        # ora aggiorno il buffer dalla posizione che ho trovato in poi
                        # quindi inizierà con AAAA0    
                        
    # # === PARTE RESIDUA DI DATI PRESENTE NEL BUFFER ===
                        
    #                     buffer = buffer[posizioni[-1]:] 
                        
    #                     print(f"lista dei dati ottenuti: {lista_dati}")    
    #                     print(f"pacchetto di dato incompleto: {buffer}")
                        
    #                     if len(buffer) >= 12:
    #                         print(f"Dato rimanente  accettabile.")
                            
    #                         if len(buffer) - index >= 12:
    #                             print("Possibile pacchetto dati nel buffer")
    #                             data_save = buffer[index : index + 12]
    #                             oggetto_new = Dato(data_save, daq_time)
    #                             lista_dati.append(oggetto_new)
    #                             file.write(f"{lista_dati[i].dato},{lista_dati[i].time}" for i in lista_dati)
    #                             file.flush()
    #                             buffer = buffer[index + 12 :]                        
                            
    #                     else:
    #                             print(f"Dati nel buffer non accettabili")
    #                             file.flush() # forza il programma a scrivere sul file PRIMA della chiusura della seriale
                            
          
        
            
        
        