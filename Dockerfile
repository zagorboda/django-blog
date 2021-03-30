FROM python:3

RUN mkdir /code
WORKDIR /code

COPY requirements.txt .
COPY entrypoint.sh .

RUN pip install -r requirements.txt
RUN chmod +x entrypoint.sh
# RUN ["chmod", "+x", "entrypoint.sh"]

ENV PYTHONUNBUFFERED 1

COPY . .

# ENTRYPOINT ["/code/entrypoint.sh"]
ENTRYPOINT ["sh","/code/entrypoint.sh"]
