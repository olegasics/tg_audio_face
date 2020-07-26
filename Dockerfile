FROM ubuntu

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update --fix-missing && apt install -y python3-pip
RUN apt-get install -y ffmpeg && apt-get install -y libsm6 libxrender1 libfontconfig1

WORKDIR /etc/tg/

COPY . /etc/tg/

RUN pip3 install -r requirements.txt

CMD python3 main.py
