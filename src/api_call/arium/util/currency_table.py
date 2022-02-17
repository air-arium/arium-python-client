from typing import Dict, List


class Currency:
    def __init__(self, code: str, rate: float, base: bool = True):
        self.code = code.upper()
        self.rate = rate
        self.base = base

    def get(self) -> Dict:
        return {
            "code": self.code,
            "rate": self.rate,
            "base": self.base
        }

    def compare_code(self, code):
        return self.code == code.upper()


class CurrencyTable:
    def __init__(self, name: str, currencies: List[Currency] = None):
        self.name = name
        self.currencies = currencies if currencies is not None else []

    def add(self, currency: Currency):
        self.remove(currency.code)
        self.currencies.append(currency)

    def remove(self, code: str):
        self.currencies = [c for c in self.currencies if not c.compare_code(code)]

    def rename(self, name: str):
        self.name = name

    def get(self) -> Dict:
        return {
            "currencies": [c.get() for c in self.currencies],
            "name": self.name
        }
