from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Buyurtma berish")],
            [KeyboardButton(text="📋 Mening buyurtmalarim")],
            [KeyboardButton(text="ℹ️ Ma'lumot")],
        ],
        resize_keyboard=True
    )

def invoice_kb():
    """Invoice tasdiqlash/bekor qilish tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="invoice_tasdiqlash"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="invoice_bekor"),
        ]
    ])

def admin_tasdiqlash_kb(order_id: str):
    """Admin uchun to'lovni tasdiqlash/rad etish"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin_ok_{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_rad_{order_id}"),
        ]
    ])

def admin_fayl_kb(order_id: str):
    """Admin uchun o'quv reja yuborish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 O'quv reja yuborish", callback_data=f"yuborish_{order_id}")]
    ])
