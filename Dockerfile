FROM tensorflow/tensorflow:2.4.1

RUN mkdir app
WORKDIR /app

RUN apt-get --version
RUN apt-get update && \
    apt-get -y install timidity ffmpeg

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD . .

EXPOSE 8000

CMD ["python", "app.py"]