from typing import Dict


def get_currency(code: str, rate: float, base: bool = True) -> Dict:
    return {"code": code, "rate": rate, "base": base}
