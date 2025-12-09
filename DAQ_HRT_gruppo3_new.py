"""
Read sensor sht75 
@author: M.D.P.

"""
# === MODULI IMPORTATI === 
import time
import serial

t0 = time.time() # restituisce il tempo dal 1971 fino al momento in cui  viene eseguito il codice
sleep_time = 0.400 # in secondi, è il tempo di "stop" che posso inserire nel codice
acquisition_time = 7200 # (s)
pattern = "AAAA0"

# ==== VARIABILI GLOBALI ====
discardEnable = True # da disattivare appena trovo i dati vanno bene

resto = ""
lista_dati = []

# === FUNZIONI PER CONVERTIRE I VALORI DA ESADECIMALI A DECIMALI

def temperatura_vera(temp_raw):
	a=-39.7
	b=0.01
	T=a+b*temp_raw
	return T

def umidita_vera(hum_raw, temperatura_vera):
	a=-2.0468
	b=0.0367
	c=-1.5955*(10**(-6))	
	RH= a+b*hum_raw+c*(hum_raw)**2
	T1=0.01
	T2=0.00008
	U= RH + (temperatura_vera-25)*(T1+T2*hum_raw)
	return U

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
		t = temperatura_vera(self.temp)
		u = umidita_vera(self.hr, t)
		return f"Attributi dell'oggetto:\nDato: HR = {u} , T  = {t}"
     
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
	return buffer, discardEnable
        

gm = time.gmtime()
    
ty = gm.tm_year
tmon = gm.tm_mon
tday = gm.tm_mday 
thour = gm.tm_hour + 1 # In Italy, with solar time, we have UTC+1, with legal time UTC+21
tmin = gm.tm_min
tsec = gm.tm_sec  

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
N = 0
ciclo = 0
 
start = time.time()
with open(file_name, "w") as file:
	while (time.time() - start < acquisition_time):
    
	#	if time.time() - start > 5: # svuota la lista ogni minuto
	#		lista_dati = []
        
		print("===========================================================================================================")
		print("ACQUISIZIONE DATI IN CORSO...")
		print(f"CICLO NUMERO = {ciclo}")
		ciclo += 1
		#print(f"lista oggetti = {lista_dati}")
		time.sleep(sleep_time)
		data_coming = ser.in_waiting
		N += data_coming
        # numero di bytes presenti nel buffer
		print(f"Numero di bytes presenti nel buffer: {data_coming}")
        
		if data_coming > 0: # se sono presenti bytes di dati
			daq_time = time.time()  - start # tempo di acquisizione per la prima stringa di dati
			data = ser.read(data_coming) 
            
			if data: # se la stringa non è vuota
				print(f"Dati in arrivo [{data}]")
				hex_string = ''.join(f"{b:02X}" for b in data) 
                # hex_string1 = data.hex()
                # print(f"")

                # questo vuol dire ogni "b" == dato che leggi, convertilo in formato
                # f"{} == formato esadecimale 02X usando due cifre
                
				buffer = resto + hex_string
                
				print(f"Dati presenti nel buffer: {buffer}")
                # non è detto che vadano bene, quindi 
				buffer_temp, discardEnable = Discard(buffer, discardEnable)
				if discardEnable and buffer_temp == buffer:
					resto += buffer_temp #  qui il resto va sommato finché non trovo un pattern
					print(f"Nessun pattern trovato. Aggiorno il resto = {resto}")
					
				else:
					buffer = buffer_temp
					print(f"Dato rimanente rilevato: {buffer}")

		        # === INIZIO PROCEDURA PER TROVARE I PATTERN ALL'INTERNO DELLA STRINGA === 
		        
				index = buffer.find(pattern)
				posizioni = []
		        
				while index != -1:
					posizioni.append(index)
					index = buffer.find(pattern, index +1) 
		            
		            # mi restituirà una lista del tipo posizioni = [0, 12, 24]
		        
				print(f"Trovati {len(posizioni)}")
				n = 1
				i = 0
				time_resto = 0
				for pos in posizioni:
					if len(buffer[pos:]) >= 12:
						stringa_dato = buffer[pos : pos + 12]
						time_dato = daq_time + i/n*sleep_time
						dato = Dato(stringa_dato, time_dato)
						lista_dati.append(dato)
						print(f"oggetto {dato} valido")
						#print(f"valori: HR = {dato.hr}, T = {dato.temp}, t = {dato.time}")
						#file.write(f"{dato.hr} {dato.temp} {dato.time}\n")
						temp_num = int(dato.temp, base = 16)
						hr_num =int(dato.hr, base = 16)

						temp_vera = temperatura_vera(temp_num)
						hr_vera = umidita_vera(hr_num, temp_vera)
						print(f"valori veri: HR = {hr_vera:.2f}, T = {temp_vera:.2f}, t = {dato.time:.3f}")
						file.write(f"{hr_vera:.2f} {temp_vera:.2f} {dato.time:.3f}\n")

						file.flush()
						n +=1 
						i += 1
						if len(buffer[pos + 12 :]) < 5: # es: AAAA0YYYXXXXAAA, senza pattern
							resto = buffer[pos + 12:] # qui invece il resto va ridefinito
							print(f"dato {resto} incompleto senza pattern")
					else: # es AAAA0YYYXXXXAAAA0XX, con pattern
						resto = buffer[pos:]
						print(f"dato {resto} incompleto con pattern")
						
	print(f"numero di bytes totale = {N}")
ser.close()
