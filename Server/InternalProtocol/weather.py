class Weather():
    def __init__(self, date: str, prec_tot: int, city: str):
        self.date = date
        self.prec_tot = prec_tot
        self.city = city

    def get_id(self):
        return f"{self.city}-{self.date}"

    def is_rainy(self, threshold):
        return self.prec_tot > threshold

    def get_rain(self):
        return self.prec_tot
