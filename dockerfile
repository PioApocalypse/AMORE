FROM python:3.12

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV PYTHONPATH="/app"
ARG URL
ARG VERIFY
ENV ELABFTW_BASE_URL=$URL
ENV VERIFY_SSL=$VERIFY
ARG API_KEY
RUN python3 amore/scan_for_categories.py $API_KEY $URL $VERIFY

ENV FLASK_APP=amore/gui/app.py
ENV FLASK_ENV=production

CMD ["flask", "run", "--host=0.0.0.0"]