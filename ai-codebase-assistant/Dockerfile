FROM python:3.11

WORKDIR /app

COPY . .

WORKDIR /app/ai-codebase-assistant

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]