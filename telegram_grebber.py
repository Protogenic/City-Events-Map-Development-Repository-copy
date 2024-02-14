import asyncio

from telethon import TelegramClient, events


def telegram_grabber(session, api_id, api_hash, telegram_channels=None, check_ban_words=None, parsing_func=None,
                     send_message_func=None, loop=None):
    client = TelegramClient(session, api_id, api_hash, system_version="4.16.30-vxCUSTOM", loop=loop)
    client.start()

    @client.on(events.NewMessage(chats=telegram_channels))
    async def check_events(event):
        new_text = event.raw_text.replace("\n", "")
        if not (check_ban_words(new_text)):
            print("Не прошло")
            return
        message_link = f"https://t.me/{event.chat.username}/{event.id}"
        post = await parsing_func(new_text)
        post += '\n4)Источник: ' + message_link
        photo_path = ""
        if event.photo:
            photo = event.photo
            photo_path = await client.download_media(photo, file="downloaded_image.jpg")
        await send_message_func(post, photo_path)
    return client
