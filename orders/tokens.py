from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

# Custom Token generated for account activation
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.address.email_confirmed)
        )


account_activation_token = AccountActivationTokenGenerator()
