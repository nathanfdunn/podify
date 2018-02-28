
FROM python:3.6.4

LABEL maintainer="Nathan Dunn"

COPY app.py requirements.txt /app/
COPY frames /app/frames/
COPY results /app/results/
COPY static /app/static/
COPY temp /app/temp/
COPY templates /app/templates/

#COPY app.py requirements.txt frames results static temp templates /app/

WORKDIR /app/

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

#ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]