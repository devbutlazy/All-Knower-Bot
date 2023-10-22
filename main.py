import json
from aiohttp import ClientSession
import openai
from uuid import uuid4
from pyrogram import Client, types, filters, enums
from typing import Union
import asyncio 

premium_users = json.load(open("premium.json", "r"))

# Setup OpenAI API Key
openai.api_key = ""

app = Client(name="", api_id=, 
             api_hash="",
             bot_token="", 
             parse_mode=enums.ParseMode.HTML)  




@app.on_message(filters.command("start"))  # ок
async def start(_: Client, message: types.Message):
    keyboard = [[types.InlineKeyboardButton("❓ About | Про", callback_data='start_chatting')]]
    await message.reply(
        text="🇺🇸 Hello, I am an AI. How may I assist you?\n\n🇺🇦 Привіт, я AI. Як я можу "
             "допомогти вам?",
        reply_markup=types.InlineKeyboardMarkup(keyboard),
        reply_to_message_id=message.id
    )


async def get_donates():
    async with ClientSession(headers={"X-Token": "322273e9a15b2c1a032ac892583d02cf"}) as session:  # правильно?
        async with session.get("https://donatello.to/api/v1/donates") as response:
            text = await response.read()
    if 'content' in json.loads(text):
        return json.loads(text)['content']
    else:
        return -1


async def find_donate(donat_or: Union[str, int], comment: str):
    donates = await get_donates()
    response, author = False, None

    if donates == -1:
        return response, author

    for donate in donates:
        print(donate)
        if (str(donate['clientName']) == str(donat_or) and
                str(donate['message']) == str(comment)):
            response, author = True, str(donat_or)

    return response, author


async def chatbot_response(text):
    response = (await openai.Completion.acreate(
        engine="text-davinci-003",
        prompt=text,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )).get("choices")[0].text
    return f"📕 Answer by All Known\n\n{response}"


@app.on_callback_query()
async def call_back(_: Client, callback: types.CallbackQuery):
    data = callback.data

    if data == "start_chatting":
        # query = callback.callback_query
        keyboard = [[types.InlineKeyboardButton("⬅️ Home | Додому", callback_data='home')]]

        await callback.message.edit_text(
            text="🇺🇸 Hello. I am a bot that can answer all your questions on every language.\nMy knowledge is only "
                 "related till 2021\n\nNow pls write me a question and I'll answer on it.\n\n🇺🇦 Привіт. Я бот, "
                 "який може відповісти на всі ваші запитання на будь-якій мові.\nМої знання є лише до 2021 "
                 "року.\n\nТепер напишіть мені запитання та я відповім на нього.",
            reply_markup=types.InlineKeyboardMarkup(keyboard)
        )

    if data == "home":
        keyboard = [[types.InlineKeyboardButton("❓ About", callback_data='start_chatting')]]

        await callback.message.edit_text(
            text="🇺🇸 Hello, I am an AI. How may I assist you?\n\n🇺🇦 Привіт, я AI. Як я можу допомогти вам?",
            reply_markup=types.InlineKeyboardMarkup(keyboard)
        )
    if data.split("|")[0] == "check_donate":
        print(data.split("|")[0])
        split_d = callback.data.split("|")  # check_donate|{message.from_user.id}|{code}
        user_id, code = str(split_d[1]), split_d[2]
        response, author = await find_donate(donat_or=str(user_id), comment=str(code))
        if response:
            premium_users[callback.from_user.first_name] = str(author)
            json.dump(obj=premium_users, fp=open("premium.json", "w"), indent=4)

            await callback.message.edit_text(
                text=f"🇺🇸 Your premium was activated, thanks for supporting\n\n🇺🇦 Ваш преміум був активований, дякуємо за підтримку",
                reply_markup=None
            )
        else:
            keyboard = [[types.InlineKeyboardButton("🔄 Refresh", callback_data=f"check_donate|{user_id}|{code}")]]
            await callback.message.reply(
                text=f"🇺🇸 Ooops...\nYou haven't payed for the premium, yet?\n\n🇺🇦 Упс...\nВи ще дотепер не заплатили за преміум?",
                reply_markup=types.InlineKeyboardMarkup(keyboard)
            )


@app.on_message(~filters.command("start") & filters.text)
async def openai_call(_: Client, message: types.Message):
    reply_markup = None
    user_id = str(message.from_user.id)
    found = False
    for name, _id in premium_users.items():
        if user_id == _id:
            found = True
            break
        else:
            continue
    if found:
        msg = await message.reply(
            text="⏳ Your request is submiting!\n\n⏳ Ваш запит обробляється!",
            reply_to_message_id=message.id)
        response = await chatbot_response(message.text)
        await msg.delete()
        await message.reply(text=response, reply_markup=reply_markup, reply_to_message_id=message.id)
    else:    
        code = str(uuid4())  # код
        keyboard = [[types.InlineKeyboardButton("💎 Check premium",
                                                callback_data=f"check_donate|{message.from_user.id}|{code}")]]
        await message.reply(
            text="🇺🇸 All Knowner Answers are premium.\n\n💸 Cost: 150₴\n\n📌 To buy premium, go here -> "
                 f"https://donatello.to/allknown\nSend the amount of money (150grn) and in the message box write this "
                 f"code: <b><code>{code}</code></b>, and your donate name should be: <b><code>{user_id}</code></b>\n❗️To copy the codes, just click on them"
                 "\n\n\n🇺🇦 Всі відповіді від All Knowner є платними.\n\n💸 Вартість: 150₴\n\n📌 Щоб купити преміум, перейдіть сюди -> "
                 f"https://donatello.to/allknown\nВідправте суму грошей (150 грн) і в поле повідомлення напишіть "
                 f"код: <b><code>{code}</code></b>, та впишіть це в ім'я донатера: <b><code>{user_id}</code></b>\n❗️Щоб скопіювати коди, про настисніть на них",
            reply_markup=types.InlineKeyboardMarkup(keyboard))




app.run()
print("Bot is ready!")
