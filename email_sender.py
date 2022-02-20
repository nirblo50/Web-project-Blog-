import smtplib, ssl

sender, password = "balouka.reminder@gmail.com", "Reminder1234"

template = """\
Subject: #Title#

#Body#

#Sign#
"""


def send_email(receiver: str, title: str, body: str, sign: str) -> bool:
    """
    Sends an email to a given email address
    :param receiver: The email of the receiver wanted
    :param message: The message to send
    :return: True if email was sent successful and False if it had failed
    """
    port = 465
    context = ssl.create_default_context()

    print("Starting to send")
    message = template.replace("#Title#", title)
    message = message.replace("#Body#", body)
    message = message.replace("#Sign#", sign)


    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", port,
                              context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, message)
            print("email was sent!")
    except Exception as e:
        print("email was not sent do to an error:\n", e)
        return False
    return True

if __name__ == '__main__':
    send_email("nirblo50@gmail.com", "message from site", "132", "nir")