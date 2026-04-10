import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # Telegram ID'ingiz

# Karta rekvizitlari
KARTA_RAQAM = os.getenv("KARTA_RAQAM", "8600 XXXX XXXX XXXX")
KARTA_EGASI = os.getenv("KARTA_EGASI", "Ism Familiya")

# Narx kategoriyalari (so'm)
NARXLAR = {
    "kichik": {"bet": (1, 5),   "narx": 25000, "muddat": "12 soat"},
    "orta":   {"bet": (6, 15),  "narx": 40000, "muddat": "24 soat"},
    "katta":  {"bet": (16, 30), "narx": 60000, "muddat": "48 soat"},
    "maxsus": {"bet": (31, 999),"narx": None,  "muddat": "Kelishiladi"},
}
