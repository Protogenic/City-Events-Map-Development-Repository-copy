import json
from datetime import datetime
from telethon import TelegramClient, events
from internal.function import response_to_server, filter_func, SummarizeAiFunc


def telegram_grabber(session, api_id, api_hash, loop=None, tg_channels=None):
    client = TelegramClient(session, api_id, api_hash, system_version="4.16.30-vxCUSTOM", loop=loop)
    client.start()

    @client.on(events.NewMessage(chats=tg_channels))
    async def check_events(event):
        new_text = event.raw_text.replace("\n", "")
        if not (filter_func(new_text)):
            print("Не прошло")
            return client
        message_link = f"https://t.me/{event.chat.username}/{event.id}"
        post = await SummarizeAiFunc(new_text)
        if post == "":
            return client
        data = json.loads(post)
        data['url'] = message_link
        data['img'] = None
        time = datetime.now().strftime("%Y-%m-%d")
        data['news_date'] = time
        blob = None
        if event.message.photo:
            blob = await event.download_media(bytes)
        print(blob)
        print(data)
        # response_to_server(data)
        ##send_message_func(data)

    return client
