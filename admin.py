import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from utils.keyboards import admin_fayl_kb
from utils.database import get_order, update_order_status, set_result_file, get_all_orders
from utils.pdf_utils import format_narx

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

class AdminState(StatesGroup):
    fayl_yuborish = State()

# ───── ADMIN PANEL ─────
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return

    orders = get_all_orders()
    kutilmoqda = [o for o in orders.values() if o["status"] in ["kutilmoqda", "chek_yuborildi", "tasdiqlandi"]]

    await message.answer(
        f"🔐 <b>Admin Panel</b>\n\n"
        f"📊 Jami buyurtmalar: <b>{len(orders)}</b>\n"
        f"⏳ Jarayondagi: <b>{len(kutilmoqda)}</b>\n\n"
        f"<b>Buyruqlar:</b>\n"
        f"/orders — Barcha buyurtmalar\n"
        f"/order [ID] — Buyurtma ma'lumoti",
        parse_mode="HTML"
    )

# ───── BARCHA BUYURTMALAR ─────
@router.message(Command("orders"))
async def all_orders(message: Message):
    if not is_admin(message.from_user.id):
        return

    orders = get_all_orders()
    if not orders:
        await message.answer("📭 Hech qanday buyurtma yo'q.")
        return

    status_emoji = {
        "kutilmoqda": "🟡",
        "chek_yuborildi": "🔵",
        "tasdiqlandi": "🟢",
        "rad_etildi": "🔴",
        "bajarildi": "✅"
    }

    text = "📋 <b>Barcha buyurtmalar:</b>\n\n"
    for order_id, order in list(orders.items())[-20:]:
        emoji = status_emoji.get(order["status"], "⚪")
        narx = format_narx(order["narx"])
        text += f"{emoji} #{order_id} | @{order['username']} | {order['bet_soni']}b | {narx} | {order['status']}\n"

    await message.answer(text, parse_mode="HTML")

# ───── BITTA BUYURTMA ─────
@router.message(Command("order"))
async def one_order(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Ishlatish: /order 0001")
        return

    order_id = parts[1].zfill(4)
    order = get_order(order_id)

    if not order:
        await message.answer(f"❌ #{order_id} buyurtma topilmadi.")
        return

    narx = format_narx(order["narx"])
    await message.answer(
        f"📌 <b>Buyurtma #{order_id}</b>\n\n"
        f"👤 @{order['username']} | ID: <code>{order['user_id']}</code>\n"
        f"📄 Bet soni: {order['bet_soni']}\n"
        f"💰 Narx: {narx}\n"
        f"⏱ Muddat: {order['muddat']}\n"
        f"📊 Status: {order['status']}\n"
        f"📅 Sana: {order['created_at']}",
        parse_mode="HTML",
        reply_markup=admin_fayl_kb(order_id) if order["status"] == "tasdiqlandi" else None
    )

# ───── TO'LOVNI TASDIQLASH ─────
@router.callback_query(F.data.startswith("admin_ok_"))
async def admin_tasdiqlash(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    order_id = callback.data.replace("admin_ok_", "")
    order = get_order(order_id)

    if not order:
        await callback.answer("Buyurtma topilmadi!")
        return

    update_order_status(order_id, "tasdiqlandi")

    # Buyurtmachiga xabar
    await bot.send_message(
        order["user_id"],
        f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
        f"📌 Buyurtma: #<b>{order_id}</b>\n"
        f"⏱ O'quv reja {order['muddat']} ichida tayyor bo'ladi.\n\n"
        f"Tayyor bo'lganda sizga yuboriladi 📨",
        parse_mode="HTML"
    )

    await callback.message.edit_caption(
        callback.message.caption + f"\n\n✅ <b>TASDIQLANDI</b>",
        parse_mode="HTML",
        reply_markup=admin_fayl_kb(order_id)
    )
    await callback.answer("✅ Tasdiqlandi!")

# ───── TO'LOVNI RAD ETISH ─────
@router.callback_query(F.data.startswith("admin_rad_"))
async def admin_rad(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    order_id = callback.data.replace("admin_rad_", "")
    order = get_order(order_id)

    if not order:
        await callback.answer("Buyurtma topilmadi!")
        return

    update_order_status(order_id, "rad_etildi")

    # Buyurtmachiga xabar
    await bot.send_message(
        order["user_id"],
        f"❌ <b>To'lovingiz tasdiqlanmadi.</b>\n\n"
        f"📌 Buyurtma: #<b>{order_id}</b>\n\n"
        f"Muammo bo'lsa admin bilan bog'laning.",
        parse_mode="HTML"
    )

    await callback.message.edit_caption(
        callback.message.caption + f"\n\n❌ <b>RAD ETILDI</b>",
        parse_mode="HTML"
    )
    await callback.answer("❌ Rad etildi!")

# ───── O'QUV REJA YUBORISH BOSQICHI ─────
@router.callback_query(F.data.startswith("yuborish_"))
async def yuborish_bosqich(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    order_id = callback.data.replace("yuborish_", "")
    await state.update_data(order_id=order_id)
    await state.set_state(AdminState.fayl_yuborish)

    await callback.message.answer(
        f"📤 #{order_id} buyurtma uchun o'quv reja faylini yuboring (PDF yoki Word):"
    )
    await callback.answer()

# ───── O'QUV REJA FAYLINI QABUL QILISH ─────
@router.message(AdminState.fayl_yuborish, F.document)
async def oquv_reja_yuborish(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    order_id = data.get("order_id")
    order = get_order(order_id)

    if not order:
        await message.answer("❌ Buyurtma topilmadi.")
        await state.clear()
        return

    result_file_id = message.document.file_id
    set_result_file(order_id, result_file_id)

    # Buyurtmachiga o'quv rejani yuborish
    await bot.send_document(
        order["user_id"],
        document=result_file_id,
        caption=(
            f"🎉 <b>O'quv rejangiz tayyor!</b>\n\n"
            f"📌 Buyurtma: #<b>{order_id}</b>\n"
            f"📄 Faylni yuklab oling.\n\n"
            f"Xizmatimizdan foydalanganingiz uchun rahmat! 🙏"
        ),
        parse_mode="HTML"
    )

    await message.answer(f"✅ O'quv reja #{order_id} buyurtmachiga yuborildi!")
    await state.clear()

# ───── MAXSUS BUYURTMA CHAT ─────
@router.callback_query(F.data.startswith("admin_chat_"))
async def admin_chat(callback: CallbackQuery, bot: Bot):
    order_id = callback.data.replace("admin_chat_", "")
    order = get_order(order_id)

    if order:
        await bot.send_message(
            ADMIN_ID,
            f"💬 <b>Maxsus buyurtma #{order_id}</b>\n"
            f"Foydalanuvchi: @{order['username']} (<code>{order['user_id']}</code>)\n"
            f"Narx kelishish kerak!",
            parse_mode="HTML"
        )

    await callback.answer("Admin bilan bog'lanildi! Tez orada javob beriladi.", show_alert=True)
