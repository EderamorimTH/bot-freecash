FROM python:3.9-slim

# Instala wget, gnupg e dependências necessárias para o Chrome
RUN apt-get update && apt-get install -y wget gnupg unzip \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 \
    fonts-liberation libatk-bridge2.0-0 libgtk-3-0 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Adiciona a chave e o repositório do Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

# Instala Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Baixa o ChromeDriver compatível com a versão principal do Chrome instalado
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
    CHROME_MAJOR=$(echo $CHROME_VERSION | cut -d '.' -f 1) && \
    CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR") && \
    wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY monitor_freecash.py .

CMD ["python", "monitor_freecash.py"]
