from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    """Oddiy foydalanuvchi keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Buyurtma berish")],
            [KeyboardButton(text="📋 Mening buyurtmalarim")],
            [KeyboardButton(text="ℹ️ Ma'lumot")],
        ],
        resize_keyboard=True
    )

def admin_menu():
    """Admin keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏳ Kutilayotganlar"), KeyboardButton(text="🟢 Tasdiqlangan")],
            [KeyboardButton(text="📋 Barcha buyurtmalar"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="🔍 Buyurtma qidirish")],
        ],
        resize_keyboard=True
    )

def invoice_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="invoice_tasdiqlash"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="invoice_bekor"),
        ]
    ])

def admin_tasdiqlash_kb(order_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin_ok_{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_rad_{order_id}"),
        ]
    ])

def admin_fayl_kb(order_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 O'quv reja yuborish", callback_data=f"yuborish_{order_id}")]
    ])
