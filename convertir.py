import boto3
import botocore
import os
import pydub
import glob
import shutil
import smtplib
import time
from pymongo import MongoClient
import pprint

path_media = '/app/'
archivo_descarga = "doublebassSustentacion.wav"
#pydub.AudioSegment.ffmpeg = "/app/vendor/ffmpeg/bin"
pydub.AudioSegment.converter = "/app/vendor/ffmpeg/bin"

print("Convirtiendo de WAV a MP3 script convertir.py...............")
try:
    msplit = archivo_descarga.split(".")
    print("msplit[0]: ", msplit[0])
    print("msplit[1]: ", msplit[1])
    mp3_file = msplit[0] + '.mp3'
    wav_file = path_media+archivo_descarga
    print("wav_file: ", wav_file)
    print("mp3_file: ", mp3_file)
    sound = pydub.AudioSegment.from_wav(wav_file)
    sound.export(mp3_file, format= "mp3")
    print("Conversion Exitosa!!!!!!!!!")
    ok=1
except:
    print("Ocurrio un error en la CONVERSION del archivo")
    print("No se elimina el mensaje de la cola")
    ok=0
