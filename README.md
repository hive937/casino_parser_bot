# CasinoParserBot
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat-square&logo=Selenium&logoColor=white)](https://www.selenium.com/)


Бот-парсер для популярного сайта-казино, сделанный на заказ.
Бот позволяет получить заданные комбинации с конкретной рулетки при их выпадении и отсылает уведомление о выпадении в Телеграм бота.

## Подготовка и запуск проекта
### Склонируйте репозиторий:
```
git clone https://github.com/hive937/casino_parser_bot
```
* Установите зависимости
```
pip install -r requirements.txt
```
* Запустите бота
```
python main.py
```

## Для успешной работы проекта
Необходимо подставить в код main2.py:
- В значение TOKEN подставить токен бота, полученный в BotFather
- В значение CHAT_ID подставить id чата, в который будут присылаться уведомления


# Использованные технологии:
- Selenium
- Python-telegram-bot
- BeautifulSoup
- Telegram API

## Автор проекта
Павел Вервейн | [hive937](https://github.com/hive937)
