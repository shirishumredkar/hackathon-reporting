from config import settings

class CostService:
    def __init__(self):
        # Ensure PRICE_PER_TB is loaded as a float
        try:
            self.PRICE_PER_TB = float(settings.PRICE_PER_TB)
        except (ValueError, TypeError):
            self.PRICE_PER_TB = 5.0  # Default value if conversion fails

    def estimate(self, byte_processed: int):
        if byte_processed is None:
            return 0.0

        tb = byte_processed / (1024 ** 4)
        return round(tb * self.PRICE_PER_TB, 4)