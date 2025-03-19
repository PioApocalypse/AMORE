FROM python:3.12

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV PYTHONPATH="/app"
ENV BASE_URL="https://elabftw.fisica.unina.it/"
ENV API_KEY="asdasdasd"
ENV VERIFY=True

RUN echo "ELABFTW_BASE_URL=$BASE_URL" >> .env
RUN echo "API_KEY=$API_KEY" >> .env
RUN echo "VERIFY_SSL=$VERIFY" >> .env

ENV FLASK_APP=amore/gui/app.py
ENV FLASK_ENV=production

CMD ["flask", "run", "--host=127.0.0.1"]