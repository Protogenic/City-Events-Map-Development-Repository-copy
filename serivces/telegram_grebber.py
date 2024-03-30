import base64
import json
from datetime import datetime
from telethon import TelegramClient, events
from internal.function import response_to_server, filter_func, SummarizeAiFunc, convertImageToDataUri


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
        time = datetime.now().strftime("%d-%m-%Y%H-%M-%S")
        path = f"images/img+{time}"
        if event.message.photo:
            await event.download_media(path)
        imt = ""
        with open(path+".jpg", "rb") as file:
            image_data = file.read()
            img = base64.b64encode(image_data).decode('utf-8')
        data['img'] = img
        print(data)
       ## response_to_server(data)
        ##send_message_func(data)

    return client
