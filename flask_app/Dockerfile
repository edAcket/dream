FROM python:3.8

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_ENV=production

CMD ["flask", "run", "--host=0.0.0.0"]
