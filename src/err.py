"""错误类型定义。"""


class AppError(Exception):
    def __str__(self) -> str:
        return f"App error: {super().__str__()}"


class ParseApiKeyError(AppError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"parse api key fail: {err}")


class UserInterruptError(AppError):
    pass


class DictError(AppError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"dict operation fail: {err}")
        self.err = err


class RequestApiError(DictError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"request api fail: {err}")
        self.err = err


class ParseApiResponseError(DictError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"parse api response fail: {err}")
        self.err = err


class ParseUserInputError(AppError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"parse user input fail: {err}")
        self.err = err


class DatabaseError(AppError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"database operation fail: {err}")
        self.err = err


class DatabaseQueryError(DatabaseError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"database query fail: {err}")
        self.err = err


class DatabaseInsertError(DatabaseError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"database insert fail: {err}")
        self.err = err


class DatabaseDeleteError(DatabaseError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"database delete fail: {err}")
        self.err = err


class DatabaseUpdateError(DatabaseError):
    def __init__(self, err: Exception | str) -> None:
        super().__init__(f"database update fail: {err}")
        self.err = err
