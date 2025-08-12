from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import random
import logging
import pickle
import os

logging.basicConfig(filename='/app/bot.log', level=logging.INFO)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def login_freecash(email, password):
    try:
        driver.get("https://freecash.com/login")
        sleep(random.uniform(2, 5))
        driver.find_element("name", "email").send_keys(email)
        driver.find_element("name", "password").send_keys(password)
        driver.find_element("xpath", "//button[@type='submit']").click()
        sleep(random.uniform(5, 8))
        pickle.dump(driver.get_cookies(), open(f"/app/cookies.pkl", "wb"))
        logging.info("Login bem-sucedido")
    except Exception as e:
        logging.error(f"Erro no login: {e}")

def monitor_surveys():
    try:
        driver.get("https://freecash.com")
        if os.path.exists("/app/cookies.pkl"):
            for cookie in pickle.load(open("/app/cookies.pkl", "rb")):
                driver.add_cookie(cookie)
        driver.get("https://freecash.com/surveys")
        sleep(random.uniform(3, 7))
        surveys = driver.find_elements("xpath", "//div[@class='survey-item']")
        for survey in surveys:
            try:
                reward = survey.find_element("xpath", ".//span[@class='reward']").text
                if float(reward.replace('$', '')) >= 0.5:
                    survey.find_element("xpath", ".//button[@class='start-survey']").click()
                    sleep(random.uniform(5, 10))
                    options = driver.find_elements("xpath", "//input[@type='radio']")
                    if options:
                        random.choice(options).click()
                        driver.find_element("xpath", "//button[@type='submit']").click()
                        sleep(random.uniform(2, 5))
                        logging.info(f"Pesquisa completada: {reward}")
            except:
                continue
        return len(surveys)
    except Exception as e:
        logging.error(f"Erro ao monitorar: {e}")
        return 0

if __name__ == "__main__":
    email = "SEU_EMAIL_AQUI"
    password = "SUA_SENHA_AQUI"
    login_freecash(email, password)
    while True:
        surveys_found = monitor_surveys()
        logging.info(f"{surveys_found} pesquisas encontradas")
        sleep(random.uniform(300, 600))
