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

# Configura logs para o console
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
        logging.info("Acessando página de login")
        driver.get("https://freecash.com/auth/login")
        sleep(random.uniform(3, 6))
        
        # Verifica redirecionamentos
        if "login" not in driver.current_url:
            logging.warning(f"Redirecionado para {driver.current_url}, possível CAPTCHA ou erro")
            return False
        
        # Aguarda até que o campo de email esteja visível
        logging.info("Aguardando campo de email")
        email_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((
                By.XPATH, 
                "//input[@id='email' or @name='email' or @type='email' or contains(@class, 'email')]"
            ))
        )
        logging.info("Inserindo email")
        email_field.send_keys(email)
        
        # Aguarda o campo de senha
        logging.info("Aguardando campo de senha")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, 
                "//input[@id='password' or @name='password' or @type='password' or contains(@class, 'password')]"
            ))
        )
        logging.info("Inserindo senha")
        password_field.send_keys(password)
        
        # Verifica se há CAPTCHA
        try:
            captcha = driver.find_element(By.XPATH, "//div[contains(@class, 'captcha') or contains(@id, 'captcha')]")
            logging.warning("CAPTCHA detectado, login manual necessário")
            return False
        except:
            pass
        
        # Clica no botão de login
        logging.info("Clicando no botão de login")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//button[@type='submit' or contains(@class, 'login') or contains(text(), 'Login') or contains(text(), 'Sign In')]"
            ))
        )
        login_button.click()
        sleep(random.uniform(6, 9))
        
        # Verifica se o login foi bem-sucedido
        WebDriverWait(driver, 10).until(
            EC.url_contains("dashboard")
        )
        logging.info("Salvando cookies")
        pickle.dump(driver.get_cookies(), open("/app/cookies.pkl", "wb"))
        logging.info("Login bem-sucedido")
        return True
    except Exception as e:
        logging.error(f"Erro no login: {str(e)}")
        return False
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
        surveys = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'survey-item')]"))
        )
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
    if login_freecash(email, password):
        while True:
            surveys_found = monitor_surveys()
            logging.info(f"Ciclo concluído: {surveys_found} pesquisas encontradas")
            sleep(random.uniform(600, 1200))
    else:
        logging.error("Falha no login, encerrando bot")
