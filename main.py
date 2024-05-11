from telethon import TelegramClient, events
import asyncio

api_id = 'ID'
api_hash = 'HASH'
phone_number = '+995555555555'

excluded_users = set()
baned_users = 0

channels = []
ban_words = ["Ban word"]

message_count = 0
start_time = 0

target_chat_id = -1000000000000 # Where to send messages
target_chat_stats = 000000000 # Admin's chat
target_chat_ban_id = -0000000000 # Messages for keeping a ban

client = TelegramClient(phone_number, api_id, api_hash)


@client.on(events.NewMessage(chats=channels))
async def handler(event):
    global message_count
    
    if event.sender_id in excluded_users:
        print(f"Сообщение от исключенного пользователя. {event.sender_id}")
        return

    if target_chat_id is None:
        print("Целевой чат не найден.")
        return


@client.on(events.NewMessage(chats=channels))
async def word_filter_handler(event): 
    global message_count
    
    try:
        message_text = event.message.text.lower()
        for word in ban_words:
            if word in message_text:
                print("Найдено запрещенное слово:", word)
                await client.send_message(target_chat_ban_id, event.message)
                return
            else:
                if event.sender_id not in excluded_users:
                    print(f"Forward new message......")
                    message_count += 1
                    original_message_link = f"https://t.me/{event.chat.username}/{event.id}"
                    user_info = f"ID пользователя: {event.sender_id}\nИмя пользователя: {event.sender.first_name}\nНомер телефона: {event.sender.phone}"
                    forward_text = f"Ссылка на сообщение: {original_message_link}\nДанные пользователя:\n{user_info}\n\n{event.message.text}"
                    await client.send_message(target_chat_id, forward_text)
                    return
    except Exception as e:
        print("Ошибка обработки сообщения:", e)



@client.on(events.NewMessage(chats=target_chat_ban_id))
async def add_excluded_users(event):
    global baned_users, excluded_users
    if event.message.forward and event.message.forward.sender_id not in excluded_users:
        print("New ban: ", event.message.forward.sender_id)
        excluded_users.add(event.message.forward.sender_id)
        baned_users += 1


async def main():
    global baned_users, excluded_users
    await client.start()
    
    if target_chat_ban_id:
        async for message in client.iter_messages(target_chat_ban_id, reverse=True):
            if message.forward:
                excluded_users.add(message.forward.sender_id)
            baned_users += 1

        print(excluded_users)
    else:
        print("Не удалось найти целевой чат для бана.")

    async for dialog in client.iter_dialogs():
        channels.append(dialog.id)
    
    if target_chat_ban_id in channels:
        channels.remove(target_chat_ban_id)
    
    if target_chat_id is None:
        return

    asyncio.create_task(notify_working())
    asyncio.create_task(notify_admin())
    
    await client.run_until_disconnected()

async def notify_working():
    while True:
        print("Script work...")
        await asyncio.sleep(5)
        
async def notify_admin():
    while True:
        await asyncio.sleep(3600)
        await client.send_message(target_chat_stats, "Скрипт переслал за эту сессию - " + str(message_count) + " сообщений.\nBanned - " + str(len(excluded_users)))


client.loop.run_until_complete(main())
