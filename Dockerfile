FROM python:3.12.4
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY MzConverter.py .
CMD ["python", "MzConverter.py"]
