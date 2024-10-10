import logging


class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, validate=True):
        super().__init__(fmt=fmt, datefmt=datefmt, validate=validate)
        self.colors = {
            "RESET": "\u001b[0m",
            # FORGROUND COLORS
            "FGBLACK": "\u001b[30m",
            "FGRED": "\u001b[31m",
            "FGGREEN": "\u001b[32m",
            "FGYELLOW": "\u001b[33m",
            "FGBLUE": "\u001b[34m",
            "FGMAGENTA": "\u001b[35m",
            "FGCYAN": "\u001b[36m",
            "FGWHITE": "\u001b[37m",
            # BACKGROUND COLORS
            "BGBLACK": "\u001b[40m",
            "BGRED": "\u001b[41m",
            "BGGREEN": "\u001b[42m",
            "BGYELLOW": "\u001b[43m",
            "BGBLUE": "\u001b[44m",
            "BGMAGENTA": "\u001b[45m",
            "BGCYAN": "\u001b[46m",
            "BGWHITE": "\u001b[47m",
            # STYLES
            "BOLD": "\u001b[1m",
            "UNDERLINE": "\u001b[4m",
            "REVERSE": "\u001b[7m",
        }

    def format(self, record):
        if record.levelno == logging.DEBUG:
            log_color = f'{self.colors["FGCYAN"]}'
        elif record.levelno == logging.INFO:
            log_color = f'{self.colors["FGGREEN"]}'
        elif record.levelno == logging.WARNING:
            log_color = f'{self.colors["FGYELLOW"]}'
        elif record.levelno == logging.ERROR:
            log_color = f'{self.colors["FGRED"]}'
        elif record.levelno == logging.CRITICAL:
            log_color = f'{self.colors["BOLD"]}{self.colors["FGWHITE"]}{self.colors["BGRED"]}'
        else:
            log_color = self.colors["RESET"]
        record.msg = f"{self.colors['RESET']}{log_color}{record.msg}{self.colors['RESET']}"
        return super().format(record)
