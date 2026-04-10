"""
Kanal arxiv yordamchi funksiyalari.
Barcha muhim voqealar kanalga yuboriladi.
"""
import logging
from aiogram import Bot
from config import KANAL_ID, NARX, MUDDAT

logger = logging.getLogger(__name__)

async def kanal_yangi_buyurtma(bot: Bot, order_id: str, order: dict, chek_photo_id: str):
    """
    Yangi buyurtma kelganda kanalga yuboradi:
    - Buyurtma ma'lumotlari (chek rasmi bilan)
    - Malaka talabi PDF fayli
    """
    if not KANAL_ID:
        return
    try:
        # 1. Chek rasmi + ma'lumotlar
        await bot.send_photo(
            KANAL_ID,
            photo=chek_photo_id,
            caption=(
                f"🆕 <b>YANGI BUYURTMA #{order_id}</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 @{order['username'] or 'Nomaʼlum'}\n"
                f"🆔 <code>{order['user_id']}</code>\n"
                f"📚 Yo'nalish: <b>{order['kategoriya']}</b>\n"
                f"📄 Bet soni: {order['bet_soni']}\n"
                f"💰 Summa: <b>{NARX:,} so'm</b>\n"
                f"📅 Sana: {order['created_at']}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 Status: <b>Chek yuborildi</b>"
            ),
            parse_mode="HTML"
        )
        # 2. Malaka talabi fayli
        await bot.send_document(
            KANAL_ID,
            document=order["file_id"],
            caption=f"📎 Malaka talabi — #{order_id} | {order['kategoriya']}"
        )
    except Exception as e:
        logger.error(f"Kanalga yangi buyurtma yuborishda xato: {e}")


async def kanal_tasdiqlandi(bot: Bot, order_id: str, order: dict):
    """To'lov tasdiqlanganda kanalga xabar"""
    if not KANAL_ID:
        return
    try:
        await bot.send_message(
            KANAL_ID,
            f"✅ <b>TASDIQLANDI #{order_id}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 @{order['username'] or 'Nomaʼlum'}\n"
            f"📚 Yo'nalish: <b>{order['kategoriya']}</b>\n"
            f"💰 {NARX:,} so'm\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Status: <b>✅ To'lov tasdiqlandi</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Kanalga tasdiqlash yuborishda xato: {e}")


async def kanal_rad_etildi(bot: Bot, order_id: str, order: dict):
    """To'lov rad etilganda kanalga xabar"""
    if not KANAL_ID:
        return
    try:
        await bot.send_message(
            KANAL_ID,
            f"❌ <b>RAD ETILDI #{order_id}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 @{order['username'] or 'Nomaʼlum'}\n"
            f"📚 Yo'nalish: <b>{order['kategoriya']}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Status: <b>❌ Rad etildi</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Kanalga rad etish yuborishda xato: {e}")


async def kanal_bajarildi(bot: Bot, order_id: str, order: dict, result_file_id: str):
    """
    O'quv reja tayyor bo'lganda kanalga yuboradi:
    - Bajarildi xabari + o'quv reja fayli
    """
    if not KANAL_ID:
        return
    try:
        await bot.send_document(
            KANAL_ID,
            document=result_file_id,
            caption=(
                f"🎉 <b>BAJARILDI #{order_id}</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 @{order['username'] or 'Nomaʼlum'}\n"
                f"📚 Yo'nalish: <b>{order['kategoriya']}</b>\n"
                f"💰 {NARX:,} so'm\n"
                f"📅 {order['created_at']}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 Status: <b>✅ Bajarildi</b>"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Kanalga bajarildi yuborishda xato: {e}")
