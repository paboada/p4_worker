import boto3
import os

id_audio = "91"
archivo_original = "Pink_Floyd.wav"

print("¿Digite el numero de mensajes del archivo Pink_Floyd.wav que quiere enviar a la cola?")
numero_max_mensajes = int(input())
print("Se enviaran ", numero_max_mensajes, " mensajes a la cola")
cont = 0
# Create SQS client
access_id=os.environ["S3_AWS_ACCESS_KEY_ID"]
access_secret=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
sqs = boto3.resource('sqs', aws_access_key_id=access_id, aws_secret_access_key=access_secret)
queue = sqs.get_queue_by_name(QueueName='sqs_concursos')
url_queue=queue.url
# Create a new message
while cont < numero_max_mensajes:
    response = queue.send_message(MessageBody='Registrando Mensaje',
                                  MessageAttributes={
                                                        'id_audio': {
                                                                    'StringValue': id_audio,
                                                                    'DataType': 'Number'
                                                                    },
                                                        'archivo_original': {
                                                                    'StringValue': archivo_original,
                                                                    'DataType': 'String'
                                                                    }
                                                    })
    print("Mensaje: ", cont+1, "creado")
    cont = cont+1
