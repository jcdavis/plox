import argparse

class LoxRunner(object):
    def __init__(self):
        had_error = False
    
    def run(self, contents: str) -> None:
        for token in contents.split():
            print("{}".format(token))

    def error(self, line: int, message: str) -> None:
        print("[line {}] Error: {}", line, message)

    def run_file(self, file_name: str) -> None:
        with open(file_name, 'r', encoding='utf-8') as file:
            self.run(file.read())

    def run_prompt(self) -> None:
        line = input('>')
        while line:
            self.run(line)
            self.had_error = False
            line = input('>')

def main() -> None:
    parser = argparse.ArgumentParser(prog='plox')
    parser.add_argument('-f', '--file', required=False)
    args = parser.parse_args()
    lox = LoxRunner()
    if args.file:
        lox.run_file(args.file)
    else:
        lox.run_prompt()

if __name__ == "__main__":
    main()
