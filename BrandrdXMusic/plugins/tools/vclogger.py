import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import Message

from BrandrdXMusic import app
from BrandrdXMusic.utils.database import (
    get_assistant,
    is_vclogger_on,
    vclogger_off,
    vclogger_on,
)

links = {}


@app.on_message(filters.command(["vclogger"]) & filters.group & ~filters.channel)
async def vclogger_cmd(_, message: Message):
    usage = (
        "<b>ᴠᴄ ʟᴏɢɢᴇʀ</b>\n\n"
        "<b>ᴜsᴀɢᴇ :</b>\n"
        "» <code>/vclogger</code> ➜ ᴛᴏ ᴄʜᴇᴄᴋ ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs\n"
        "» <code>/vclogger on</code> │ <code>enable</code> │ <code>yes</code> │ <code>enabled</code> ➜ ᴇɴᴀʙʟᴇ\n"
        "» <code>/vclogger off</code> │ <code>disable</code> │ <code>no</code> │ <code>disabled</code> ➜ ᴅɪsᴀʙʟᴇ"
    )
    if len(message.command) < 2:
        state = await is_vclogger_on(message.chat.id)
        status = "ᴇɴᴀʙʟᴇᴅ ✅" if state else "ᴅɪsᴀʙʟᴇᴅ ❌"
        return await message.reply_text(f"{usage}\n\n<b>sᴛᴀᴛᴜs :</b> {status}")
    state = message.text.split(None, 1)[1].strip().lower()
    if state in ("on", "enable", "enabled", "yes"):
        await vclogger_on(message.chat.id)
        await message.reply_text(
            "» ᴠᴄ ʟᴏɢɢᴇʀ ᴇɴᴀʙʟᴇᴅ ✅\n\n"
            "ɴᴏᴡ ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ɪɴ ᴛʜɪs ᴄʜᴀᴛ\n"
            "ᴡʜᴇɴᴇᴠᴇʀ ᴀɴʏᴏɴᴇ ᴊᴏɪɴs ᴏʀ ʟᴇᴀᴠᴇs ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ."
        )
    elif state in ("off", "disable", "disabled", "no"):
        await vclogger_off(message.chat.id)
        await message.reply_text("» ᴠᴄ ʟᴏɢɢᴇʀ ᴅɪsᴀʙʟᴇᴅ ❌")
    else:
        await message.reply_text(usage)


@app.on_message(filters.command(["invite", "invitelogger", "vcinvite"]) & filters.group)
async def invite_assistant(client, message: Message):
    chat_id = message.chat.id
    userbot = await get_assistant(chat_id)

    mystic = await message.reply_text(
        "**ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...\n\nɪɴᴠɪᴛɪɴɢ ᴀssɪsᴛᴀɴᴛ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ...**"
    )

    # Check if assistant is already a member
    is_member = True
    try:
        get = await client.get_chat_member(chat_id, userbot.id)
        if get.status in (
            ChatMemberStatus.BANNED,
            ChatMemberStatus.KICKED,
            ChatMemberStatus.RESTRICTED,
        ):
            return await mystic.edit_text(
                "**ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴɴᴇᴅ ᴏʀ ᴋɪᴄᴋᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ** ❌\n\n"
                f"<b>ɪᴅ :</b> <code>{userbot.id}</code>\n"
                f"<b>ɴᴀᴍᴇ :</b> {userbot.name}"
            )
        if get.status == ChatMemberStatus.LEFT:
            is_member = False
    except UserNotParticipant:
        is_member = False
    except ChatAdminRequired:
        return await mystic.edit_text(
            "**ʙᴏᴛ ʀᴇǫᴜɪʀᴇs ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ɪɴᴠɪᴛᴇ ᴀssɪsᴛᴀɴᴛ** ❌"
        )

    if is_member:
        return await mystic.edit_text(
            f"**{userbot.name} ɪs ᴀʟʀᴇᴀᴅʏ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ᴄʜᴀᴛ** ✅\n\n"
            "ᴠᴄ ʟᴏɢɢᴇʀ ɪs ʀᴇᴀᴅʏ ᴛᴏ ᴜsᴇ."
        )

    # Assistant not in chat - invite via link
    if chat_id in links:
        invitelink = links[chat_id]
    else:
        if message.chat.username:
            invitelink = message.chat.username
            try:
                await userbot.resolve_peer(invitelink)
            except:
                pass
        else:
            try:
                invitelink = await client.export_chat_invite_link(
                    chat_id,
                )
            except ChatAdminRequired:
                return await mystic.edit_text(
                    "**ʙᴏᴛ ʀᴇǫᴜɪʀᴇs ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ɪɴᴠɪᴛᴇ ᴀssɪsᴛᴀɴᴛ** ❌"
                )
            except Exception as e:
                return await mystic.edit_text(
                    f"**ғᴀɪʟᴇᴅ ᴛᴏ ɪɴᴠɪᴛᴇ ᴀssɪsᴛᴀɴᴛ :** <code>{type(e).__name__}</code>"
                )

    if invitelink.startswith("https://t.me/+"):
        invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
    try:
        await asyncio.sleep(1)
        await userbot.join_chat(invitelink)
    except InviteRequestSent:
        try:
            await client.approve_chat_join_request(
                chat_id,
                userbot.id,
            )
        except Exception as e:
            return await mystic.edit_text(
                f"**ғᴀɪʟᴇᴅ ᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ :** <code>{type(e).__name__}</code>"
            )
        await asyncio.sleep(3)
    except UserAlreadyParticipant:
        pass
    except Exception as e:
        return await mystic.edit_text(
            f"**ғᴀɪʟᴇᴅ ᴛᴏ ɪɴᴠɪᴛᴇ ᴀssɪsᴛᴀɴᴛ :** <code>{type(e).__name__}</code>"
        )

    links[chat_id] = invitelink
    try:
        await userbot.resolve_peer(chat_id)
    except:
        pass

    await mystic.edit_text(
        f"**{userbot.name} ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴄʜᴀᴛ** 🥳\n\n"
        "ᴠᴄ ʟᴏɢɢᴇʀ ɪs ɴᴏᴡ ʀᴇᴀᴅʏ ᴛᴏ ᴜsᴇ ɪɴ ᴛʜɪs ᴄʜᴀᴛ."
    )
