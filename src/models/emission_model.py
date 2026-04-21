# src/models/emission_model.py
"""
Aviation Emission Calculation Engine
ICAO + Boeing Fuel Flow Method 2 (BFFM2)
"""

import numpy as np
from src.models.atmosphere import ISAAtmosphere   # Bu dosya varsa
# from config.settings import EI_CO2, EI_H2O, EI_SO2   # Bu kısım sonra düzelteceğiz

class EmissionCalculator:
    """Uçak emisyonlarını hesaplayan ana sınıf"""

    # Motor veritabanı (gerçek veriler)
    ENGINE_EMISSION_DB = {
        'CFM56-7B26': {   # Boeing 737-800
            'manufacturer': 'CFM International',
            'bypass_ratio': 5.1,
            'ei_nox': {'idle': 4.0, 'approach': 9.4, 'climb': 18.4, 'takeoff': 27.4},
            'ei_co': {'idle': 25.0, 'approach': 4.5, 'climb': 0.8, 'takeoff': 0.5}
        },
        'LEAP-1B': {      # Boeing 737 MAX
            'manufacturer': 'CFM International',
            'bypass_ratio': 9.0,
            'ei_nox': {'idle': 3.2, 'approach': 7.5, 'climb': 15.0, 'takeoff': 22.0},
            'ei_co': {'idle': 20.0, 'approach': 3.5, 'climb': 0.6, 'takeoff': 0.4}
        },
        'CFM56-5B4/3': {  # Airbus A320
            'ei_nox': {'idle': 3.8, 'approach': 8.8, 'climb': 17.2, 'takeoff': 25.8}
        }
    }

    # Sık kullanılan havalimanları
    AIRPORTS = {
        'LTFM': {'name': 'Istanbul', 'lat': 41.275, 'lon': 28.752},
        'LTAC': {'name': 'Ankara', 'lat': 40.128, 'lon': 32.995},
        'LTAI': {'name': 'Antalya', 'lat': 36.899, 'lon': 30.800},
        'EGLL': {'name': 'London Heathrow', 'lat': 51.470, 'lon': -0.454},
        'EDDF': {'name': 'Frankfurt', 'lat': 50.033, 'lon': 8.571},
    }

    def __init__(self):
        self.atm = ISAAtmosphere()

        # Geçici emisyon katsayıları (gerçek değerler)
        self.EI_CO2 = 3.16   # 1 kg Jet A1 yakıt ≈ 3.16 kg CO2
        self.EI_H2O = 1.23   # 1 kg yakıt ≈ 1.23 kg su buharı
        self.EI_SO2 = 0.0008 # çok az

    # ====================== TEMEL HESAPLAR ======================
    def co2_from_fuel(self, fuel_kg):
        """Yakıt miktarından CO2 hesaplama"""
        return fuel_kg * self.EI_CO2

    def h2o_from_fuel(self, fuel_kg):
        return fuel_kg * self.EI_H2O

    def calculate_flight_emissions(self, fuel_burn_kg, distance_nm, 
                                   engine_type='CFM56-7B26',
                                   cruise_altitude_ft=35000):
        """Bir uçuş için tüm emisyonları hesapla"""
        
        co2 = self.co2_from_fuel(fuel_burn_kg)
        h2o = self.h2o_from_fuel(fuel_burn_kg)

        # Basit NOx tahmini (şimdilik)
        nox_kg = fuel_burn_kg * 0.015   # ortalama değer, ileride geliştireceğiz

        return {
            'fuel_burn_kg': round(fuel_kg, 1),
            'distance_nm': distance_nm,
            'emissions': {
                'CO2_kg': round(co2, 1),
                'NOx_kg': round(nox_kg, 2),
                'H2O_kg': round(h2o, 1),
            },
            'details': {
                'engine_type': engine_type,
                'cruise_altitude_ft': cruise_altitude_ft
            }
        }


# ====================== DEMO ======================
def demo():
    print("=== UÇAK EMİSYON HESAPLAMA MOTORU ===\n")
    
    calc = EmissionCalculator()

    print("Örnek 1: 10.000 kg yakıt yakan uçak")
    result = calc.calculate_flight_emissions(
        fuel_burn_kg=10000,
        distance_nm=1200,
        engine_type='CFM56-7B26',
        cruise_altitude_ft=37000
    )

    print(f"Yakıt tüketimi     : {result['fuel_burn_kg']:,} kg")
    print(f"CO₂ emisyonu      : {result['emissions']['CO2_kg']:,} kg")
    print(f"NOx emisyonu      : {result['emissions']['NOx_kg']} kg")
    print(f"Su buharı (H2O)   : {result['emissions']['H2O_kg']:,} kg")

    print("\n✅ Demo başarılı!")

if __name__ == "__main__":
    demo()