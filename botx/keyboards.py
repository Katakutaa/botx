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

def tasdiqlash_kb(order_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ To'lov qildim", callback_data=f"tolov_{order_id}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"bekor_{order_id}"),
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

def maxsus_kb(order_id: str):
    """Maxsus buyurtma uchun narx kelishish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Admin bilan bog'lanish", callback_data=f"admin_chat_{order_id}")]
    ])
