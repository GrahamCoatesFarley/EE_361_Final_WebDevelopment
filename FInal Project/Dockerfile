FROM python
ENV PYTHONUNBUFFERED 1
WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]