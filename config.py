import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

# Bir yoki bir nechta admin ID (vergul bilan ajrating)
# Misol: "123456789" yoki "123456789,987654321"
_admin_ids = os.getenv("ADMIN_ID", "123456789")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids.split(",") if x.strip()]
ADMIN_ID = ADMIN_IDS[0]  # Asosiy admin (birinchisi)

# Karta rekvizitlari
KARTA_RAQAM = os.getenv("KARTA_RAQAM", "8600 XXXX XXXX XXXX")
KARTA_EGASI = os.getenv("KARTA_EGASI", "Ism Familiya")

# Qat'iy narx va muddat
NARX = 900_000
MUDDAT = "24 soat"

# Arxiv kanali
KANAL_ID = int(os.getenv("KANAL_ID", "0"))
