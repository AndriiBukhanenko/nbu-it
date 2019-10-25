from utils import *


async def start(message: types.Message, state: FSMContext):

    await UserStates.select_type.set()

    reply_markup = InlineKeyboardMarkup(row_width=1)
    async with state.proxy() as data:
        data["object_type"] = "3"
        btn1 = InlineKeyboardButton(text="Отделение банка", callback_data="type-1")
        btn2 = InlineKeyboardButton(text="Банкомат", callback_data="type-2")
        btn3 = InlineKeyboardButton(text="Обменник", callback_data="type-3")
        reply_markup.add(btn1, btn2, btn3)

        await bot.send_message(message.from_user.id,
                               "Я помогу найти ближайшие обьекты. \r\nЧто ты хочешь найти?", reply_markup=reply_markup)


async def get_name(callback_query: types.CallbackQuery, state: FSMContext):

    await UserStates.select_name.set()

    async with state.proxy() as data:
        object_type = callback_query.data.split("-")
        data["object_type"] = object_type[1]
        message_text = 'Напишите названия банка'
        reply_markup = InlineKeyboardMarkup(row_width=1)
        btn = InlineKeyboardButton(text="Любой", callback_data="all")
        btn1 = InlineKeyboardButton(text="Назад", callback_data="back")

        reply_markup.add(btn, btn1)

        if object_type[1] == '1' or object_type[1] == '2':
            await bot.send_message(callback_query.from_user.id, message_text, reply_markup=reply_markup)
        else:
            await get_location(callback_query, state)

async def get_location(message: types.Message, state: FSMContext):

    await UserStates.get_location.set()

    async with state.proxy() as data:
        object_type = data["object_type"]

        if (object_type == '1' or object_type == '2') and "text" in message :
            data["object_name"] = message.text
        elif object_type == "3" or "data" in message:
            data["object_name"] = ""

        reply_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn1 = KeyboardButton(text="Отправить геолокацию", request_location=True)
        reply_markup.add(btn1)

        await bot.send_message(message.from_user.id, "Принято, отправьте Вашу локацию", reply_markup=reply_markup)


async def show_result(message: types.Message, state: FSMContext):

    await UserStates.show_result.set()

    async with state.proxy() as data:
        object_name = ""
        object_type = data["object_type"]
        place_type = ""

        if object_type == '1':
            object_name = data["object_name"]
            place_type = "Отделения банка"

        elif object_type == '2':
            object_name = data["object_name"]
            place_type = "банкомат"

        else:
            place_type = "Обмен валют"

        google_service = Google_finder()

        result = google_service.find_location(message.location.latitude, message.location.longitude, place_type, object_name)
        data["result"] = result
        message_text = 'Ближе всего к Вам:\r\n'
        counter = 1
        reply_markup = InlineKeyboardMarkup(row_width=1)
        for item in result:
            name = item["Name"].split(": ")
            adr = item["Address"]
            distance = item["Distanse"]
            message_text += f"{counter}. {name[1]}, {adr}, {distance}\r\n"
            btn = InlineKeyboardButton(text=f"Геолокация - {counter}", callback_data=f"location-{counter}")
            reply_markup.add(btn)
            counter += 1
            if counter > 5:
                break

        message_text1= "Выберите нужный адресс и я пришлю карту"
        btn1 = InlineKeyboardButton(text="Искать заново", callback_data="back")
        reply_markup.add(btn1)

        reply_markup1 = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn_back = KeyboardButton(text="Искать заново")
        reply_markup1.add(btn_back)
        # bot.edit_message_reply_markup(message.from_user.id, (message.message_id - 1), (message.message_id - 1), reply_markup=reply_markup1)
        await bot.send_message(chat_id=message.from_user.id, text=message_text, reply_markup=reply_markup1)
        await bot.send_message(chat_id=message.from_user.id, text=message_text1, reply_markup=reply_markup)


async def send_location(callback_query: types.CallbackQuery, state: FSMContext):

    await UserStates.select_name.set()

    async with state.proxy() as data:
        location_id = callback_query.data.split("-")[1]

        result = data["result"]
        selected_location = result[int(location_id)]
        reply_markup = InlineKeyboardMarkup(row_width=1)
        btn = InlineKeyboardButton(text="Искать заново", callback_data="back")
        reply_markup.add(btn)

        await bot.send_location(callback_query.from_user.id, latitude=selected_location["lat"],
                                longitude=selected_location["lng"],
                                reply_markup=reply_markup)