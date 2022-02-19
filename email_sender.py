import smtplib, ssl

sender, password = "balouka.reminder@gmail.com", "Reminder1234"


def send_email(receiver: str, message: str) -> bool:
    """
    Sends an email to a given email address
    :param receiver: The email of the receiver wanted
    :param message: The message to send
    :return: True if email was sent successful and False if it had failed
    """
    port = 465
    context = ssl.create_default_context()

    print("Starting to send")
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
