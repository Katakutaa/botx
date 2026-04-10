import fitz  # PyMuPDF
from config import NARXLAR

def get_pdf_pages(file_path: str) -> int:
    """PDF fayldan bet sonini aniqlaydi"""
    try:
        doc = fitz.open(file_path)
        return len(doc)
    except Exception as e:
        return -1

def get_kategoriya(bet_soni: int) -> dict:
    """Bet soniga qarab kategoriya va narxni qaytaradi"""
    for nom, info in NARXLAR.items():
        min_bet, max_bet = info["bet"]
        if min_bet <= bet_soni <= max_bet:
            return {
                "nom": nom,
                "bet_soni": bet_soni,
                "narx": info["narx"],
                "muddat": info["muddat"]
            }
    return {
        "nom": "maxsus",
        "bet_soni": bet_soni,
        "narx": None,
        "muddat": "Kelishiladi"
    }

def format_narx(narx) -> str:
    if narx is None:
        return "Kelishiladi"
    return f"{narx:,} so'm".replace(",", " ")
