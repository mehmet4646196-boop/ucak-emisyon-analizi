# run_demo.py
# Uçak Emisyon Hesaplama Motoru - Tam Versiyon (Motor DB + Yıllık Rapor)

print("✈️  UÇAK EMİSYON HESAPLAMA MOTORU")
print("   Tam Versiyon - Motor Veritabanı + Yıllık Rapor")
print("=" * 90)

class EmissionCalculator:
    def __init__(self):
        self.EI_CO2 = 3.16
        self.EI_H2O = 1.23
        
        # Gerçek Motor Veritabanı
        self.engines = {
            'CFM56-7B26':  {'name': 'CFM56-7B26 (B737-800)',     'nox_factor': 1.00, 'pax': 162},
            'LEAP-1B':     {'name': 'LEAP-1B (B737 MAX)',        'nox_factor': 0.82, 'pax': 172},
            'CFM56-5B4':   {'name': 'CFM56-5B4 (A320)',          'nox_factor': 0.95, 'pax': 150},
            'GE90-115B':   {'name': 'GE90-115B (B777-300ER)',    'nox_factor': 1.35, 'pax': 365},
        }

        # Havalimanları
        self.airports = {
            'LTFM': {'name': 'İstanbul', 'lat': 41.275, 'lon': 28.752},
            'LTAC': {'name': 'Ankara',   'lat': 40.128, 'lon': 32.995},
            'LTAI': {'name': 'Antalya',  'lat': 36.899, 'lon': 30.800},
            'LTBJ': {'name': 'İzmir',    'lat': 38.292, 'lon': 27.157},
            'EGLL': {'name': 'London',   'lat': 51.470, 'lon': -0.454},
            'EDDF': {'name': 'Frankfurt','lat': 50.033, 'lon': 8.571},
            'OMDB': {'name': 'Dubai',    'lat': 25.253, 'lon': 55.364},
        }

    def great_circle_distance(self, origin, dest):
        if origin not in self.airports or dest not in self.airports:
            return None
        o = self.airports[origin]
        d = self.airports[dest]
        from math import radians, sin, cos, sqrt, atan2
        R = 6371
        lat1, lon1 = radians(o['lat']), radians(o['lon'])
        lat2, lon2 = radians(d['lat']), radians(d['lon'])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return round(R * c / 1.852, 1)

    def nox_estimate(self, fuel_kg, altitude_ft, engine_type):
        engine = self.engines.get(engine_type, self.engines['CFM56-7B26'])
        base = fuel_kg * 0.014
        altitude_factor = max(0.65, 1 - (altitude_ft - 30000) / 150000)
        return base * altitude_factor * engine['nox_factor']

    def check_contrail(self, altitude_ft, humidity=0.6):
        temp_c = 15 - (altitude_ft / 1000) * 1.98
        persistent = temp_c < -47 and humidity > 0.75
        likely = temp_c < -40 and humidity > 0.5

        print(f"\n☁️  CONTRAIL ANALİZİ")
        print(f"   İrtifa           : {altitude_ft:,} ft")
        print(f"   Tahmini Sıcaklık : {temp_c:.1f} °C")
        if persistent:
            print("   🔴 PERSISTENT CONTRAIL → İklim etkisi ÇOK YÜKSEK!")
        elif likely:
            print("   🟠 Contrail oluşma riski VAR")
        else:
            print("   🟢 Contrail riski düşük")

    def calculate_flight(self, fuel_kg, distance_nm, engine_type="CFM56-7B26", altitude_ft=37000, origin=None, dest=None):
        engine = self.engines.get(engine_type, self.engines['CFM56-7B26'])
        co2 = fuel_kg * self.EI_CO2
        h2o = fuel_kg * self.EI_H2O
        nox = self.nox_estimate(fuel_kg, altitude_ft, engine_type)
        pax = engine['pax']
        co2_per_pax_km = (co2 / (pax * distance_nm * 1.852)) * 1000 if pax > 0 else 0

        route = f"{origin}→{dest}" if origin and dest else "Manuel"

        print(f"\n{'='*90}")
        print(f"                  UÇUŞ EMİSYON RAPORU - {route}")
        print(f"{'='*90}")
        print(f" Yakıt Tüketimi      : {fuel_kg:,.0f} kg")
        print(f" Mesafe              : {distance_nm:,.0f} NM")
        if origin and dest:
            print(f" Rota                : {self.airports[origin]['name']} → {self.airports[dest]['name']}")
        print(f" Motor               : {engine['name']}")
        print(f" İrtifa              : {altitude_ft:,.0f} ft")
        print("-" * 80)
        print(f" CO₂ Emisyonu        : {co2:,.0f} kg ({co2/1000:.1f} ton)")
        print(f" Su Buharı           : {h2o:,.0f} kg")
        print(f" NOx Emisyonu        : {nox:.1f} kg")
        print(f" CO₂ / Pax / km      : {co2_per_pax_km:.1f} g")
        print(f" Verimlilik          : {fuel_kg / distance_nm:.2f} kg/NM")
        
        self.check_contrail(altitude_ft)
        
        total_co2e = co2 + nox * 298 + h2o * 0.3
        print(f"\n Toplam İklim Etkisi (CO₂e) : {total_co2e:,.0f} kg")


# ====================== ANA PROGRAM ======================
if __name__ == "__main__":
    calc = EmissionCalculator()
    flights = []   # Yıllık rapor için uçuşları saklayacağız

    print("Hoş geldiniz! Artık motor veritabanı ve yıllık rapor var.\n")

    while True:
        print("\n" + "-"*90)
        mode = input("1: Tek uçuş hesapla | 2: Yıllık rapor oluştur | q: Çıkış → ").strip()

        if mode == 'q':
            break
        if mode == '2' and flights:
            # Yıllık Özet Rapor
            total_fuel = sum(f['fuel'] for f in flights)
            total_co2 = total_fuel * calc.EI_CO2
            print(f"\n📊 YILLIK CORSIA ÖZET RAPOR")
            print(f"Toplam Uçuş Sayısı : {len(flights)}")
            print(f"Toplam Yakıt       : {total_fuel:,.0f} kg ({total_fuel/1000:.1f} ton)")
            print(f"Toplam CO₂         : {total_co2:,.0f} kg ({total_co2/1000:.1f} ton)")
            print("Rapor kaydedildi (ileride dosyaya yazılabilir).")
            continue

        # Tek uçuş modu
        try:
            origin = input("Kalkış (LTFM / manuel) : ").strip().upper()
            if origin == 'MANUEL':
                fuel = float(input("Yakıt (kg)              : "))
                dist = float(input("Mesafe (NM)             : "))
                alt = int(input("İrtifa (ft)             : ") or 37000)
                eng = input("Motor (CFM56-7B26)      : ") or "CFM56-7B26"
                calc.calculate_flight(fuel, dist, eng, alt)
                flights.append({'fuel': fuel})
            else:
                dest = input("Varış Havalimanı        : ").strip().upper()
                dist = calc.great_circle_distance(origin, dest)
                if not dist:
                    print("Havalimanı kodu bulunamadı!")
                    continue
                fuel = float(input("Yakıt miktarı (kg)      : "))
                alt = int(input("İrtifa (ft)             : ") or 37000)
                eng = input("Motor tipi              : ") or "CFM56-7B26"
                
                calc.calculate_flight(fuel, dist, eng, alt, origin, dest)
                flights.append({'fuel': fuel, 'origin': origin, 'dest': dest})
        except:
            print("Giriş hatası, tekrar deneyin.")

    print("\nTeşekkürler! Proje tamamlandı.")
    print("İstersen bu kodu daha da geliştirebiliriz (dosyaya kaydetme, grafik vs.)")