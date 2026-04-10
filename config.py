import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "0")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789,324561861"))  # Telegram ID'ingiz

# Karta rekvizitlari
KARTA_RAQAM = os.getenv("KARTA_RAQAM", "8600 XXXX XXXX XXXX")
KARTA_EGASI = os.getenv("KARTA_EGASI", "Ism Familiya")

# Qat'iy narx va muddat
NARX = 900_000       # so'm
MUDDAT = "24 soat"

KANAL_ID = int(os.getenv("KANAL_ID", "-1003905433017"))
