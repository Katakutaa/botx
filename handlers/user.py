import os
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID, KARTA_RAQAM, KARTA_EGASI
from utils.pdf_utils import get_pdf_pages, get_kategoriya, format_narx
from utils.keyboards import main_menu, tasdiqlash_kb, maxsus_kb, admin_tasdiqlash_kb
from utils.database import create_order, get_order, update_order_status, get_user_orders

router = Router()
logger = logging.getLogger(__name__)

class OrderState(StatesGroup):
    fayl_kutish = State()
    chek_kutish = State()

# ───── START ─────
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Salom, <b>{message.from_user.first_name}</b>!\n\n"
        "📚 <b>O'quv Reja Bot</b>ga xush kelibsiz!\n\n"
        "Bu bot orqali siz malaka talabingizga asosan "
        "professional o'quv reja buyurtma qilishingiz mumkin.\n\n"
        "👇 Quyidagi menyudan foydalaning:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

# ───── MA'LUMOT ─────
@router.message(F.text == "ℹ️ Ma'lumot")
async def malumot(message: Message):
    await message.answer(
        "📋 <b>Narx va Muddatlar:</b>\n\n"
        "📄 1-5 bet → <b>25 000 so'm</b> | 12 soat\n"
        "📄 6-15 bet → <b>40 000 so'm</b> | 24 soat\n"
        "📄 16-30 bet → <b>60 000 so'm</b> | 48 soat\n"
        "📄 30+ bet → <b>Kelishiladi</b>\n\n"
        "💳 To'lov: Karta orqali\n"
        "📁 Fayl turi: Faqat PDF\n\n"
        "❓ Savol bo'lsa: @admin_username",
        parse_mode="HTML"
    )

# ───── BUYURTMA BERISH ─────
@router.message(F.text == "📄 Buyurtma berish")
async def buyurtma_boshlash(message: Message, state: FSMContext):
    await state.set_state(OrderState.fayl_kutish)
    await message.answer(
        "📎 Malaka talabi faylini <b>PDF</b> formatda yuboring:\n\n"
        "⚠️ Faqat PDF fayl qabul qilinadi",
        parse_mode="HTML"
    )

# ───── FAYL QABUL QILISH ─────
@router.message(OrderState.fayl_kutish, F.document)
async def fayl_qabul(message: Message, state: FSMContext, bot: Bot):
    doc = message.document

    # PDF tekshirish
    if not doc.file_name.lower().endswith(".pdf"):
        await message.answer("❌ Faqat PDF fayl yuboring!")
        return

    wait_msg = await message.answer("⏳ Fayl tahlil qilinmoqda...")

    # Faylni yuklab olish
    file_path = f"/tmp/{doc.file_id}.pdf"
    file = await bot.get_file(doc.file_id)
    await bot.download_file(file.file_path, file_path)

    # Bet sonini aniqlash
    bet_soni = get_pdf_pages(file_path)

    if bet_soni == -1:
        await wait_msg.edit_text("❌ Fayl o'qib bo'lmadi. Boshqa PDF yuboring.")
        return

    # Kategoriya va narx
    kategoriya = get_kategoriya(bet_soni)

    await state.update_data(
        file_id=doc.file_id,
        file_name=doc.file_name,
        bet_soni=bet_soni,
        kategoriya=kategoriya
    )

    # Maxsus kategoriya
    if kategoriya["nom"] == "maxsus":
        order_id = create_order(
            user_id=message.from_user.id,
            username=message.from_user.username,
            file_id=doc.file_id,
            bet_soni=bet_soni,
            kategoriya="maxsus",
            narx=None,
            muddat="Kelishiladi"
        )
        await wait_msg.edit_text(
            f"📄 Fayl qabul qilindi\n"
            f"📊 Bet soni: <b>{bet_soni} bet</b>\n"
            f"📂 Kategoriya: <b>Maxsus (30+ bet)</b>\n\n"
            f"Bu kategoriya uchun narx alohida kelishiladi.\n"
            f"Admin siz bilan bog'lanadi. Buyurtma #<b>{order_id}</b>",
            parse_mode="HTML",
            reply_markup=maxsus_kb(order_id)
        )
        # Adminga xabar
        await bot.send_document(
            ADMIN_ID,
            document=doc.file_id,
            caption=(
                f"🆕 <b>Maxsus buyurtma #{order_id}</b>\n\n"
                f"👤 Foydalanuvchi: @{message.from_user.username or 'Noma\'lum'}\n"
                f"🆔 ID: <code>{message.from_user.id}</code>\n"
                f"📄 Fayl: {doc.file_name}\n"
                f"📊 Bet soni: {bet_soni} bet\n"
                f"💰 Narx: Kelishiladi"
            ),
            parse_mode="HTML"
        )
        await state.clear()
        return

    # Oddiy kategoriya
    narx_text = format_narx(kategoriya["narx"])
    await wait_msg.edit_text(
        f"✅ <b>Fayl tahlil qilindi!</b>\n\n"
        f"📄 Fayl: <b>{doc.file_name}</b>\n"
        f"📊 Bet soni: <b>{bet_soni} bet</b>\n"
        f"📂 Kategoriya: <b>{kategoriya['nom'].capitalize()}</b>\n\n"
        f"💰 Narx: <b>{narx_text}</b>\n"
        f"⏱ Muddat: <b>{kategoriya['muddat']}</b>\n\n"
        f"Davom etasizmi?",
        parse_mode="HTML",
        reply_markup=tasdiqlash_kb("new")
    )

# ───── TO'LOV BOSQICHI ─────
@router.callback_query(F.data == "tolov_new")
async def tolov_bosqich(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    kategoriya = data.get("kategoriya", {})
    narx_text = format_narx(kategoriya.get("narx"))

    order_id = create_order(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        file_id=data["file_id"],
        bet_soni=data["bet_soni"],
        kategoriya=kategoriya["nom"],
        narx=kategoriya["narx"],
        muddat=kategoriya["muddat"]
    )

    await state.update_data(order_id=order_id)
    await state.set_state(OrderState.chek_kutish)

    await callback.message.edit_text(
        f"💳 <b>To'lov rekvizitlari:</b>\n\n"
        f"🏦 Karta: <code>{KARTA_RAQAM}</code>\n"
        f"👤 Egasi: <b>{KARTA_EGASI}</b>\n"
        f"💰 Summa: <b>{narx_text}</b>\n\n"
        f"📌 Buyurtma: #<b>{order_id}</b>\n\n"
        f"To'lovni amalga oshirgandan so'ng <b>chek rasmini</b> yuboring 📸",
        parse_mode="HTML"
    )
    await callback.answer()

# ───── BEKOR QILISH ─────
@router.callback_query(F.data == "bekor_new")
async def bekor(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")
    await callback.answer()

# ───── CHEK QABUL QILISH ─────
@router.message(OrderState.chek_kutish, F.photo)
async def chek_qabul(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get("order_id")
    order = get_order(order_id)

    if not order:
        await message.answer("❌ Buyurtma topilmadi.")
        await state.clear()
        return

    narx_text = format_narx(order["narx"])

    # Adminga chek + ma'lumot yuborish
    await bot.send_photo(
        ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=(
            f"🧾 <b>To'lov cheki - Buyurtma #{order_id}</b>\n\n"
            f"👤 Foydalanuvchi: @{order['username']}\n"
            f"🆔 ID: <code>{order['user_id']}</code>\n"
            f"📄 Bet soni: {order['bet_soni']} bet\n"
            f"💰 Summa: {narx_text}\n"
            f"⏱ Muddat: {order['muddat']}"
        ),
        parse_mode="HTML",
        reply_markup=admin_tasdiqlash_kb(order_id)
    )

    # Faylni ham adminga yuborish
    await bot.send_document(
        ADMIN_ID,
        document=order["file_id"],
        caption=f"📎 Malaka talabi fayli - #{order_id}"
    )

    update_order_status(order_id, "chek_yuborildi")
    await state.clear()

    await message.answer(
        f"✅ <b>Chekingiz qabul qilindi!</b>\n\n"
        f"📌 Buyurtma raqami: #<b>{order_id}</b>\n"
        f"⏳ Admin tekshirib, tez orada tasdiqlaydi.\n\n"
        f"Tayyor bo'lganda sizga avtomatik yuboriladi 📨",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

# ───── MENING BUYURTMALARIM ─────
@router.message(F.text == "📋 Mening buyurtmalarim")
async def mening_buyurtmalar(message: Message):
    orders = get_user_orders(message.from_user.id)

    if not orders:
        await message.answer("📭 Sizda hali buyurtma yo'q.")
        return

    status_emoji = {
        "kutilmoqda": "🟡",
        "chek_yuborildi": "🔵",
        "tasdiqlandi": "🟢",
        "rad_etildi": "🔴",
        "bajarildi": "✅"
    }

    text = "📋 <b>Sizning buyurtmalaringiz:</b>\n\n"
    for order_id, order in list(orders.items())[-5:]:
        emoji = status_emoji.get(order["status"], "⚪")
        narx = format_narx(order["narx"])
        text += (
            f"{emoji} #{order_id} | {order['bet_soni']} bet | {narx}\n"
            f"   📅 {order['created_at']} | {order['status']}\n\n"
        )

    await message.answer(text, parse_mode="HTML")

# ───── NOTO'G'RI FAYL ─────
@router.message(OrderState.fayl_kutish)
async def notogri_fayl(message: Message):
    await message.answer("❌ Iltimos, faqat <b>PDF</b> fayl yuboring!", parse_mode="HTML")

@router.message(OrderState.chek_kutish)
async def chek_eslatma(message: Message):
    await message.answer("📸 Iltimos, to'lov cheki <b>rasmini</b> yuboring!", parse_mode="HTML")
