FROM python:3.10-slim-bookworm

RUN python -m pip install --upgrade pip

WORKDIR /EdGame_bot

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /EdGame_bot/entrypoint.sh

ENTRYPOINT ["/EdGame_bot/entrypoint.sh"]
