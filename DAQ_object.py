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


buffer = ""

""" arriveranno dati del tipo AAAA05731971AAAA05891899...
    il punto è che l'acquisizione può anche dare un valore
    iniziale come AA057319, che non va bene.
    
    Distinguiamo alcuni casi:
    
    Può capitare, per esempio, di trovare:
    - 971AAAA058918 - 
    in questo caso, appena trova il patterr all'indice 2,
    deve:
        1) scartare 971
        2) lasciare AAAA058918
    attenzione però, sono 10 caratteri, a noi ne servono 12!
    
    quindi, va messa anche una condizione sul numero di byte 
    che arrivano (ogni carattere sono 4 bit == 1 byte)
    
    """
    
    
# === DEFINIZIONE DELL'OGGETTO DATO ===

# gli attributi saranno:
    # 1) dato in termini di bytes 
    # 2) il tempo associato al dato 
    # 3) il numero di iterazioni per formare il dato L'HO TOLTO MA POTREI AVER SBAGLIATO, VEDERE A RICEVIMENTO
    
class Dato:
    def __init__(self, dato, time):
        self.dato = dato 
        self.time = time
        
    def get_attribute(self):
         return f"Attributi dell'oggetto:\nDato = {self.dato}\nTempo di Acquisizione = {self.time}"
        
lista_dati = []

# === FUNZIONE DI SCARTO PER I PRIMI DATI === 
def Discard(buffer, discardEnable):
    if discardEnable:
        print("Procedura per scartare i dati in corso...")
        position = buffer.find(pattern)
        
        # .find() restituisce -1 se non trova l'elemento
        
        if position != -1: # == se l'ha trovato
            print(f"Trovato patter {pattern} in {buffer} nella posizione {position}")
            print(f"Dati scartati {buffer[:position]}")
            
            # aggiorno il buffer per la prima volta
            
            buffer = buffer[position:]
            
            print(f"Buffer aggiornato: {buffer}")
            
            # una volta trovato il primo dato, disabilito il processo di scarto dei dati
            
            discardEnable = False
            return buffer, discardEnable
        else:
            print(f"Sequenza {pattern} non trovata")
        
        
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

# inizializzo la seriale 

ser = serial.Serial(port="/dev/ttyUSB1", baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0)

ser.reset_input_buffer() # svuoto l'input della seriale, ossia il buffer (variabile temporanea)

if ser.isOpen():
	print("La porta è aperta correttamente")
else:
	ser.close()
	ser.open()
	print("la porta è stata chiusa e riaperta")
 
start = time.time() 

# start serve per l'acquisizione, mentre t0 serve a noi per fissare il tempo di una presa dati

# apro il file su cui scriverà il programma

with open(file_name, "w") as file:
    while (acquisition_time > start):
        print("ACQUISIZIONE DATI IN CORSO...")
        time.sleep(sleep_time) #prendi dati ogni 400 ms
        data_coming = ser.in_waiting 
        
        # numero di bytes presenti nel buffer
        
        print(f"Numero di bytes presenti nel buffer: {data_coming}")
        
        if data_coming: # se sono presenti bytes di dati
            daq_time = time.time() 
            data = ser.read(data_coming) 
            
            # daq_time è il tempo in cui i dati sono stati letti 
            # ogni volta che richiamo time.time() sto richiamando
            # il tempo in cui quella riga di codice è stata eseguita
            
            if data:
                print(f"Dati in arrivo [{data}]")
                empty_string = ''
                hex_string = empty_string.join(f"{b:02X}" for b in data) 
                
                # questo vuol dire ogni "b" == dato che leggi, convertilo in formato
                # f"{} == formato esadecimale 02X usando due cifre
                
                buffer += hex_string
                
                print(f"Dati presenti nel buffer: {buffer}")
                
                # non è detto che vadano bene, quindi:
                
                buffer_temp, discardEnable = Discard(buffer, discardEnable)
                
                buffer = buffer_temp # primo set di dati che abbiamo -> NON E' DETTO CHE VADA BENE
                
                print(f"Dato rimanente rilevato: {buffer}")
                
                index = buffer.find(pattern)
                posizioni = []
                
                # in questo caso, index dovrebbe essere 0, poiché ora 
                # buffer è la il dato "nuovo" dopo lo scarto
                
                while index != -1:
                    posizioni.append(index)
                    index = buffer.find(pattern, index +1) 
                    
                    # gli sto chiedendo di trovare altri pattern dopo quelli che ha già trovato
                    
                print(f"trovati {len(posizioni)} pattern")
            
                if posizioni:
                    for i in range(len(posizioni)-1):
                        singolo_dato = buffer[posizioni[i]:posizioni[i+1]]
                        oggetto = Dato(singolo_dato, daq_time)
                        lista_dati.append(oggetto)
                        
                    if len(posizioni) == 1:
                        oggetto =  Dato(buffer[posizioni[0]:], daq_time)
                        lista_dati.append(oggetto)
                        
                    # ora aggiorno il buffer dalla posizione che ho trovato in poi
                    # quindi inizierà con AAAA0    
                    
                    buffer = buffer[posizioni[-1]:] 
                    
                    print(f"lista dei dati ottenuti: {lista_dati}")    
                    print(f"pacchetto di dato incompleto: {buffer}")
                    
                    if len(buffer) >= 12:
                        print(f"Dato rimanente  accettabile")
                        
                        if len(buffer) - index >= 12:
                            print("Possibile pacchetto dati nel buffer")
                            data_save = buffer[index : index + 12]
                            oggetto_new = Dato(data_save, daq_time)
                            lista_dati.append(oggetto_new)
                            file.write(f"{lista_dati[i].dato},{lista_dati[i].time}" for i in lista_dati)
                            
                        
                        
                        
                    
                    
                    
                    
                    if len(buffer) >=12:
                        print("Pacchetto dati accettabile")
                        
                        
                        
                                
                
                # === CREAZIONI DEGLI ATTRIBUTI ===
                
                
                                    
                
                
                
                
                
                

            
            
        
            
        
        
        
        
        


 
 
