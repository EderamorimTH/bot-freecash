from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import random
import logging
import pickle
import os

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Script iniciado no Render")

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
        # Acessa página inicial
        driver.get("https://freecash.com/br")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logging.info(f"Página carregada: {driver.current_url}")

        # Clica no botão "Entrar"
        try:
            login_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='login'], button[href*='login']"))
            )
            login_btn.click()
            logging.info("Botão 'Entrar' clicado")
        except Exception:
            logging.error("Botão 'Entrar' não encontrado")
            return False

        # Aguarda redirecionamento para página de login
        WebDriverWait(driver, 20).until(EC.url_contains("login"))
        logging.info(f"Página de login: {driver.current_url}")

        # Preenche email
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_field.clear()
        email_field.send_keys(email)
        logging.info("Email inserido")

        # Preenche senha
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        password_field.clear()
        password_field.send_keys(password)
        logging.info("Senha inserida")

        # Clica para entrar
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        login_button.click()
        logging.info("Botão de login clicado")

        # Aguarda redirecionamento
        WebDriverWait(driver, 30).until(EC.url_contains("dashboard"))
        logging.info("Login realizado com sucesso")

        # Salva cookies
        pickle.dump(driver.get_cookies(), open("/app/cookies.pkl", "wb"))
        logging.info("Cookies salvos")

        return True
    except Exception as e:
        logging.error(f"Erro no login: {e}")
        logging.info(f"HTML no erro: {driver.page_source[:800]}")
        return False
    finally:
        driver.quit()

def monitor_surveys():
    logging.info("Iniciando monitoramento de pesquisas")
    driver = get_driver()
    try:
        driver.get("https://freecash.com")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        if os.path.exists("/app/cookies.pkl"):
            logging.info("Carregando cookies")
            cookies = pickle.load(open("/app/cookies.pkl", "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)

        driver.get("https://freecash.com/surveys")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "survey-item")))

        surveys = driver.find_elements(By.CLASS_NAME, "survey-item")
        logging.info(f"{len(surveys)} pesquisas encontradas")
        return len(surveys)
    except Exception as e:
        logging.error(f"Erro no monitoramento: {e}")
        return 0
    finally:
        driver.quit()

if __name__ == "__main__":
    logging.info("Iniciando o bot")
    email = "edert905@gmail.com"
    password = "Mariamiguel1"
    if login_freecash(email, password):
        while True:
            qnt = monitor_surveys()
            logging.info(f"Ciclo concluído: {qnt} pesquisas encontradas")
            sleep(random.uniform(600, 1200))
    else:
        logging.error("Falha no login, encerrando bot")
