from prompt_toolkit.validation import Validator, ValidationError


class EmailValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(message='Please enter your email', cursor_position=len(document.text))
        elif not document.text.endswith('@red.unid.mx'):
            raise ValidationError(message='Please enter a valid institutional email', cursor_position=len(document.text))


class PasswordValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(message='Please enter your password')
