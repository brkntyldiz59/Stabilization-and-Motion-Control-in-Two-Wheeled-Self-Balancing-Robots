from machine import Pin, PWM, I2C, UART
import time
import math

#haberlesme ve sensör adresleri pin tanımları
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
MPU_ADDR = 0x68

#Motor sürücünün pin tnaımları
pwma = PWM(Pin(18)); pwma.freq(20000)
ain1 = Pin(16, Pin.OUT); ain2 = Pin(17, Pin.OUT)
pwmb = PWM(Pin(21)); pwmb.freq(20000)
bin1 = Pin(19, Pin.OUT); bin2 = Pin(20, Pin.OUT)

#enkoder pin tanımları
enc_sol_a = Pin(12, Pin.IN, Pin.PULL_UP); enc_sol_b = Pin(13, Pin.IN, Pin.PULL_UP)
enc_sag_a = Pin(10, Pin.IN, Pin.PULL_UP); enc_sag_b = Pin(11, Pin.IN, Pin.PULL_UP)
sol_sayac = 0; sag_sayac = 0

#enkoder interrupt ayarı
def sol_enkoder_kesmesi(pin):
    global sol_sayac
    if enc_sol_b.value() == 0: sol_sayac += 1
    else: sol_sayac -= 1
    
def sag_enkoder_kesmesi(pin):
    global sag_sayac
    if enc_sag_b.value() == 0: sag_sayac -= 1 
    else: sag_sayac += 1
    
enc_sol_a.irq(trigger=Pin.IRQ_RISING, handler=sol_enkoder_kesmesi)
enc_sag_a.irq(trigger=Pin.IRQ_RISING, handler=sag_enkoder_kesmesi)

#sensör uyandırma
i2c.writeto_mem(MPU_ADDR, 0x6B, bytearray([0x00]))

#sensör verisi okuma
def veri_oku(kayit_adresi):
    try:
        veri = i2c.readfrom_mem(MPU_ADDR, kayit_adresi, 2)
        deger = (veri[0] << 8) | veri[1]
        if deger > 32767: deger -= 65536
        return deger
    except: return 0

# kontrolör ayarları
#denge PID katsayilari inner loop
Kp = 10.0          # proportional
Kd = 0.35 #derivative

#center of mass telafisi için
MEKANIK_OFFSET = -1.43

#velocity pid katsayilari outer loop
Kp_vel = 0.05      #proportiional
Ki_vel = 0.03 #integral
hiz_integral = 0.0

#Kalman filtresi ayarlari
#gürültü kovaryans matrisleri
#matrisler
Q_angle = 0.001; Q_bias = 0.003
R_measure = 1.0
aci_kalman, bias = 0.0, 0.0; P = [[0.0, 0.0], [0.0, 0.0]]

def kalman_hesapla(yeni_aci, yeni_oran, dt):
    
    global aci_kalman, bias, P
    aci_kalman += dt * (yeni_oran - bias)
    P[0][0] += dt * (dt * P[1][1] - P[0][1] - P[1][0] + Q_angle)
    P[0][1] -= dt * P[1][1]; P[1][0] -= dt * P[1][1]; P[1][1] += Q_bias * dt
    S = P[0][0] + R_measure; K = [P[0][0] / S, P[1][0] / S]; y = yeni_aci - aci_kalman
    aci_kalman += K[0] * y; bias += K[1] * y
    P[0][0] -= K[0] * P[0][0]; P[0][1] -= K[0] * P[0][1]
    P[1][0] -= K[1] * P[0][0]; P[1][1] -= K[1] * P[0][1]
    return aci_kalman

#motor sürüş ayarlari
def motorlari_sur(ana_pwm):
    global gercek_aci
        # 40 dereceden fazla yatarsa motorlar kilitlencek
    if abs(gercek_aci) > 40: 
        pwma.duty_u16(0); pwmb.duty_u16(0)
        return
        #pwm ayari
    def hiz_hazirla(deger):
        hiz_siniri = max(min(abs(deger), 240), 0)
        return int((hiz_siniri / 255.0) * 65535)
    
    if ana_pwm > 0:
        ain1.value(0); ain2.value(1); bin1.value(1); bin2.value(0)
        
    else: 
        ain1.value(1); ain2.value(0); bin1.value(0); bin2.value(1)
    pwma.duty_u16(hiz_hazirla(ana_pwm)); pwmb.duty_u16(hiz_hazirla(ana_pwm))

#global döngü degiskenleri
eski_konum = 0
filtrelenmis_hiz = 0.0
eski_zaman = time.ticks_ms()
komut_hiz = 0.0
hedef_hiz = 0.0
gercek_hedef_aci = 0.0 

#mod değişkenleri
aktif_yatma_siniri = 10.0  
aktif_integral_limiti = 300.0 

#matlab grafikleri için
ham_gyro_acisi = 0.0
print_sayaci = 0  

while True:
    zaman_simdi = time.ticks_ms()
    dt = time.ticks_diff(zaman_simdi, eski_zaman) / 1000.0
    
    if dt <= 0: dt = 0.001
    eski_zaman = zaman_simdi
    
    # haberleşme bloğu
    if uart.any():
        try:
            
            ham_veri = uart.read().decode('utf-8').strip()
            if ham_veri:
                cmd = ham_veri[-1] 
                
                # düz zemin için ileri komut
                if '1' == cmd: 
                    komut_hiz = 130.0
                    aktif_yatma_siniri = 10.0  
                    aktif_integral_limiti = 300.0  
                    
                # düz zemin için geri komut   
                elif '2' == cmd: 
                    komut_hiz = -100.0
                    aktif_yatma_siniri = 10.0  
                    aktif_integral_limiti = 300.0  
                    
               #düz zemin için dur komut
                elif '0' == cmd: 
                    komut_hiz = 0.0   
                    aktif_yatma_siniri = 10.0  
                    aktif_integral_limiti = 300.0  
                    
                # rampa için çıkış modu
                elif '3' == cmd: 
                    komut_hiz = 200.0          
                    aktif_yatma_siniri = 30.0  
                    aktif_integral_limiti = 1200.0  
                    
                # rampa için iniş modu
                elif '4' == cmd: 
                    komut_hiz = -60.0          
                    aktif_yatma_siniri = 30.0
                    aktif_integral_limiti = 1200.0
                    
                 # rampada durma modu
                elif '5' == cmd:
                    komut_hiz = 0.001        
                    aktif_yatma_siniri = 30.0
                    aktif_integral_limiti = 1800.0
                    
        except: pass
    
    try:
         #sensörden verileri alma
        acc_y, acc_z = veri_oku(0x3D), veri_oku(0x3F)
        ivme_acisi = math.atan2(acc_y, acc_z) * 180 / math.pi
        gyro_x = veri_oku(0x43) / 131.0
        
        # matlab içinn
        ham_gyro_acisi += gyro_x * dt
        
        #kalman filtresinden geken temiz açı
        gercek_aci = kalman_hesapla(ivme_acisi, gyro_x, dt) - MEKANIK_OFFSET
        
        #enkoderlerden gelen hız ölçümü ve low pass filtre 
        ortalama_konum = (sol_sayac + sag_sayac) / 2.0
        ham_hiz = (ortalama_konum - eski_konum) / dt
        eski_konum = ortalama_konum
        filtrelenmis_hiz = (0.9 * filtrelenmis_hiz) + (0.1 * ham_hiz)

        #burası komut gelince robot bir anda hızlanmasın diye 
        ivme_adimi = 0.8 
        if hedef_hiz < komut_hiz:
            hedef_hiz += ivme_adimi
            if hedef_hiz > komut_hiz: hedef_hiz = komut_hiz
            
        elif hedef_hiz > komut_hiz:
            hedef_hiz -= ivme_adimi
            if hedef_hiz < komut_hiz: hedef_hiz = komut_hiz

        if komut_hiz == 0.0 and abs(hedef_hiz) < 1.0:
            hedef_hiz = 0.0
            hiz_integral = 0.0 

       # hız hatasından açı üretimi outer loop      
        hiz_hatasi = hedef_hiz - filtrelenmis_hiz
        
        if komut_hiz != 0.0:
            hiz_integral += hiz_hatasi * dt
            hiz_integral = max(min(hiz_integral, aktif_integral_limiti), -aktif_integral_limiti)
        
        ham_hedef_aci = - (hiz_hatasi * Kp_vel + hiz_integral * Ki_vel)
        ham_hedef_aci = max(min(ham_hedef_aci, aktif_yatma_siniri), -aktif_yatma_siniri)
        
        # inner loop
        gercek_hedef_aci = ham_hedef_aci        
        hata = gercek_aci - gercek_hedef_aci
        
        # Klasik PD formülü
        pid_cikisi = (Kp * hata) + (Kd * gyro_x)
        
        motorlari_sur(pid_cikisi)
           
        #matlabdan grafik çizdirmek için
#         print_sayaci += 1
#         if print_sayaci >= 10:  
#             veri_paketi = f"{gercek_aci},{filtrelenmis_hiz}\n"
#             uart.write(veri_paketi.encode('utf-8'))
#             print(f"{ivme_acisi:.2f},{ham_gyro_acisi:.2f}")
#             print(f"{ivme_acisi:.2f},{ham_gyro_acisi:.2f},{gercek_aci:.2f}")
#             print_sayaci = 0
            
    except OSError:
        pass
    time.sleep(0.005)
