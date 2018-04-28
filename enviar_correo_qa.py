import sendgrid
import os

email_from="supervoices.cloud@gmail.com"
email_to="pabloandresboada@gmail.com"
email_subject="Hello World from the SendGrid Python Library!"
email_content="Hola, esta es una prueba de envio de mail a traves de add-on de Heroku"

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
data = {
  "personalizations": [
    {
      "to": [
        {
          "email": email_to
        }
      ],
      "subject": email_subject
    }
  ],
  "from": {
    "email": email_from
  },
  "content": [
    {
      "type": "text/plain",
      "value": email_content
    }
  ]
}
response = sg.client.mail.send.post(request_body=data)
print(response.status_code)
print(response.body)
print(response.headers)
