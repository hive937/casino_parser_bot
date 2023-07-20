from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException,\
    ElementNotInteractableException, NoSuchElementException, \
    StaleElementReferenceException, InvalidSessionIdException, TimeoutException
from urllib3.exceptions import MaxRetryError
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler
from telegram.error import TimedOut
import time

TOKEN = ''
CHAT_ID = ''


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Привет! Я бот для сбора статистики казино.')
    while True:
        parse_casino(update, context)
        time.sleep(2)


refresh_count = 0


def main_page_login(update, context, driver):
    global refresh_count
    try:
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        try:
            element_popup = driver.find_element(By.XPATH, '//*[@id="welcomeButton"]')
            element_popup.click()
            refresh_count = 0

        except NoSuchElementException:
            if refresh_count == 0 or refresh_count == 1:
                driver.refresh()
                refresh_count += 1
                main_page_login(update, context, driver)

            elif refresh_count == 2:
                driver.close()
                driver.quit()
                refresh_count = 0
                parse_casino(update, context)

        time.sleep(2.7)
        response_bigger_less = soup.find_all("div", {"class": "css-1fs4y27 e116526u1"})[11]
        response_bigger_less_text = response_bigger_less.get_text()
        time.sleep(1)

        try:
            element_popup = driver.find_element(By.XPATH, '//*[@id="welcomeButton"]')
            element_popup.click()
            parse_roulette(update, context, driver, response_bigger_less_text)

        except NoSuchElementException:
            parse_roulette(update, context, driver, response_bigger_less_text)

    except AttributeError:
        parse_casino(update, context)

    except TimeoutException:
        driver.close()
        driver.quit()
        parse_casino(update, context)

    except TimedOut:
        driver.close()
        driver.quit()
        parse_casino(update, context)

    except ElementClickInterceptedException:
        element_popup = driver.find_element(By.XPATH, '//*[@id="welcomeButton"]')
        driver.execute_script("arguments[0].scrollIntoView();", element_popup)
        element_popup.click()
        main_page_login(update, context, driver)

    except InvalidSessionIdException:
        driver.close()
        driver.quit()
        parse_casino(update, context)

    except StaleElementReferenceException:
        main_page_login(update, context, driver)

    except IndexError:
        driver.close()
        driver.quit()
        parse_casino(update, context)

    except MaxRetryError:
        driver.quit()
        time.sleep(10)
        parse_casino(update, context)


def parse_roulette(update, context, driver, response_bigger_less_text):
    arr = []
    arr_sum = []
    how_many_to_delete = 6

    try:
        if response_bigger_less_text == 'БББББ':
            context.bot.send_message(chat_id=CHAT_ID, text=f'Внимание! Выпало уже 5 "Больше" подряд!')
        elif response_bigger_less_text == 'МММММ':
            context.bot.send_message(chat_id=CHAT_ID, text=f'Внимание! Выпало уже 5 "Меньше" подряд!')

        driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/main/div[3]/div[1]/div[2]/section[1]/div[2]/div[1]/div/div/li').click()
        driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/main/div[3]/div[1]/div[2]/section[1]/div[1]/nav/ul/li[2]').click()
        time.sleep(1)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        response_even_odd = soup.find_all("div", {"class": "css-1fs4y27 e116526u1"})[11]
        response_even_odd_text = response_even_odd.get_text()
        if response_even_odd_text == 'ЧЧЧЧЧ':
            context.bot.send_message(chat_id=CHAT_ID, text=f'Внимание! Выпало уже 5 "Чётное" подряд!')
        elif response_even_odd_text == 'ННННН':
            context.bot.send_message(chat_id=CHAT_ID, text=f'Внимание! Выпало уже 5 "Нечётное" подряд!')

        response_numbers = soup.find("div", {"class": "css-kla5xq e11a486n3"})
        for i in response_numbers:
            if '<div class="big css-8i5j0k e11a486n2">' in str(i) or '<div class="small css-8i5j0k e11a486n2">' in str(i):
                y = i.find_all("span", {"class": "css-a4m0tb e11a486n1"})
                for n in y:
                    arr.append(n.get_text())
                y = i.find_all("span", {"class": "double css-a4m0tb e11a486n1"})
                for n in y:
                    arr.append(n.get_text())
            elif '<div class="triple big css-8i5j0k e11a486n2">' in str(i) or '<div class="triple small css-8i5j0k e11a486n2">' in str(i):
                y = i.find_all("span", {"class": "triple css-a4m0tb e11a486n1"})
                for n in y:
                    arr.append(n.get_text())

        del arr[-how_many_to_delete:]

        for i in range(1, 6):
            if str(i) not in arr:
                context.bot.send_message(chat_id=CHAT_ID, text=f'Внимание! {i} не падало уже 8 или больше раз!')

        for i in response_numbers:
            y = i.find_all("span", {"class": "css-1dotcu1 e11a486n0"})
            for n in y:
                arr_sum.append(n.get_text())
            y = i.find_all("span", {"class": "css-16mlkca e11a486n0"})
            for n in y:
                arr_sum.append(n.get_text())

        del arr_sum[-how_many_to_delete:]

        if '9' not in arr_sum and '10' not in arr_sum and '11' not in arr_sum and '12' not in arr_sum:
            context.bot.send_message(chat_id=CHAT_ID, text=f'Внимание! 9, 10, 11 и 12 не выпадали уже 4 броска!')

    except ElementNotInteractableException:
        parse_roulette(update, context, driver, response_bigger_less_text)

    except TimedOut:
        driver.close()
        driver.quit()
        parse_casino(update, context)


def parse_casino(update, context):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("headless")
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              chrome_options=chrome_options)

    try:
        driver.get('https://m.1xslot262740.top/ru/casino/')
        time.sleep(1)

        driver.find_element(By.XPATH, '/html/body/div/header/div[2]/section/button[1]').click()
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="fLogin2"]/div[1]/div/div[2]').click()
        time.sleep(1)

        login_input = driver.find_element(By.XPATH, '//*[@id="fLogin2"]/div[1]/div/div[1]/input[1]')
        login_input.send_keys('')
        password_input = driver.find_element(By.XPATH, '//*[@id="uPassword"]')
        password_input.send_keys('')
        time.sleep(1)

        driver.find_element(By.XPATH, '// *[ @ id = "userConButton"]').click()
        time.sleep(2)

        driver.find_element(By.XPATH, '/ html / body / div / header / div[2] / section / button[2]').click()
        time.sleep(2)

        driver.find_element(By.XPATH, '/ html / body / div / section / div / ul / li[2] / a').click()
        time.sleep(1)

        driver.find_element(By.XPATH, '// *[ @ id = "slots"] / section / section[2] / div[2] / button').click()
        time.sleep(1)

        driver.find_element(By.XPATH, "//span[text()='Sic-Bo']").click()
        time.sleep(1)

        element = driver.find_element(By.XPATH, '/html/body/div/div[3]/article/section/section[1]/div[2]/ul/li[3]')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.find_element(By.XPATH, '//*[@id="slots"]/section/section[1]/div[2]/ul/li[3]/div/div[1]/div').click()
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="slots"]/section/section[1]/div[2]/ul/li[3]/div/div[2]/button[2]').click()
        time.sleep(2)

        try:
            element_popup = driver.find_element(By.XPATH, '//*[@id="welcomeButton"]')
            element_popup.click()
            main_page_login(update, context, driver)
        except NoSuchElementException:
            main_page_login(update, context, driver)

        except TimedOut:
            driver.close()
            driver.quit()
            parse_casino(update, context)

        except MaxRetryError:
            driver.quit()
            time.sleep(2)
            parse_casino(update, context)

    except IndexError:
        driver.quit()
        parse_casino(update, context)

    except TimedOut:
        driver.close()
        driver.quit()
        parse_casino(update, context)

    except MaxRetryError:
        driver.quit()
        parse_casino(update, context)

    except ElementClickInterceptedException:
        driver.quit()
        parse_casino(update, context)

    except NoSuchElementException:
        driver.quit()
        parse_casino(update, context)

    except InvalidSessionIdException:
        driver.quit()
        parse_casino(update, context)

    except StaleElementReferenceException:
        main_page_login(update, context, driver)

    except AttributeError:
        driver.quit()
        parse_casino(update, context)

    finally:
        driver.quit()


def main():

    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    updater.start_polling(poll_interval=0.1)
    updater.idle()

if __name__ == '__main__':
    main()
