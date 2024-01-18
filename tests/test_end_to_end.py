from plox.interpreter import Interpreter
from plox.scanner import Scanner
from plox.parser import Parser
from plox.resolver import Resolver

def __run_script(contents: str) -> list[str]:
    sc = Scanner(contents)
    tokens = sc.scan_tokens()
    p = Parser(tokens)
    statements = p.parse()
    interp = Interpreter(capture_output=True)
    resolve = Resolver(interp)
    resolve.resolve(statements)
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

def test_return():
    script = """
        fun fib(n) {
        if (n <= 1) return n;
        return fib(n - 2) + fib(n - 1);
        }
        print fib(10);
    """
    assert __run_script(script) == ["55.0"]

def test_class():
    script = """
        class Cake {
            taste() {
                var adjective = "delicious";
                print "The " + this.flavor + " cake is " + adjective + "!";
            }
        }

        var cake = Cake();
        cake.flavor = "German chocolate";
        cake.taste();
    """
    assert __run_script(script) == ["The German chocolate cake is delicious!"]

def test_superclass():
    script = """
        class Doughnut {
        cook() {
            print "Fry until golden brown.";
        }
        }

        class BostonCream < Doughnut {
        cook() {
            super.cook();
            print "Pipe full of custard and coat with chocolate.";
        }
        }

        BostonCream().cook();
    """
    assert __run_script(script) == ["Fry until golden brown.", "Pipe full of custard and coat with chocolate."]
