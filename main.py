import subprocess
import os
import soundfile as sf
import ffmpeg
import telebot
import time

from telebot import apihelper
from pydub import AudioSegment

bot = telebot.TeleBot('1327887205:AAHwgAbPQBDkEPE5lsL-qxChN5tgPXNvXD8')
apihelper.proxy = {
    'https': 'http://IpwJHbsVr:fbpw6t8ys@45.153.55.193:54931'
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
def download_file(message):
    if isinstance(message, telebot.types.Message):
        file_info = bot.get_file(message.voice.file_id)
        dowloaded_file = bot.download_file(file_info.file_path)
        user_id = str(message.from_user.id)
        date = str(message.date)
        src = os.path.join('static/audio_voice', file_info.file_path.split('/')[1])

        with open(src, 'wb') as file:
            file.write(dowloaded_file)
        try:
            res = convert(file_info.file_path.split('/')[1], user_id, date)
        except:
            bot.send_message(message.from_user.id, 'Что-то пошло не так при конвертации')
        else:
            bot.send_message(message.from_user.id,'Конвертация прошла успешно')
            bot.send_document(message.from_user.id,
                              data=open(f'static/audio_voice/{str(user_id)}-{str(date)}.wav', 'rb'))

def convert(file_name, user_id, date):
    src_filename = f'static/audio_voice/{file_name}'
    est_filename = f'static/audio_voice/{str(user_id)}-{str(date)}.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, est_filename])
    if process.returncode != 0:
        raise Exception("Something went wrong")


bot.polling()