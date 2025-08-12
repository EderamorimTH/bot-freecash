from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import random
import logging
import pickle
import os

logging.basicConfig(filename='/app/bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_driver():
    logging.info("Inicializando o driver do Chrome")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-background-networking")
    driver = webdriver.Chrome(options=chrome_options)
    logging.info("Driver inicializado com sucesso")
    return driver

def login_freecash(email, password):
    logging.info("Iniciando login no FreeCash")
    driver = get_driver()
    try:
        logging.info("Acessando página de login")
        driver.get("https://freecash.com/login")
        sleep(random.uniform(3, 6))
        logging.info("Inserindo email")
        driver.find_element(By.NAME, "email").send_keys(email)
        logging.info("Inserindo senha")
        driver.find_element(By.NAME, "password").send_keys(password)
        logging.info("Clicando no botão de login")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        sleep(random.uniform(6, 9))
        logging.info("Salvando cookies")
        pickle.dump(driver.get_cookies(), open("/app/cookies.pkl", "wb"))
        logging.info("Login bem-sucedido")
    except Exception as e:
        logging.error(f"Erro no login: {str(e)}")
    finally:
        logging.info("Fechando driver após login")
        driver.quit()

def monitor_surveys():
    logging.info("Iniciando monitoramento de pesquisas")
    driver = get_driver()
    try:
        logging.info("Acessando página inicial do FreeCash")
        driver.get("https://freecash.com")
        sleep(random.uniform(2, 4))
        if os.path.exists("/app/cookies.pkl"):
            logging.info("Carregando cookies")
            cookies = pickle.load(open("/app/cookies.pkl", "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)
        logging.info("Acessando página de pesquisas")
        driver.get("https://freecash.com/surveys")
        sleep(random.uniform(4, 8))
        logging.info("Buscando pesquisas disponíveis")
        surveys = driver.find_elements(By.XPATH, "//div[contains(@class, 'survey-item')]")
        logging.info(f"{len(surveys)} pesquisas encontradas")
        count = 0
        for survey in surveys:
            try:
                reward = survey.find_element(By.XPATH, ".//span[contains(@class, 'reward')]").text
                reward_value = float(reward.replace('$', ''))
                if reward_value >= 0.5:
                    logging.info(f"Iniciando pesquisa com recompensa: {reward}")
                    survey.find_element(By.XPATH, ".//button[contains(@class, 'start-survey')]").click()
                    sleep(random.uniform(6, 12))
                    options = driver.find_elements(By.XPATH, "//input[@type='radio']")
                    if options:
                        logging.info("Selecionando opção aleatória")
                        random.choice(options).click()
                        logging.info("Enviando resposta")
                        driver.find_element(By.XPATH, "//button[@type='submit']").click()
                        sleep(random.uniform(3, 6))
                        logging.info(f"Pesquisa completada: {reward}")
                        count += 1
                    if count >= 5:
                        logging.info("Limite de 5 pesquisas por ciclo atingido")
                        break
            except Exception as e:
                logging.error(f"Erro ao processar pesquisa: {str(e)}")
                continue
        return len(surveys)
    except Exception as e:
        logging.error(f"Erro ao monitorar: {str(e)}")
        return 0
    finally:
        logging.info("Fechando driver após monitoramento")
        driver.quit()

if __name__ == "__main__":
    logging.info("Iniciando o bot")
    email = "edert905@gmail.com"
    password = "Mariamiguel1"
    login_freecash(email, password)
    while True:
        surveys_found = monitor_surveys()
        logging.info(f"Ciclo concluído: {surveys_found} pesquisas encontradas")
        sleep(random.uniform(600, 1200))
