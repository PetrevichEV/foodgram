LENGTH_TEXT = 15
MIN_VALUE = 1
MAX_VALUE = 10
MAX_LENGTH = 256
MAX_SLAG = 50
MIN_YEAR = 0
MAX_EMAIL_FIELD = 254
MAX_NAME_FIELD = 150
CONFIRM_CODE_LEN = 32
PER_PAGE = 10
RESOLVED_CHARS = (
    'Допустимы только латинские буквы, '
    'цифры и символы @/./+/-/_. '
)
FORBIDDEN_NAME = 'Имя пользователя \'me\' использовать нельзя!'
HELP_TEXT_NAME = RESOLVED_CHARS + FORBIDDEN_NAME
UNIQUE_FIELDS = (
    'Пользователь с таким email уже существует.',
    'Пользователь с таким username уже существует.'
)
