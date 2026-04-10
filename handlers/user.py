import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID, ADMIN_IDS, KARTA_RAQAM, KARTA_EGASI, NARX, MUDDAT
from utils.pdf_utils import get_pdf_pages
from utils.keyboards import main_menu, admin_menu, invoice_kb, admin_tasdiqlash_kb
from utils.database import create_order, get_order, update_order_status, get_user_orders
from utils.kanal import kanal_yangi_buyurtma

router = Router()
logger = logging.getLogger(__name__)

class OrderState(StatesGroup):
    yunalish_kutish = State()
    fayl_kutish = State()
    chek_kutish = State()

# ───── START ─────
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    # Admin bo'lsa — admin keyboard
    if message.from_user.id in ADMIN_IDS:
        await message.answer(
            f"👋 Salom, Admin! Boshqaruv paneli:",
            reply_markup=admin_menu()
        )
        return
    await message.answer(
        f"👋 Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
        "📚 <b>O'quv Reja Bot</b>ga xush kelibsiz!\n\n"
        "Bu bot orqali malaka talabingizga asosan "
        "professional o'quv reja buyurtma qilishingiz mumkin.\n\n"
        f"💰 <b>1 dona o'quv reja — {NARX:,} so'm</b>\n\n"
        "👇 Quyidagi menyudan foydalaning:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

# ───── MA'LUMOT ─────
@router.message(F.text == "ℹ️ Ma'lumot")
async def malumot(message: Message):
    await message.answer(
        "📋 <b>Xizmat haqida:</b>\n\n"
        f"📄 1 dona o'quv reja → <b>{NARX:,} so'm</b>\n"
        f"⏱ Muddat: <b>{MUDDAT}</b>\n"
        "💳 To'lov: Karta orqali\n"
        "📁 Fayl turi: Faqat PDF\n\n"
        "❓ Savol bo'lsa: +998 97 222 92 49",
        parse_mode="HTML"
    )

# ───── 1-QADAM: YO'NALISH ─────
@router.message(F.text == "📄 Buyurtma berish")
async def buyurtma_boshlash(message: Message, state: FSMContext):
    await state.set_state(OrderState.yunalish_kutish)
    await message.answer(
        "📝 <b>1-qadam: Yo'nalish nomi</b>\n\n"
        "Qaysi yo'nalish uchun o'quv reja kerak?\n\n"
        "<i>Misol: Maktabgacha ta'lim, Boshlang'ich ta'lim, Matematika...</i>",
        parse_mode="HTML"
    )

# ───── 2-QADAM: PDF ─────
@router.message(OrderState.yunalish_kutish, F.text)
async def yunalish_qabul(message: Message, state: FSMContext):
    yunalish = message.text.strip()
    if len(yunalish) < 3:
        await message.answer("❌ Yo'nalish nomini to'liq kiriting!")
        return
    await state.update_data(yunalish=yunalish)
    await state.set_state(OrderState.fayl_kutish)
    await message.answer(
        f"✅ Yo'nalish: <b>{yunalish}</b>\n\n"
        "📎 <b>2-qadam: Malaka talabi fayli</b>\n\n"
        "Endi malaka talabi faylini <b>PDF</b> formatda yuboring:",
        parse_mode="HTML"
    )

# ───── 3-QADAM: INVOICE ─────
@router.message(OrderState.fayl_kutish, F.document)
async def fayl_qabul(message: Message, state: FSMContext, bot: Bot):
    doc = message.document
    if not doc.file_name.lower().endswith(".pdf"):
        await message.answer("❌ Faqat <b>PDF</b> fayl yuboring!", parse_mode="HTML")
        return

    wait_msg = await message.answer("⏳ Fayl qabul qilindi, tayyorlanmoqda...")

    file_path = f"/tmp/{doc.file_id}.pdf"
    file = await bot.get_file(doc.file_id)
    await bot.download_file(file.file_path, file_path)
    bet_soni = get_pdf_pages(file_path)

    data = await state.get_data()
    yunalish = data.get("yunalish", "—")

    await state.update_data(
        file_id=doc.file_id,
        file_name=doc.file_name,
        bet_soni=bet_soni if bet_soni > 0 else 0,
    )

    bet_text = f"{bet_soni} bet" if bet_soni > 0 else "Aniqlanmadi"

    await wait_msg.edit_text(
        "🧾 <b>BUYURTMA INVOICE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📚 Yo'nalish: <b>{yunalish}</b>\n"
        f"📄 Fayl: <b>{doc.file_name}</b>\n"
        f"📊 Hajmi: <b>{bet_text}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Narx: <b>{NARX:,} so'm</b>\n"
        f"⏱ Muddat: <b>{MUDDAT}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Buyurtmani tasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=invoice_kb()
    )

# ───── INVOICE TASDIQLASH → KARTA ─────
@router.callback_query(F.data == "invoice_tasdiqlash")
async def invoice_tasdiqlash(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = create_order(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        file_id=data["file_id"],
        bet_soni=data.get("bet_soni", 0),
        kategoriya=data.get("yunalish", "—"),
        narx=NARX,
        muddat=MUDDAT
    )
    await state.update_data(order_id=order_id)
    await state.set_state(OrderState.chek_kutish)

    await callback.message.edit_text(
        "💳 <b>To'lov rekvizitlari:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🏦 Karta: <code>{KARTA_RAQAM}</code>\n"
        f"👤 Egasi: <b>{KARTA_EGASI}</b>\n"
        f"💰 Summa: <b>{NARX:,} so'm</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Buyurtma: #<b>{order_id}</b>\n\n"
        "To'lovni amalga oshirib, <b>chek rasmini</b> shu yerga yuboring 📸",
        parse_mode="HTML"
    )
    await callback.answer()

# ───── INVOICE BEKOR ─────
@router.callback_query(F.data == "invoice_bekor")
async def invoice_bekor(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Buyurtma bekor qilindi.\n\nQayta buyurtma berish uchun menyudan foydalaning."
    )
    await callback.answer()

# ───── CHEK QABUL → ADMIN + KANAL ─────
@router.message(OrderState.chek_kutish, F.photo)
async def chek_qabul(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get("order_id")
    order = get_order(order_id)

    if not order:
        await message.answer("❌ Buyurtma topilmadi.")
        await state.clear()
        return

    chek_photo_id = message.photo[-1].file_id

    # Adminga chek + fayl
    await bot.send_photo(
        ADMIN_ID,
        photo=chek_photo_id,
        caption=(
            f"🧾 <b>To'lov cheki — Buyurtma #{order_id}</b>\n\n"
            f"👤 @{order['username'] or 'Nomaʼlum'}\n"
            f"🆔 <code>{order['user_id']}</code>\n"
            f"📚 Yo'nalish: {order['kategoriya']}\n"
            f"📄 Bet soni: {order['bet_soni']}\n"
            f"💰 Summa: {NARX:,} so'm"
        ),
        parse_mode="HTML",
        reply_markup=admin_tasdiqlash_kb(order_id)
    )
    await bot.send_document(
        ADMIN_ID,
        document=order["file_id"],
        caption=f"📎 Malaka talabi — #{order_id} | {order['kategoriya']}"
    )

    # Kanalga arxivlash
    await kanal_yangi_buyurtma(bot, order_id, order, chek_photo_id)

    update_order_status(order_id, "chek_yuborildi")
    await state.clear()

    await message.answer(
        f"✅ <b>Chekingiz qabul qilindi!</b>\n\n"
        f"📌 Buyurtma: #<b>{order_id}</b>\n"
        f"⏳ Admin tekshirib tasdiqlaydi.\n\n"
        f"O'quv reja tayyor bo'lgach sizga yuboriladi 📨",
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
        "kutilmoqda": "🟡", "chek_yuborildi": "🔵",
        "tasdiqlandi": "🟢", "rad_etildi": "🔴", "bajarildi": "✅"
    }
    text = "📋 <b>Sizning buyurtmalaringiz:</b>\n\n"
    for order_id, order in list(orders.items())[-5:]:
        emoji = status_emoji.get(order["status"], "⚪")
        text += (
            f"{emoji} #{order_id} | {order['kategoriya']}\n"
            f"   💰 {NARX:,} so'm | 📅 {order['created_at']}\n"
            f"   Holat: {order['status']}\n\n"
        )
    await message.answer(text, parse_mode="HTML")

# ───── XATO INPUTLAR ─────
@router.message(OrderState.yunalish_kutish)
async def yunalish_xato(message: Message):
    await message.answer("✏️ Iltimos, yo'nalish nomini <b>matn</b> shaklida yuboring!", parse_mode="HTML")

@router.message(OrderState.fayl_kutish)
async def fayl_xato(message: Message):
    await message.answer("📎 Iltimos, faqat <b>PDF fayl</b> yuboring!", parse_mode="HTML")

@router.message(OrderState.chek_kutish)
async def chek_xato(message: Message):
    await message.answer("📸 Iltimos, to'lov cheki <b>rasmini</b> yuboring!", parse_mode="HTML")
