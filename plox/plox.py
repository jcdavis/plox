import logging
import argparse
from . import interpreter
from . import parser
from . import resolver
from . import scanner

had_error = False


def error(line: int, message: str) -> None:
    global had_error
    had_error = True
    print(f"[line {line}] Error: {message}")


class LoxRunner:
    def run(self, contents: str) -> None:
        sc = scanner.Scanner(contents)
        tokens = sc.scan_tokens()
        p = parser.Parser(tokens)
        statements = p.parse()
        if had_error:
            return

        interp = interpreter.Interpreter()
        resolve = resolver.Resolver(interp)
        resolve.resolve(statements)
        if had_error:
            return
        interp.interpret(statements)

    def run_file(self, file_name: str) -> None:
        with open(file_name, 'r', encoding='utf-8') as file:
            self.run(file.read())

    def run_prompt(self) -> None:
        global had_error
        line = input('>')
        while line:
            self.run(line)
            had_error = False
            line = input('>')


def main() -> None:
    arg_parser = argparse.ArgumentParser(prog='plox')
    arg_parser.add_argument('-f', '--file', required=False)
    arg_parser.add_argument('-d', "--debug", action='store_true')
    args = arg_parser.parse_args()
    lox = LoxRunner()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    if args.file:
        lox.run_file(args.file)
    else:
        lox.run_prompt()


if __name__ == "__main__":
    main()
