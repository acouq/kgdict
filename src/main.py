import sys
from typing import Any

from cli import get_user_input
from tool import render_table

from err import AppError, UserInterruptError
from settings import Settings
from dict import Dict


class App:
    def __init__(self, argv: Any | None = None) -> None:
        self.user_input = get_user_input(argv)
        self.settings = Settings()
        self.dict = Dict(self.settings)

    def run(self) -> None:
        match self.user_input.op:
            case "add":
                for w in self.user_input.add.words:
                    self.dict.add_word(w)
                    print(f"Add {w} success.")
            case "del":
                for w in self.user_input.delete.words:
                    self.dict.delete_word(w)
                    print(f"Delete {w} success.")
            case "set":
                self.dict.update_word(
                    self.user_input.set.word, self.user_input.set.meaning
                )
                print("Set success.")
            case "get":
                word_meanings = []
                for w in self.user_input.get.words:
                    wm = self.dict.query_word(w)
                    if wm:
                        word_meanings.append(wm)
                if word_meanings:
                    print(render_table(word_meanings))
                else:
                    print("No result.")
            case "pick":
                word_meanings = self.dict.query_random(self.user_input.pick.count)
                if word_meanings:
                    print(render_table(word_meanings))
                else:
                    print("No result.")
            case "range":
                word_meanings = self.dict.query_range(
                    self.user_input.range.start, self.user_input.range.end
                )
                if word_meanings:
                    print(render_table(word_meanings))
                else:
                    print("No result.")

    def close(self) -> None:
        self.dict.close_db()


def main(argv: Any | None = None) -> int:
    app = None
    try:
        app = App(argv)
        app.run()
    except UserInterruptError:
        print("Exiting...")
        return 1
    except AppError as e:
        print(e, file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected err: {e}", file=sys.stderr)
        return 3
    finally:
        if app:
            app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
