FROM python:3.10-slim-bookworm

WORKDIR /client_app

COPY requirements.client.txt .

RUN pip install --no-cache-dir -r requirements.client.txt

COPY streamlit_app.py .

ENV ENV='prod'

CMD ["streamlit", "run", "streamlit_app.py", "--server.headless=true"]
