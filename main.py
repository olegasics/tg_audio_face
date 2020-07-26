import subprocess
import os
import telebot
import time
import cv2

from telebot import apihelper
from settings import tg_token, proxy_host, proxy_port, proxy_login, proxy_pass

bot = telebot.TeleBot(tg_token)
apihelper.proxy = {
    'https': f'http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}'
}


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message,
                 'Привет. Бот конвертирует аудиосообщения в формат .wav с частотой дискретизации'
                 ' 16kHz. Просто отправьте любое голосовое сообщение')
    time.sleep(3)
    bot.reply_to(message,
                 'Также бот определяет, есть ли на отправленном вами фото лицо. Отправьте любую фотографию')


@bot.message_handler(content_types=['voice'])
def download_audio(message):
    if isinstance(message, telebot.types.Message):
        file_info = bot.get_file(message.voice.file_id)
        dowloaded_file = bot.download_file(file_info.file_path)
        user_id = str(message.from_user.id)
        date = str(message.date)
        file_name = f'static/audio_voice/{str(user_id)}-{str(date)}.wav'
        src = os.path.join('static/audio_voice', file_info.file_path.split('/')[1])

        with open(src, 'wb') as file:
            file.write(dowloaded_file)
        try:
            convert(file_info.file_path.split('/')[1], user_id, date)
        except Exception as exc:
            print(exc)
            bot.send_message(message.from_user.id, 'Что-то пошло не так при конвертации')
        else:
            bot.send_message(message.from_user.id,'Конвертация прошла успешно')
            bot.send_document(message.from_user.id,
                              data=open(f'static/audio_voice/{str(user_id)}-{str(date)}-16kHz.wav', 'rb'))


def convert(file_name, user_id, date):
    src_filename = f'static/audio_voice/{file_name}'
    est_filename = f'static/audio_voice/{str(user_id)}-{str(date)}-16kHz.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, '-acodec', 'pcm_s16le', '-ac',
                              '1',
                              '-ar',
                              '16000',
                              est_filename])
    if process.returncode != 0:
        raise Exception("Something went wrong")


@bot.message_handler(content_types=['photo'])
def download_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    user_id = str(message.from_user.id)
    date = str(message.date)

    src = os.path.join(f'static/images', f'user-{user_id}_date-{date}.jpg')

    with open(src, 'wb') as file:
        file.write(downloaded_file)

    try:
        face_rec(src, user_id, date)
    except Exception as exc:
        print(exc)
        bot.send_message(message.from_user.id, 'Лиц не обнаружено. Попробуйте еще раз')
    else:
        bot.send_message(message.from_user.id, 'Обнаружены лица')
        bot.send_photo(message.from_user.id, photo=open(f'static/images/user-{user_id}_date-{date}-face.jpg', 'rb'))


def face_rec(file_path, user_id, date):
    face_cascade = cv2.CascadeClassifier(r'/etc/tg/venv/lib/python3.8/site-packages/cv2/data/haarcascade_frontalface_default.xml')
    image = cv2.imread(filename=file_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(10,10)
    )
    if len(faces) != 0:
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)
        cv2.imwrite(f'static/images/user-{user_id}_date-{date}-face.jpg', image)
    else:
        raise Exception


bot.polling()