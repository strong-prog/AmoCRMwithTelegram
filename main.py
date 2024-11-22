import logging
import requests
import aioschedule
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, timedelta
from config import AMOCRM_TOKEN, AMOCRM_BASE_URL, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

async def get_revenue_data():
    """Получение данных из AmoCRM"""
    url = f"{AMOCRM_BASE_URL}/api/v4/leads"
    headers = {
        "Authorization": f"Bearer {AMOCRM_TOKEN}"
    }

    # Вычисляем временные метки
    start_date = int((datetime.now() - timedelta(days=1)).timestamp())
    end_date = int(datetime.now().timestamp())

    # Параметры для фильтрации
    params = {
        "filter[closed_at][from]": start_date,
        "filter[closed_at][to]": end_date,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        logging.info(f"Статус ответа: {response.status_code}")
        logging.info(f"Тело ответа: {response.text}")
        if response.status_code == 200:
            data = response.json()
            managers_revenue = {}
            for lead in data["_embedded"]["leads"]:
                manager = lead["responsible_user_id"]
                revenue = lead.get("price", 0)
                managers_revenue[manager] = managers_revenue.get(manager, 0) + revenue
            return managers_revenue
        else:
            logging.error(f"Ошибка AmoCRM: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Ошибка при запросе к AmoCRM: {e}")
        return None

async def send_report():
    """Отправка отчета в Telegram"""
    revenue_data = await get_revenue_data()
    if revenue_data:
        message = "Ежедневный отчет по выручке:\n"
        for manager_id, revenue in revenue_data.items():
            message += f"Менеджер {manager_id}: {revenue} руб.\n"
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    else:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Не удалось получить данные для отчета.")

async def scheduler():
    """Настройка расписания"""
    aioschedule.every().day.at("09:00").do(send_report)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

@dp.message(Command(commands=["start", "help"]))
async def send_welcome(message: Message):
    """Обработка команды /start и /help"""
    await message.reply("Привет! Этот бот ежедневно отправляет отчеты по выручке из AmoCRM. "
                        "Для получения отчета используй команду /send_report")

@dp.message(Command(commands=["send_report"]))
async def manual_report(message: Message):
    """Ручная отправка отчета через команду"""
    await send_report()
    await message.reply("Отчет отправлен!")

async def main():
    """Главная функция для запуска бота"""
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

