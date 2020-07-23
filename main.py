import subprocess
import os
import telebot
import time
import wave
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
            change_freq(user_id, date)
        except:
            bot.send_message(message.from_user.id, 'Что-то пошло не так при конвертации')
        else:
            bot.send_message(message.from_user.id,'Конвертация прошла успешно')
            bot.send_document(message.from_user.id,
                              data=open(f'static/audio_voice/{str(user_id)}-{str(date)}-16kHz.wav', 'rb'))


def convert(file_name, user_id, date):
    src_filename = f'static/audio_voice/{file_name}'
    est_filename = f'static/audio_voice/{str(user_id)}-{str(date)}.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, est_filename])
    if process.returncode != 0:
        raise Exception("Something went wrong")

def change_freq(user_id, date):
    with wave.open(f'static/audio_voice/{str(user_id)}-{str(date)}.wav', 'rb') as file:
        n_channels = file.getnchannels()
        sample_width = file.getsampwidth()
        framerate = 16000
        n_frames = file.getnframes()
        comp_type = file.getcomptype()
        comp_name = file.getcompname()
        print(file.getframerate())

        frames = file.readframes(n_frames)
        assert len(frames) == sample_width * n_frames

    with wave.open(f'static/audio_voice/{str(user_id)}-{str(date)}-16kHz.wav', 'wb') as file:
        params = (n_channels, sample_width, framerate, n_frames, comp_type, comp_name)
        file.setparams(params)
        file.writeframes(frames)

@bot.message_handler(content_types=['photo'])
def download_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    src = os.path.join(f'static/images', file_info.file_path.split('/')[1])

    with open(src, 'rb') as file:
        file.write(downloaded_file)

bot.polling()