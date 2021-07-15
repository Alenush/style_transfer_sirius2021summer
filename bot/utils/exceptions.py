# define Python user-defined exceptions
class BotError(Exception):
    """Base class for bot exceptions"""
    pass


class ModelError(BotError):
    """Raised when the error occured with model runtime"""
    pass


class BotRuntimeError(BotError):
    """Raised when the error occured with bot runtime"""
    pass

class BotLogicError(BotRuntimeError):
    """Raised when the error occured with bot logic"""
    pass
