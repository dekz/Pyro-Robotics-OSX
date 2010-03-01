"""A framework for running unit test examples, written in docstrings.

This lets you write 'Ex: sqrt(4) ==> 2; sqrt(-1) raises ValueError' in the
docstring for sqrt, and then execute the examples as unit tests.

This functionality is similar to Tim Peters' doctest module, but I
started this before doctest became an official Python module.  If you
want more functionality and standardization, use doctest; if you want
to make your docstrings shorter, you might want docex.  (The name
'docex' connotes DOCstring EXamples, a similarity to doctest, the
literal 'Ex:', and a certain package delivery service that also ends
with 'ex', and offers fast reliable no-frills service.)

From Python, when you want to test modules m1, m2, ... do:
    docex.Test([m1, m2, ...])
From the shell, when you want to test files *.py, do:
    python docex.py output-file *.py
If output file ends in .htm or .html, it will be written in HTML.
If output file is -, then standard output is used.

For each module, Test looks at the __doc__ and _docex strings of the
module itself, and of each member, and recursively for each member
class.  If a line in a docstring starts with r'^\s*Ex: ' (a line with
blanks, then 'Ex: '), then the remainder of the string after the colon
is treated as examples. Each line of the examples should conform to
one of the following formats:

    (1) Blank line or a comment; these just get echoed verbatim to the log.
    (2) Of the form example1 ; example2 ; ...
    (3) Of the form 'x ==> y' for any expressions x and y.
            x is evaled and assigned to _, then y is evaled.
            If x != y, an error message is printed.
    (4) Of the form 'x raises y', for any statement x and expression y.
            First y is evaled to yield an exception type, then x is execed.
            If x doesn't raise the right exception, an error msg is printed.
    (5) Of the form 'statement'. Statement is execed for side effect.
    (6) Of the form 'expression'. Expression is evaled for side effect. 

My main reason for stubbornly sticking with my docex rather than converting 
to doctest is that I want docstrings to be brief. Compare doctest's 8-lines:
    >>> len('abc')
    3
    >>> len([])
    0
    >>> len(5))
    Traceback (most recent call last):
      ...
    TypeError: len() of unsized object
with docex's 1-line:
    Ex: len('abc') ==> 3; len([]) ==> 0; len(5) raises TypeError
"""

import re, sys, types

class Test:
    """A class to run test examples written in docstrings or in _docex."""

    def __init__(self, modules=None, html=1, out=None,
                 title='Docex Example Output'):
        if modules is None:
            modules = sys.modules.values()
        self.passed = self.failed = 0;
        self.dictionary = {}
        self.already_seen = {}
        self.html = html
        try:
            if out: sys.stdout = out
            self.writeln('', '<<header("%s")>>\n<pre>\n' % title)
            for module in modules:
                self.run_module(module)
            self.writeln(str(self), '</pre>\n<hr><h1>', '</h1>\n<<footer>>')
        finally:
            if out:
                sys.stdout = sys.__stdout__
                out.close()
                
    def __repr__(self):
	if self.failed:
            return ('<Test: #### failed %d, passed %d>'
                    % (self.failed, self.passed))
        else:
            return '<Test: passed all %d>' % self.passed

    def run_module(self, object):
        """Run the docstrings, and then all members of the module."""
        if not self.seen(object):
            self.dictionary.update(vars(object)) # import module into self
            name = object.__name__
            self.writeln('## Module %s ' % name,
             '\n</pre><a name=%s><h1>' % name,
             '(<a href="%s.html">.html</a>, <a href="%s.py">.py</a>)</h1><pre>'
             % (name, name))
            self.run_docstring(object)
            names = object.__dict__.keys()
            names.sort()
            for name in names:
                val = object.__dict__[name]
                if isinstance(val, types.ClassType):
                    self.run_class(val)
                elif isinstance(val, types.ModuleType):
                    pass
                elif not self.seen(val):
                    self.run_docstring(val)

    def run_class(self, object):
        """Run the docstrings, and then all members of the class."""
        if not self.seen(object):
            self.run_docstring(object)
            names = object.__dict__.keys()
            names.sort()
            for name in names:
                self.run_docstring(object.__dict__[name])

    def run_docstring(self, object, search=re.compile(r'(?m)^\s*Ex: ').search):
        "Run the __doc__ and _docex attributes, if the object has them."
        if hasattr(object, '__doc__'):
            s = object.__doc__
            if isinstance(s, str):
                match = search(s)
                if match: self.run_string(s[match.end():])
        if hasattr(object, '_docex'):
                self.run_string(object._docex)
        
    def run_string(self, teststr):
        """Run a test string, printing inputs and results."""
        if not teststr: return
        teststr = teststr.strip()
        if teststr.find('\n') > -1:
            map(self.run_string, teststr.split('\n'))
        elif teststr == '' or teststr.startswith('#'):
            self.writeln(teststr)
        elif teststr.find('; ') > -1:
            for substr in teststr.split('; '): self.run_string(substr)
        elif teststr.find('==>') > -1:
            teststr, result = teststr.split('==>')
            self.evaluate(teststr, result)
        elif teststr.find(' raises ') > -1:
            teststr, exception = teststr.split(' raises ')
            self.raises(teststr, exception)
        else: ## Try to eval, but if it is a statement, exec
            try:
                self.evaluate(teststr)
            except SyntaxError:
                exec teststr in self.dictionary

    def evaluate(self, teststr, resultstr=None):
        "Eval teststr and check if resultstr (if given) evals to the same."
        self.writeln('>>> ' +  teststr.strip())
        result = eval(teststr, self.dictionary)
        self.dictionary['_'] = result
        self.writeln(repr(result))
        if resultstr == None:
          return
        elif result == eval(resultstr, self.dictionary):
          self.passed += 1
        else:
          self.fail(teststr, resultstr)
    
    def raises(self, teststr, exceptionstr):
        teststr = teststr.strip()
        self.writeln('>>> ' + teststr)
        except_class = eval(exceptionstr, self.dictionary)
        try:
            exec teststr in self.dictionary
        except except_class:
            self.writeln('# raises %s as expected' % exceptionstr)
            self.passed += 1
            return
        self.fail(teststr, exceptionstr)

    def fail(self, teststr, resultstr):
        self.writeln('###### ERROR, TEST FAILED: expected %s for %s' 
                     % (resultstr, teststr),
                     '<font color=red><b>', '</b></font>')
        self.failed += 1

    def writeln(self, s, before='', after=''):
        "Write s, html escaped, and wrapped with html code before and after."
        s = str(s)
        if self.html:
            s = s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            print '%s%s%s' % (before, s, after)
        else:
            print s

    def seen(self, object):
        """Return true if this object has been seen before.
        In any case, record that we have seen it."""
        result = self.already_seen.has_key(id(object))
        self.already_seen[id(object)] = 1
        return result

def main(args):
    import glob
    out = None
    html = 0
    if args[0] != "-" and not args[0].endswith(".py"):
        out = open(args[0], 'w')
        if args[0].endswith(".html") or args[0].endswith(".htm"):
            html = 1
    modules = []
    for arg in args:
        for file in glob.glob(arg):
            if file.endswith('.py'):
                modules.append(__import__(file[:-3]))
    print Test(modules, html=html, out=out)

if __name__ == '__main__':
    main(sys.argv[1:])


