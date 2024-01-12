from plox.interpreter import Interpreter
from plox.scanner import Scanner
from plox.parser import Parser

def __run_script(contents: str) -> list[str]:
    sc = Scanner(contents)
    tokens = sc.scan_tokens()
    p = Parser(tokens)
    statements = p.parse()
    interp = Interpreter(capture_output=True)
    interp.interpret(statements)
    return interp.output

def test_sanity():
    assert __run_script("print 1+2;") == ["3.0"]

def test_var():
    script = """
        var foo = 1;
        var bar = 2;
        foo = 3;
        {
            var bar = 4;
            print foo + bar;
        }
        print foo + bar;
    """
    assert __run_script(script) == ["7.0", "5.0"]

def test_for():
    script = """
        var i = 0;
        for (;i<5;i = i+2) {
            print i;
        }
    """
    assert __run_script(script) == ["0.0", "2.0", "4.0"]

def test_fun():
    script = """
        fun test(first, last) {
            print first + " " + last;
        }
        test("Hello", "world!");
    """
    assert __run_script(script) == ["Hello world!"]