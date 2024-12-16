FROM python:3

ENV API_HOST=0.0.0.0
ENV APT_PORT=8005

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./emulator.py" ]
EXPOSE 8005