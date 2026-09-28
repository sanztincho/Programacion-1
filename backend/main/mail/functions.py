# Configuración del envío de mail
from .. import mailsender
from flask import current_app, render_template
from flask_mail import Message
from smtplib import SMTPException


# La función pide al menos 3 atributos: to (lista de destinatarios), subject (asunto)
# y template (nombre de la plantilla en main/templates, sin extensión)
def sendMail(to, subject, template, **kwargs):
    # Configuración del mail
    msg = Message(subject, sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=to)
    try:
        # Creación del cuerpo del mensaje (versión texto y versión HTML)
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        # Envío de mail
        mailsender.send(msg)
    except SMTPException as e:
        current_app.logger.warning(str(e))
        return "Mail deliver failed"
    return True
