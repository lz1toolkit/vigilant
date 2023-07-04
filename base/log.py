TAG = 'Vigilant'


def log_format(level, tag, content):
    print('%s: %s_%s -> %s' % (level, TAG, tag, content))


def d(tag: str, content: str):
    log_format('Debug', tag, content)


def i(tag: str, content: str):
    log_format('Info', tag, content)


def w(tag: str, content: str):
    log_format('Warning', tag, content)


def e(tag: str, content: str):
    log_format('Fatal', tag, content)
