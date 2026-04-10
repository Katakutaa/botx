import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID, NARX, MUDDAT
from utils.keyboards import admin_menu, admin_fayl_kb
from utils.database import get_order, update_order_status, set_result_file, get_all_orders
from utils.kanal import kanal_tasdiqlandi, kanal_rad_etildi, kanal_bajarildi

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

class AdminState(StatesGroup):
    fayl_yuborish = State()
    order_id_kutish = State()  # /order uchun

# ───── START — adminga o'z keyboard ─────
@router.message(Command("start"))
async def admin_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        f"👋 Salom, Admin!\n\n"
        f"📊 Buyurtmalarni boshqarish paneli:",
        reply_markup=admin_menu()
    )

# ───── ADMIN PANEL ─────
@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        "🔐 <b>Admin Panel</b>",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )

# ───── 📋 BARCHA BUYURTMALAR ─────
@router.message(F.text == "📋 Barcha buyurtmalar")
async def all_orders(message: Message):
    if not is_admin(message.from_user.id):
        return
    orders = get_all_orders()
    if not orders:
        await message.answer("📭 Hech qanday buyurtma yo'q.")
        return

    status_emoji = {
        "kutilmoqda": "🟡", "chek_yuborildi": "🔵",
        "tasdiqlandi": "🟢", "rad_etildi": "🔴", "bajarildi": "✅"
    }
    text = "📋 <b>Barcha buyurtmalar (oxirgi 20):</b>\n\n"
    for order_id, order in list(orders.items())[-20:]:
        emoji = status_emoji.get(order["status"], "⚪")
        text += f"{emoji} <code>#{order_id}</code> | {order['kategoriya']} | @{order['username']}\n"

    await message.answer(text, parse_mode="HTML")

# ───── ⏳ KUTILAYOTGANLAR ─────
@router.message(F.text == "⏳ Kutilayotganlar")
async def pending_orders(message: Message):
    if not is_admin(message.from_user.id):
        return
    orders = get_all_orders()
    pending = {k: v for k, v in orders.items() if v["status"] == "chek_yuborildi"}

    if not pending:
        await message.answer("✅ Kutilayotgan buyurtma yo'q.")
        return

    text = f"⏳ <b>Chek yuborilgan ({len(pending)} ta):</b>\n\n"
    for order_id, order in pending.items():
        text += (
            f"🔵 <code>#{order_id}</code> | {order['kategoriya']}\n"
            f"   👤 @{order['username']} | 📅 {order['created_at']}\n\n"
        )
    text += "Buyurtma ID ni ko'rish uchun: /order 0001"
    await message.answer(text, parse_mode="HTML")

# ───── ✅ TASDIQLANGAN (ISHLASH KERAK) ─────
@router.message(F.text == "🟢 Tasdiqlangan")
async def confirmed_orders(message: Message):
    if not is_admin(message.from_user.id):
        return
    orders = get_all_orders()
    confirmed = {k: v for k, v in orders.items() if v["status"] == "tasdiqlandi"}

    if not confirmed:
        await message.answer("📭 Tasdiqlangan lekin bajarilmagan buyurtma yo'q.")
        return

    text = f"🟢 <b>Ishlash kerak ({len(confirmed)} ta):</b>\n\n"
    for order_id, order in confirmed.items():
        text += (
            f"✅ <code>#{order_id}</code> | <b>{order['kategoriya']}</b>\n"
            f"   👤 @{order['username']} | 📅 {order['created_at']}\n\n"
        )
    text += "O'quv reja yuborish uchun: /order 0001"
    await message.answer(text, parse_mode="HTML")

# ───── 📊 STATISTIKA ─────
@router.message(F.text == "📊 Statistika")
async def statistika(message: Message):
    if not is_admin(message.from_user.id):
        return
    orders = get_all_orders()

    counts = {
        "kutilmoqda": 0, "chek_yuborildi": 0,
        "tasdiqlandi": 0, "rad_etildi": 0, "bajarildi": 0
    }
    for o in orders.values():
        status = o.get("status", "kutilmoqda")
        if status in counts:
            counts[status] += 1

    bajarildi_summa = counts["bajarildi"] * NARX

    await message.answer(
        "📊 <b>Statistika</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Jami buyurtmalar: <b>{len(orders)}</b>\n\n"
        f"🟡 Kutilmoqda: <b>{counts['kutilmoqda']}</b>\n"
        f"🔵 Chek yuborildi: <b>{counts['chek_yuborildi']}</b>\n"
        f"🟢 Tasdiqlandi: <b>{counts['tasdiqlandi']}</b>\n"
        f"✅ Bajarildi: <b>{counts['bajarildi']}</b>\n"
        f"🔴 Rad etildi: <b>{counts['rad_etildi']}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Jami daromad: <b>{bajarildi_summa:,} so'm</b>",
        parse_mode="HTML"
    )

# ───── 🔍 BUYURTMA QIDIRISH ─────
@router.message(F.text == "🔍 Buyurtma qidirish")
async def buyurtma_qidirish(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminState.order_id_kutish)
    await message.answer("🔍 Buyurtma ID sini yuboring:\n<i>Misol: 0001</i>", parse_mode="HTML")

@router.message(AdminState.order_id_kutish, F.text)
async def order_id_qabul(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    order_id = message.text.strip().zfill(4)
    order = get_order(order_id)
    await state.clear()

    if not order:
        await message.answer(f"❌ #{order_id} buyurtma topilmadi.")
        return

    status_emoji = {
        "kutilmoqda": "🟡", "chek_yuborildi": "🔵",
        "tasdiqlandi": "🟢", "rad_etildi": "🔴", "bajarildi": "✅"
    }
    emoji = status_emoji.get(order["status"], "⚪")

    await message.answer(
        f"📌 <b>Buyurtma #{order_id}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 @{order['username']} | <code>{order['user_id']}</code>\n"
        f"📚 Yo'nalish: <b>{order['kategoriya']}</b>\n"
        f"📄 Bet soni: {order['bet_soni']}\n"
        f"💰 Narx: {NARX:,} so'm\n"
        f"⏱ Muddat: {MUDDAT}\n"
        f"{emoji} Status: <b>{order['status']}</b>\n"
        f"📅 Sana: {order['created_at']}",
        parse_mode="HTML",
        reply_markup=admin_fayl_kb(order_id) if order["status"] == "tasdiqlandi" else None
    )

# ───── /order buyruqi (eski usul ham ishlaydi) ─────
@router.message(Command("order"))
async def one_order(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Ishlatish: /order 0001")
        return
    order_id = parts[1].zfill(4)
    order = get_order(order_id)
    if not order:
        await message.answer(f"❌ #{order_id} topilmadi.")
        return

    await message.answer(
        f"📌 <b>Buyurtma #{order_id}</b>\n"
        f"👤 @{order['username']} | <code>{order['user_id']}</code>\n"
        f"📚 {order['kategoriya']} | 📄 {order['bet_soni']} bet\n"
        f"📊 {order['status']} | 📅 {order['created_at']}",
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
    await bot.send_message(
        order["user_id"],
        f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
        f"📌 Buyurtma: #<b>{order_id}</b>\n"
        f"⏱ O'quv reja {MUDDAT} ichida tayyor bo'ladi.\n\n"
        f"Tayyor bo'lganda sizga yuboriladi 📨",
        parse_mode="HTML"
    )
    await kanal_tasdiqlandi(bot, order_id, order)
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
    await bot.send_message(
        order["user_id"],
        f"❌ <b>To'lovingiz tasdiqlanmadi.</b>\n\n"
        f"📌 Buyurtma: #<b>{order_id}</b>\n\n"
        f"Muammo bo'lsa admin bilan bog'laning.",
        parse_mode="HTML"
    )
    await kanal_rad_etildi(bot, order_id, order)
    await callback.message.edit_caption(
        callback.message.caption + f"\n\n❌ <b>RAD ETILDI</b>",
        parse_mode="HTML"
    )
    await callback.answer("❌ Rad etildi!")

# ───── O'QUV REJA YUBORISH ─────
@router.callback_query(F.data.startswith("yuborish_"))
async def yuborish_bosqich(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return
    order_id = callback.data.replace("yuborish_", "")
    await state.update_data(order_id=order_id)
    await state.set_state(AdminState.fayl_yuborish)
    await callback.message.answer(
        f"📤 #{order_id} uchun o'quv reja faylini yuboring:"
    )
    await callback.answer()

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

    await bot.send_document(
        order["user_id"],
        document=result_file_id,
        caption=(
            f"🎉 <b>O'quv rejangiz tayyor!</b>\n\n"
            f"📌 Buyurtma: #<b>{order_id}</b>\n"
            f"📚 Yo'nalish: {order['kategoriya']}\n\n"
            f"Faylni yuklab oling. Xizmatimizdan foydalanganingiz uchun rahmat! 🙏"
        ),
        parse_mode="HTML"
    )
    await kanal_bajarildi(bot, order_id, order, result_file_id)
    await message.answer(f"✅ O'quv reja #{order_id} yuborildi!", reply_markup=admin_menu())
    await state.clear()
