FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget unzip libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 google-chrome-stable

RUN CHROME_DRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY monitor_freecash.py .

CMD ["python", "monitor_freecash.py"]
