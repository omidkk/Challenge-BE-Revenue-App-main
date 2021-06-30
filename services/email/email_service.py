import smtplib
import ssl


class SendEmail():

    @classmethod
    def send_main(cls, mode, receiver_email, token):
        port = 465  # For SSL
        __password = 'QQ123456789QQ'
        __sender_email = "layermarkinterview@gmail.com"

        # Create a secure SSL context
        context = ssl.create_default_context()

        RESET_PASSWORD_MESSAGE = """\
            Subject: Reset Password

            Please use {} to reset your password."""

        ACCOUNT_VERIFICATION_MESSAGE = """\
            Subject: Email Verification

            Please use {} to activate your account."""

        message = ''
        if mode == 'reset_password':
            message = RESET_PASSWORD_MESSAGE
        elif mode == 'account_verification':
            message = ACCOUNT_VERIFICATION_MESSAGE

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(__sender_email, __password)
            server.sendmail(__sender_email, receiver_email, message.format(token))
