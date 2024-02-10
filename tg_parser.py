from telethon import TelegramClient, events
from config import my_chat_id


def telegram_parser(session, api_id, api_hash, telegram_channels, check_ban_words=None, parse_func=None,
                    send_message_func=None, loop=None):
    client = TelegramClient(session, api_id, api_hash, system_version="4.16.30-vxCUSTOM", loop=loop)
    client.start()

    @client.on(events.NewMessage(chats=telegram_channels))
    async def my_event_handler(event):
        print(type(event.raw_text))
        one_line_text = event.raw_text.replace("\n", " ")
        print(one_line_text)
        post = await parse_func(one_line_text)
        await client.send_message(my_chat_id, post)

    return client
