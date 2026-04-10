# 📚 O'quv Reja Bot

Telegram bot orqali malaka talabiga asosan o'quv reja buyurtma qilish tizimi.

## 📁 Fayl Tuzilishi

```
oquv_reja_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Sozlamalar
├── requirements.txt    # Kutubxonalar
├── Procfile            # Railway uchun
├── handlers/
│   ├── user.py         # Foydalanuvchi handlerlari
│   └── admin.py        # Admin handlerlari
└── utils/
    ├── database.py     # Ma'lumotlar bazasi (JSON)
    ├── keyboards.py    # Tugmalar
    └── pdf_utils.py    # PDF ishlash
```

## 🚀 Railway.app ga Deploy

### 1. Bot yaratish
1. Telegramda @BotFather ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting
4. Token oling

### 2. Admin ID olish
1. @userinfobot ga yozing
2. ID raqamingizni nusxa oling

### 3. GitHub ga yuklash
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

### 4. Railway da deploy
1. railway.app ga kiring
2. "New Project" → "Deploy from GitHub repo"
3. Repozitoriyani tanlang
4. **Variables** bo'limiga kiring va quyidagilarni kiriting:

| Variable | Qiymat |
|----------|--------|
| `BOT_TOKEN` | BotFather dan olgan token |
| `ADMIN_ID` | Sizning Telegram ID'ingiz |
| `KARTA_RAQAM` | `8600 XXXX XXXX XXXX` |
| `KARTA_EGASI` | `Ism Familiya` |

5. Deploy avtomatik boshlanadi ✅

## 🔄 Jarayon

```
Buyurtmachi PDF yuklaydi
→ Bot bet sonini aniqlab narx chiqaradi
→ Buyurtmachi to'lov qiladi
→ Chek rasmini yuboradi
→ Adminga (sizga) xabar keladi
→ Siz tasdiqlaysiz
→ O'quv rejani yuklaysiz
→ Buyurtmachiga avtomatik yuboriladi
```

## 💰 Narx Tizimi

| Bet soni | Narx | Muddat |
|----------|------|--------|
| 1-5 bet | 25 000 so'm | 12 soat |
| 6-15 bet | 40 000 so'm | 24 soat |
| 16-30 bet | 60 000 so'm | 48 soat |
| 30+ bet | Kelishiladi | - |

## ⚙️ Admin Buyruqlari

| Buyruq | Vazifa |
|--------|--------|
| `/admin` | Admin panel |
| `/orders` | Barcha buyurtmalar |
| `/order 0001` | Bitta buyurtma ma'lumoti |
