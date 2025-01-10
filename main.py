from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from back import get_day_weather, temperature_graph, get_week_weather
from bd_lg import is_user_registered, register_user, get_user_info, set_operation, get_operations
import asyncio
FIRST_NAME, LAST_NAME, MAIN_TOWN = range(3)
CNT, CITY = range(2)
api_key = "4f03e9067c13e35da1032789ecd08df6"

# Функция для открытия главного меню
async def open_message(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    # Определяем пользователя и chat_id
    if hasattr(update_or_query, "message") and update_or_query.message:  # Обычное сообщение
        user = update_or_query.message.from_user
        chat_id = update_or_query.message.chat.id
    elif hasattr(update_or_query, "from_user") and hasattr(update_or_query, "message"):  # Нажатие кнопки
        user = update_or_query.from_user
        chat_id = update_or_query.message.chat.id
    else:
        raise ValueError("Неподходящий объект: нет message или from_user.")

    # Получаем username
    tg_name = user.username if user.username else None
    print(tg_name)
    # Проверяем, зарегистрирован ли пользователь
    if is_user_registered(tg_name) or tg_name == 'GeoWeather1_bot':
        keyboard = [
            [InlineKeyboardButton(text="Профиль", callback_data='1')],
            [InlineKeyboardButton(text="Погода", callback_data='2')],
            [InlineKeyboardButton(text="История", callback_data='3')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем главное меню
        await context.bot.send_message(
            chat_id=chat_id,
            text='Приветствую! Выберите команду:',
            reply_markup=reply_markup
        )
    else:
        return await start_registration(update_or_query, context)




# Функция для начала регистрации
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Для начала регистрации введите ваше имя:")
    return FIRST_NAME

# Получение имени
async def get_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["first_name"] = update.message.text
    await update.message.reply_text("Отлично! Теперь введите вашу фамилию:")
    return LAST_NAME

# Получение фамилии
async def get_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_name"] = update.message.text
    await update.message.reply_text("Напишите город, где вы проживаете:")
    return MAIN_TOWN

# Получение города и завершение регистрации
async def get_main_town_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text="В меню", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data["main_town"] = update.message.text
    tg_name = update.effective_user.username
    first_name = context.user_data["first_name"]
    last_name = context.user_data["last_name"]
    main_town = context.user_data["main_town"]

    # Регистрация пользователя в базе данных
    register_user(first_name, last_name, tg_name, main_town)

    await update.message.reply_text(
        f"Регистрация завершена!\nИмя: {first_name}\nФамилия: {last_name}\nГород: {main_town}.",
        reply_markup= reply_markup
    )
    return ConversationHandler.END

async def open_message_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query  # Работаем с CallbackQuery
    await query.answer()  # Уведомляем Telegram, что callback обработан

    if query.data == '1':  # Профиль
        tg_name = query.from_user.username
        user_inf = get_user_info(tg_name)

        if user_inf:
            keyboard = [[InlineKeyboardButton(text="Назад", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text=f"👤 **Ваше имя**: {user_inf[0][1]}\n"
                     f"🧾 **Ваша фамилия**: {user_inf[0][2]}\n"
                     f"🏷️ **Ваш ник**: {user_inf[0][3]}\n"
                     f"🌍 **Ваш город**: {user_inf[0][4]}",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                text="Информация о пользователе не найдена.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="Назад", callback_data='back')]
                ])
            )
    elif query.data == 'back':  # Назад
        await open_message(query, context)
    elif query.data == '2':  # Погода
        await start_weather(query, context)
    elif query.data == '3':  # История
        tg_name = query.from_user.username
        user_hist = get_operations(tg_name)
        keyboard = [[InlineKeyboardButton(text="Назад", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        k = 0
        message = ''
        for item in user_hist:
            k+=1
            message += f"🔢 Операция {k}\n\n🌍 Город: {item[0]}\n🛠️ Код операции: {item[1]}\n\n"
        await query.edit_message_text(text=message, reply_markup= reply_markup)


async def start_weather(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    print(update_or_query)
    print("Сценарий погоды начат")
    # Определяем chat_id
    if hasattr(update_or_query, "message") and update_or_query.message:  # Это сообщение
        chat_id = update_or_query.message.chat.id
    elif hasattr(update_or_query, "callback_query") and update_or_query.callback_query:  # Это CallbackQuery
        chat_id = update_or_query.callback_query.message.chat.id
    else:
        raise ValueError("Неподходящий объект: ни message, ни callback_query не найдены.")
    # Запрашиваем город
    await context.bot.send_message(
        chat_id=chat_id,
        text="Пожалуйста, введите название города для получения прогноза погоды."
    )
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_city = update.message.text
    context.user_data["city"] = user_city
    await update.message.reply_text(f"Ваш город {user_city}. Сколько дней вас интересует прогноз? (до 7)")
    return CNT  # Возвращаем состояние CNT


async def get_cnt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text="Назад", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        user_cnt = int(update.message.text)
        if user_cnt == 1:
            user_cnt = user_cnt*8
            context.user_data["cnt"] = user_cnt
            user_city = context.user_data['city']
            user_data = get_day_weather(user_city, api_key, user_cnt)
            context.user_data["data"] = get_day_weather(user_city, api_key, user_cnt)
            time = []
            temp_list = []
            feel_temp_list = []
            for item in user_data:
                print(item)
                if type(item) == dict:
                    time.append(item['time'][11:19])
                    temp_list.append(item['temperature'])
                    feel_temp_list.append(item['feels_like'])
                else:
                    raise TypeError
            image_url = temperature_graph(temp_list, feel_temp_list, time)

            response_text = f"🌍 Ваш город: {user_city}\n📅 Дата: {user_data[0]['time'][:-15]}\n🔎 Данные о погоде:\n\n"
            for i in range(len(user_data)):
                if isinstance(user_data[i], dict):
                    response_text += (
                        f"⏰ **Время**: {user_data[i]['time'][11:19]}\n\n"
                        f"🌡️ **Температура**: {user_data[i]['temperature']}°C\n"
                        f"🥶 **Ощущается как**: {user_data[i]['feels_like']}°C\n"
                        f"🌤️ **Описание погоды**: {user_data[i]['weather']}\n"
                        f"🌬️ **Ветер**: {user_data[i]['wind']} м/с\n\n"
                    )


                else:
                    response_text += ""
            set_operation(user_city,'DAY', update.effective_user.username)
        elif user_cnt > 1:
            context.user_data["cnt"] = user_cnt
            user_city = context.user_data['city']
            user_data = get_week_weather(user_city, api_key, user_cnt)
            context.user_data["data"] = get_week_weather(user_city, api_key, user_cnt)
            time = []
            temp_list = []
            feel_temp_list = []
            for item in user_data:
                print(item)
                if type(item) == dict:
                    time.append(item['date'])
                    temp_list.append(item['temp_6am'])
                    feel_temp_list.append(item['temp_6pm'])
                else:
                    raise TypeError
            image_url = temperature_graph(temp_list, feel_temp_list, time)
            response_text = f"😈💥🥀\nВаш город: 🌍 {user_city}\n📅 Промежуток: {user_cnt} дней.\n🔎 Данные о погоде:\n\n"
            for i in range(len(user_data)):
                if isinstance(user_data[i], dict):
                    response_text += (
                        f"📅 **Дата**: {user_data[i]['date']}\n\n"
                        f"🌅 **Данные в 6 утра 6️⃣ : 0️⃣0️⃣:**\n"
                        f"🌡️ Температура: {user_data[i]['temp_6am']}°C\n"
                        f"🌤️ Погода: {user_data[i]['weather_6am']}\n"
                        f"☁️ Облачность: {user_data[i]['clouds_6am']} %\n"
                        f"🌬️ Ветер: {user_data[i]['wind_6am']} м/с\n\n"
                        f"🌇 **Данные в 6 вечера 1️⃣8️⃣ : 0️⃣0️⃣:**\n"
                        f"🌡️ Температура: {user_data[i]['temp_6pm']}°C\n"
                        f"🌤️ Погода: {user_data[i]['weather_6pm']}\n"
                        f"☁️ Облачность: {user_data[i]['clouds_6pm']} %\n"
                        f"🌬️ Ветер: {user_data[i]['wind_6pm']} м/с\n\n"
                    )

                else:
                    response_text += ""
            set_operation(user_city, 'WEEK', update.effective_user.username)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)
        await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число для временного промежутка.")
        return CNT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Разговор отменён.")
    return ConversationHandler.END
def main():
    # Создаём объект приложения
    application = Application.builder().token("7291723270:AAHEDnFAC2HdNX11FfRkgkZnnvqcwvQc8MU").build()


    # ConversationHandler для управления регистрацией
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("start", open_message)],
        states={
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_first_name)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_last_name)],
            MAIN_TOWN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_main_town_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],  # Обработчик команды /cancel
    )
    weather_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_weather, pattern="^2$")],  # Начало с нажатия "Погода"
        states={
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            CNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cnt)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Регистрация обработчиков
    application.add_handler(weather_handler)
    application.add_handler(registration_handler)
    application.add_handler(CommandHandler("start", open_message))
    application.add_handler(registration_handler)
    application.add_handler(CallbackQueryHandler(open_message_buttons)) # Обработчик нажатий кнопок

    # Запускаем бота
    application.run_polling()

# Точка входа
if __name__ == '__main__':
    main()