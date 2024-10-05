FROM python:3-alpine
ADD git@github.com:Prizrakost/NewsFromEverywhere_bot.git /bot
WORKDIR /bot
RUN python -m venv /bot
RUN bin/pip install -r requirements.txt
ENV TOKEN=""
ENTRYPOINT bin/python main.py
LABEL org.opencontainers.image.source https://github.com/Prizrakost/NewsFromEverywhere_bot
