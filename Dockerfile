FROM python:3.7.1-alpine
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
EXPOSE 443
ENTRYPOINT ["python","./telegram.py"]