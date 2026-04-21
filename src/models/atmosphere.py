class ISAAtmosphere:
    """Basit atmosfer modeli"""

    def __init__(self):
        pass

    def temperature(self, altitude_ft):
        return 15 - (altitude_ft / 1000) * 2