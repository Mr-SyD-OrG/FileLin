import os
import logging
import random
import asyncio
import pytz, string
from Script import script
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from pyrogram.types import ChatJoinRequest
from urllib.parse import quote_plus
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db, delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user
from info import CHANNELS, ADMINS, FSUB_UNAME, AUTH_CHANNEL, SYD_CHANNEL, URL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, CHNL_LNK, GRP_LNK, REQST_CHANNEL, SUPPORT_CHAT_ID, SUPPORT_CHAT, MAX_B_TN, VERIFY, HOWTOVERIFY, SHORTLINK_API, SHORTLINK_URL, TUTORIAL, IS_TUTORIAL, PREMIUM_USER, PICS, SUBSCRIPTION, REFERAL_PREMEIUM_TIME, REFERAL_COUNT, PREMIUM_AND_REFERAL_MODE
from utils import get_settings, get_size, is_req_subscribed, is_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, get_shortlink, get_tutorial, get_authchannel
from database.connections_mdb import active_connection
# from plugins.pm_filter import ENABLE_SHORTLINK
import re, asyncio, os, sys
import json
from util.file_properties import get_name, get_hash, get_media_file_size

import base64
logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Kolkata"
SYD = ["🎋", "❄️", "🍀", "🎐", "😶‍🌫️", "🤐"]

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    await message.reply(random.choice(SYD))
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[
                    InlineKeyboardButton('☒ Δᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴩ ☒', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('📓 Gᴜɪᴅᴇ 📓', url="https://t.me/{temp.U_NAME}?start=help")
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.GSTART_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
   # await message.reply(".")
    if len(message.command) != 2:
       # await message.reply("jj.")
        buttons = [[
                    InlineKeyboardButton('✲ Uᴩᴅᴀᴛᴇꜱ', url='https://t.me/Bot_cracker'),
                    InlineKeyboardButton('Mᴏᴠɪᴇꜱ ✲', url='https://t.me/Mod_Moviez_X')
                ],[
                    InlineKeyboardButton('⌬ Hᴇʟᴩ ⌬', callback_data='help')
                ], [
                    InlineKeyboardButton('⚝ Oᴡɴᴇʀ', user_id=1733124290),
                    InlineKeyboardButton("Bᴏᴛꜱ ⚝", url="https://t.me/Bot_Cracker/17")
                ],[
                    InlineKeyboardButton('◎ Gʀᴏᴜᴩ ◎', url='https://t.me/+5n7vViwKXJJiMjhl')
                ]]
       
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.B_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        return
        
    if AUTH_CHANNEL:
        try:
            # Fetch subscription statuses once
            fsub, ch1, ch2 = await get_authchannel(client, message)    #is_req_sub = await is_req_subscribed(client, message, AUTH_CHANNEL)
            #is_req_sub2 = await is_req_subscribed(client, message, SYD_CHANNEL)
            is_sub = await is_subscribed(client, message)

            if not (fsub and is_sub):
                try:
                    invite_link, invite_link2 = None, None
                    if ch1:
                        invite_link = await client.create_chat_invite_link(int(ch1), creates_join_request=True)
                    if ch2:
                        invite_link2 = await client.create_chat_invite_link(int(ch2), creates_join_request=True)
                except ChatAdminRequired:
                    logger.error("Make sure Bot is admin in Forcesub channel")
                    return
                
                btn = []

                # Only invite_linkadd buttons if the user is not subscribed
                
                if invite_link:
                    btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ¹⊛", url=invite_link.invite_link)])

                if invite_link2:
                    btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ²⊛", url=invite_link2.invite_link)])
                
                if not is_sub:
                    btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ³⊛", url=f"https://t.me/{FSUB_UNAME}")])
                    
                    
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ ↻", callback_data=f"checksyd#{log_msg.id}")])

                sydback = await client.send_message(
                    chat_id=message.from_user.id,
                    text="<b>Jᴏɪɴ Oᴜʀ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ</b> Aɴᴅ Tʜᴇɴ Cʟɪᴄᴋ Oɴ Tʀʏ Aɢᴀɪɴ Tᴏ Gᴇᴛ Yᴏᴜʀ Rᴇǫᴜᴇꜱᴛᴇᴅ Fɪʟᴇ.",
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=enums.ParseMode.HTML
                )
                await db.store_file_id_if_not_subscribed(message.from_user.id, log_msg.id, sydback.id)
                return
        except Exception as e:
            logger.error(f"Error in subscription check: {e}")
            await client.send_message(chat_id=1733124290, text=f"FORCE  SUB  ERROR ......  CHECK LOGS {e}")

        
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
                    InlineKeyboardButton('✲ Uᴩᴅᴀᴛᴇꜱ', url='https://t.me/Bot_cracker'),
                    InlineKeyboardButton('Mᴏᴠɪᴇꜱ ✲', url='https://t.me/Mod_Moviez_X')
                ],[
                    InlineKeyboardButton('⌬ Hᴇʟᴩ ⌬', callback_data='help')
                ],[
                    InlineKeyboardButton('⚝ Oᴡɴᴇʀ', user_id=1733124290),
                    InlineKeyboardButton('Bᴏᴛꜱ ⚝', url="https://t.me/Bot_Cracker/17")
                ],[
                    InlineKeyboardButton('◎ Gʀᴏᴜᴩ ◎', url='https://t.me/+5n7vViwKXJJiMjhl')
                ]]
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.B_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        return
    

@Client.on_message(filters.private & (filters.document | filters.video))
async def link(client, message):
    try:
        user_id = message.from_user.id
        username = message.from_user.mention
        file_id = message.document.file_id if message.document else message.video.file_id

        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=file_id,
        )

        if AUTH_CHANNEL:
            try:
                # Fetch subscription statuses once
                fsub, ch1, ch2 = await get_authchannel(client, message)    #is_req_sub = await is_req_subscribed(client, message, AUTH_CHANNEL)
                #is_req_sub2 = await is_req_subscribed(client, message, SYD_CHANNEL)
                is_sub = await is_subscribed(client, message)

                if not (fsub and is_sub):
                    try:
                        invite_link, invite_link2 = None, None
                        if ch1:
                            invite_link = await client.create_chat_invite_link(int(ch1), creates_join_request=True)
                        if ch2:
                            invite_link2 = await client.create_chat_invite_link(int(ch2), creates_join_request=True)
                    except ChatAdminRequired:
                        logger.error("Make sure Bot is admin in Forcesub channel")
                        return
                
                    btn = []

                # Only invite_linkadd buttons if the user is not subscribed
                
                    if invite_link:
                        btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ¹⊛", url=invite_link.invite_link)])

                    if invite_link2:
                        btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ²⊛", url=invite_link2.invite_link)])
                
                    if not is_sub:
                        btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ³⊛", url=f"https://t.me/{FSUB_UNAME}")])
                    
                    
                    btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ ↻", callback_data=f"checksyd#{log_msg.id}")])
                    
                    sydback = await client.send_message(
                        chat_id=message.from_user.id,
                        text="<b>Jᴏɪɴ Oᴜʀ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ</b> Aɴᴅ Tʜᴇɴ Cʟɪᴄᴋ Oɴ Tʀʏ Aɢᴀɪɴ Tᴏ Gᴇᴛ Yᴏᴜʀ Rᴇǫᴜᴇꜱᴛᴇᴅ Fɪʟᴇ.",
                        reply_markup=InlineKeyboardMarkup(btn),
                        parse_mode=enums.ParseMode.HTML
                    ) 
                    await db.store_file_id_if_not_subscribed(message.from_user.id, log_msg.id, sydback.id)
                    return
            except Exception as e:
                logger.error(f"Error in subscription check: {e}")
                await client.send_message(chat_id=1733124290, text="FORCE  SUB  ERROR ......  {e}")

        # Send file to log channel
        
        # Prepare file info and links
        file_name = message.document.file_name if message.document else message.video.file_name
        encoded_name = quote_plus(file_name)
        stream = f"{URL}watch/{str(log_msg.id)}/{encoded_name}?hash={get_hash(log_msg)}"
        download = f"{URL}{str(log_msg.id)}/{encoded_name}?hash={get_hash(log_msg)}"

   
        # Prepare buttons
        
        buttons = [[
            InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=download),
            InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=stream)
        ], [
            InlineKeyboardButton('! Sᴜᴩᴩᴏʀᴛ Uꜱ !', url="https://t.me/Mod_Moviez_X")
        ]]

        # Send links to user
        await message.reply_text(
            text=f"<b>Hᴇʀᴇ ɪꜱ ʏᴏᴜʀ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴᴅ ꜱᴛʀᴇᴀᴍ ʟɪɴᴋ:\n\n✧ ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ <code>{stream}</code>\n✧ ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ: <code>{download}</code>\n\n<blockquote>♻️ ᴛʜɪs ʟɪɴᴋ ɪs ᴘᴇʀᴍᴀɴᴇɴᴛ ᴀɴᴅ ᴡᴏɴ'ᴛ ɢᴇᴛs ᴇxᴘɪʀᴇᴅ [ɪɴ ᴄᴀꜱᴇ ɪꜰ ᴇxᴩɪʀᴇᴅ ɢᴇɴᴇʀᴀᴛᴇ ᴀɢᴀɪɴ] ♻️</blockquote></b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

        # Log it
        await log_msg.reply_text(
            text=f"#LinkGenerated\n\nIᴅ : <code>{user_id}</code>\nUꜱᴇʀɴᴀᴍᴇ : {username}\n\nNᴀᴍᴇ : {file_name}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=download),
                InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=stream)
            ]])
        )

    except Exception as e:
        print(e)
        await message.reply_text(f"⚠️ SOMETHING WENT WRONG \n\n{e}\nForward Message To @Syd_XyZ")



@Client.on_callback_query(filters.regex(r"checksyd"))
async def check_subscription_callback(client, query):
    try:
        fsub, ch1, ch2 = await get_authchannel(client, message)    #is_req_sub = await is_req_subscribed(client, message, AUTH_CHANNEL)
        is_sub = await is_subscribed(client, query)
        if not (fsub and is_sub):
            await query.answer("Rᴇqᴜᴇꜱᴛ Tᴏ Jᴏɪɴ ɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ ᴍᴀʜɴ! ᴩʟᴇᴀꜱᴇ... 🥺", show_alert=True)
            return

        file_id = query.data.split("#")[1]
        user_id = query.from_user.id
        doc = await client.get_messages(LOG_CHANNEL, int(file_id))
        file_name = doc.document.file_name if doc.document else doc.video.file_name
        encoded_name = quote_plus(file_name)
        msg_id = doc.id

        stream = f"{URL}watch/{msg_id}/{encoded_name}?hash={get_hash(doc)}"
        download = f"{URL}{msg_id}/{encoded_name}?hash={get_hash(doc)}"

        buttons = [[
            InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=download),
            InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=stream)
        ]]

        await query.message.edit_text(
            text=f"<b>Hᴇʀᴇ ɪꜱ ʏᴏᴜʀ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴᴅ ꜱᴛʀᴇᴀᴍ ʟɪɴᴋ:\n\n✧ ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ <code>{stream}</code>\n✧ ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ: <code>{download}</code>\n\n<blockquote>♻️ ᴛʜɪs ʟɪɴᴋ ɪs ᴘᴇʀᴍᴀɴᴇɴᴛ ᴀɴᴅ ᴡᴏɴ'ᴛ ɢᴇᴛs ᴇxᴘɪʀᴇᴅ [ɪɴ ᴄᴀꜱᴇ ɪꜰ ᴇxᴩɪʀᴇᴅ ɢᴇɴᴇʀᴀᴛᴇ ᴀɢᴀɪɴ] ♻️</blockquote></b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

        # Remove file_id from DB if stored
        

    except Exception as e:
        await query.message.edit_text(f"⚠️ Failed to generate link\n\n{e}")


@Client.on_callback_query(filters.regex("^jrq:") & filters.user(ADMINS))
async def jreq_callback(client, cq):
    action = cq.data.split(":")[1]

    # ---- REMOVE CHANNEL FLOW ----
    if action == "remove":
        ask = await cq.message.reply("📨 Send the **channel ID** you want to remove from all users.")
        await cq.answer()

        try:
            # WAIT FOR ADMIN INPUT
            response = await client.listen(
                chat_id=cq.from_user.id,
                timeout=60
            )
        except TimeoutError:
            await ask.edit("⏳ Timed out. Try again.")
            return

        if not response.text.isdigit():
            return await response.reply("❌ Invalid ID. Only numbers allowed.")

        channel_id = int(response.text)
        modified = await db.remove_channel_from_all_users(channel_id)

        return await response.reply(
            f"✅ Removed `{channel_id}` from **{modified}** users."
        )

    # ---- DELETE ALL ----
    if action == "del_all":
        await db.del_all_join_req()
        await cq.message.reply("🗑️ All join-requests deleted.")
        return await cq.answer("Cleared!")

    if action == "count":
        total = await db.req.count_documents({})
        await cq.message.reply(f"📊 Total join-requests: `{total}`")
        return await cq.answer("Loaded!")

      
@Client.on_message(filters.command("jreq") & filters.user(ADMINS))
async def jreq_menu(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Remove Channel from All Users", callback_data="jrq:remove")],
        [InlineKeyboardButton("❌ Delete ALL Join-Requests", callback_data="jrq:del_all")],
        [InlineKeyboardButton("📊 View Count", callback_data="jrq:count")],
        [InlineKeyboardButton("➕ Add Channel", callback_data="fsyd_add")],
        [InlineKeyboardButton("🗑 Remove One", callback_data="fsyd_remove_one")],
        [InlineKeyboardButton("❌ Clear All", callback_data="fsyd_clear")],
        [InlineKeyboardButton("📄 View List", callback_data="fsyd_view")],
        [InlineKeyboardButton("✖ Close", callback_data="fsyd_close")]
    ])

    await message.reply(
        "**📂 Join-Request Manager**\nSelect an option:",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex("^bot_fsub_back$") & filters.user(ADMINS))
async def fsub_back(client, cb):
    await jreq_menu(client, cb.message)
    await cb.message.delete()

@Client.on_callback_query(filters.regex("^fsud_del_") & filters.user(ADMINS))
async def fsub_delet_one(client, cb):
    chat_id = int(cb.data.split("_")[-1])
    await db.remove_fsub_channel(chat_id)
    modified = await db.remove_channel_from_all_users(chat_id)
    await cb.message.edit_text(f"✅ Removed `{chat_id}`, `{modified}` from force-sub list.")
    

@Client.on_callback_query(filters.regex("^fsyd_") & filters.user(ADMINS))
async def fsub_callacks(client, cb):
    data = cb.data
    if data == "fsyd_close":
        return await cb.message.delete()

    if data == "fsyd_view":
        try:
           channels = await db.get_fsub_list()
        except Exception as e:
            await cb.message.edit_text(e)
        if not channels:
            return await cb.answer("No force-sub channels set", show_alert=True)

        text = "📄 **Force-Sub Channels:**\n\n"
        for ch in channels:
            text += f"`{ch}`\n"

        return await cb.message.edit_text(text)

    if data == "fsyd_clear":
        await db.clear_fsub()
        await db.del_all_join_req()
        return await cb.message.edit_text("✅ Force-sub list cleared.")

    if data == "fsyd_add":
        await cb.message.edit_text(
            "➕ **Send channel ID or forward a channel message**\n\n"
            "Use /cancel to abort."
        )

        try:
            msg = await client.listen(cb.from_user.id, timeout=120)
        except:
            return await cb.message.edit_text("⏳ Timeout.")

        if msg.text and msg.text.lower() == "/cancel":
            return await cb.message.edit_text("❌ Cancelled.")

        if msg.forward_from_chat:
            chat_id = msg.forward_from_chat.id
        else:
            try:
                chat_id = int(msg.text.strip())
            except:
                return await cb.message.edit_text("❌ Invalid channel ID.")

        await db.add_fsub_channel(chat_id)
        return await cb.message.edit_text(f"✅ Added `{chat_id}` to force-sub list.")
    
    if data == "fsyd_remove_one":
        channels = await db.get_fsub_list()
        if not channels:
            return await cb.answer("List is empty", show_alert=True)

        btn = [
            [InlineKeyboardButton(str(ch), callback_data=f"fsud_del_{ch}")]
            for ch in channels
        ]
        btn.append([InlineKeyboardButton("⬅ Back", callback_data="bot_fsub_back")])

        return await cb.message.edit_text(
            "🗑 **Select channel to remove**",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        
@Client.on_message(filters.command("jreq_user") & filters.user(ADMINS))
async def jreq_user_info(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/jreq_user <user_id>`")

    try:
        user_id = int(message.command[1])
    except:
        return await message.reply("❌ Invalid user_id.")

    doc = await db.syd_user(user_id)
    if not doc:
        return await message.reply("❌ No such user in join-req database.")

    channels = doc.get("channels", [])
    count = doc.get("count", 0)
    timestamp = doc.get("time", 0)

    if timestamp:
        from datetime import datetime
        time_text = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    else:
        time_text = "Not set"

    text = (
        f"📌 **User Join-Req Info**\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"📚 **Channels:** `{channels}`\n"
        f"⏱ **Time:** `{time_text}`\n"
        f"🔢 **Count:** `{count}`"
    )

    await message.reply(text)

@Client.on_chat_join_request(filters.chat())
async def join_reqs(client, message: ChatJoinRequest):
    user_id = message.from_user.id
    authchnl = await db.get_fsub_list()
    if message.chat.id not in authchnl:
        return
    try:
        await db.add_join_req(message.from_user.id, message.chat.id)
    except Exception as e:
        await client.send_message(1733124290, e)
    data = await db.get_stored_file_id(message.from_user.id)
    if data:
        file_id = data["file_id"]
        messyd = int(data["mess"])
        is_sub = await is_subscribed(client, message)
        fsub, ch1, ch2 = await get_authchannel(client, message)
        try:
            syd = await client.get_messages(chat_id=message.from_user.id, message_ids=messyd)
        except:
            syd = None
        if not (fsub and is_sub) and syd:
            try:
                invite_link, invite_link2 = None, None
                if ch1:
                    invite_link = await client.create_chat_invite_link(int(ch1), creates_join_request=True)
                if ch2:
                    invite_link2 = await client.create_chat_invite_link(int(ch2), creates_join_request=True)
                btn = []

                if invite_link:
                    btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ¹⊛", url=invite_link.invite_link)])
 
                if invite_link2:
                    btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ²⊛", url=invite_link2.invite_link)])
                
                if not is_sub:
                    btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ³⊛", url=f"https://t.me/{FSUB_UNAME}")])
                  
            
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ ↻", callback_data=f"checksub##{file_id}")])
                
                await syd.edit_text(
                    text="<b>Jᴏɪɴ Oᴜʀ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ</b> Aɴᴅ Tʜᴇɴ Cʟɪᴄᴋ Oɴ Tʀʏ Aɢᴀɪɴ Tᴏ Gᴇᴛ Yᴏᴜʀ Rᴇǫᴜᴇꜱᴛᴇᴅ Fɪʟᴇ.",
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=enums.ParseMode.HTML
                )
                return
            except Exception as e:
                await client.send_message(1733124290, f"{e} Fsub Error ")
        
        doc = await client.get_messages(LOG_CHANNEL, int(file_id))
        file_name = doc.document.file_name if doc.document else doc.video.file_name
        encoded_name = quote_plus(file_name)

        stream = f"{URL}watch/{file_id}/{encoded_name}?hash={get_hash(doc)}"
        download = f"{URL}{file_id}/{encoded_name}?hash={get_hash(doc)}"

        buttons = [[
            InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=download),
            InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=stream)
        ]]

        await client.send_message(
            user_id,
            text=f"<b>Hᴇʀᴇ ɪꜱ ʏᴏᴜʀ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴᴅ ꜱᴛʀᴇᴀᴍ ʟɪɴᴋ:\n\n✧ ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ <code>{stream}</code>\n✧ ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ: <code>{download}</code>\n\n<blockquote>♻️ ᴛʜɪs ʟɪɴᴋ ɪs ᴘᴇʀᴍᴀɴᴇɴᴛ ᴀɴᴅ ᴡᴏɴ'ᴛ ɢᴇᴛs ᴇxᴘɪʀᴇᴅ [ɪɴ ᴄᴀꜱᴇ ɪꜰ ᴇxᴩɪʀᴇᴅ ɢᴇɴᴇʀᴀᴛᴇ ᴀɢᴀɪɴ] ♻️</blockquote></b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        await db.remove_stored_file_id(user_id)
    

@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def del_requests(client, message):
    await db.del_join_req()    
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")
