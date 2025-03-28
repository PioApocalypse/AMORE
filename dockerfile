FROM python:3.12

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV PYTHONPATH="/app"
ARG URL
ARG VERIFY

RUN echo "ELABFTW_BASE_URL=${URL}" >> .env
RUN echo "VERIFY_SSL=${VERIFY}" >> .env

ENV FLASK_APP=amore/gui/app.py
ENV FLASK_ENV=production

CMD ["flask", "run", "--host=0.0.0.0"]