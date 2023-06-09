FROM python:3.8


COPY manage.py gunicorn-cfg.py requirements.txt .env ./
COPY EQUITY_new.csv ./

COPY EQUITY_L.csv ./
COPY app app
COPY authentication authentication
COPY core core

RUN pip install -r requirements.txt

RUN python manage.py makemigrations
RUN python manage.py migrate
RUN echo "yes" | python manage.py collectstatic

EXPOSE 8080
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
