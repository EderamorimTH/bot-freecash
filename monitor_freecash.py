from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import random
import logging
import pickle
import os

logging.basicConfig(filename='/app/bot.log', level=logging.INFO)

chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Modo headless atualizado
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

def login_freecash(email, password):
    try:
        driver.get("https://freecash.com/login")
        sleep(random.uniform(2, 5))
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        sleep(random.uniform(5, 8))
        pickle.dump(driver.get_cookies(), open(f"/app/cookies.pkl", "wb"))
        logging.info("Login bem-sucedido")
    except Exception as e:
        logging.error(f"Erro no login: {e}")

def monitor_surveys():
    try:
        driver.get("https://freecash.com")
        sleep(2)

        if os.path.exists("/app/cookies.pkl"):
            cookies = pickle.load(open("/app/cookies.pkl", "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)

        driver.get("https://freecash.com/surveys")
        sleep(random.uniform(3, 7))

        surveys = driver.find_elements(By.XPATH, "//div[contains(@class, 'survey-item')]")
        for survey in surveys:
            try:
                reward = survey.find_element(By.XPATH, ".//span[contains(@class, 'reward')]").text
                if float(reward.replace('$', '')) >= 0.5:
                    survey.find_element(By.XPATH, ".//button[contains(@class, 'start-survey')]").click()
                    sleep(random.uniform(5, 10))
                    options = driver.find_elements(By.XPATH, "//input[@type='radio']")
                    if options:
                        random.choice(options).click()
                        driver.find_element(By.XPATH, "//button[@type='submit']").click()
                        sleep(random.uniform(2, 5))
                        logging.info(f"Pesquisa completada: {reward}")
            except:
                continue
        return len(surveys)
    except Exception as e:
        logging.error(f"Erro ao monitorar: {e}")
        return 0

if __name__ == "__main__":
    email = "edert905@gmail.com"
    password = "Mariamiguel1"
    login_freecash(email, password)
    while True:
        surveys_found = monitor_surveys()
        logging.info(f"{surveys_found} pesquisas encontradas")
        sleep(random.uniform(300, 600))
