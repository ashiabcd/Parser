from difflib import get_close_matches
import fileinput
from collections import defaultdict


class parser_main:

# Constructor for parser class
    def __init__(self):
        self.st_pointer = 0
        self.all_errors = []
        self.errors = 0
        self.stack = ["$", "P"]
        self.flag1 = False
        self.string = []
        self.get_grammar_input()
        self.get_lexer_output()


# Takes the output from lexer and stores it in tokens list
# Lexer output assumed as a text file with one token in each line        
    def get_lexer_output(self):
        self.tokens = []
        for line in fileinput.input():
        	self.tokens.append(line.strip())
        self.tokens.append("$")    


# Takes the grammar to be used as input and stores terms, non-terms, rules and predictions in relevant dictionaries and sets
# Format of grammar input file is one expansion rule per line        
    def get_grammar_input(self):
        self.rules = defaultdict(list)
        self.predict = defaultdict(defaultdict)
        self.non_terms = set()
        self.terms = set()
        fp = open("grammar.input")
        for line in fp:
            num, dstr, predictions = line.strip().split("|")
            nt, production = dstr.split("->")
            self.terms.discard(nt)
            self.non_terms.add(nt)
            productions = production.split()
            self.rules[num] = productions
            for term in productions:
                if term not in self.non_terms:
                    self.terms.add(term)
            preds = predictions.split(',')
            for term in preds:
                assert term not in self.predict[nt]
                self.predict[nt][term] = num    
    

# First checks if the token is a term
# If the token is a term, check for proper $ at the bottom of stack
# If the token is a non-term, use appropriate rule 
# If neither, do error recovery
# Check for errors and print relevant output
    def parse_tokens(self):
        while ((self.st_pointer < len(self.tokens)) and self.stack):
            st_top = self.stack[-1]
            token = self.tokens[self.st_pointer]
            if st_top in self.terms and st_top == token or st_top is "$":
                if self.flag1:
                    self.flag1 = False
                    self.errors += 1
                temp1 = self.stack.pop()
                if self.stack:
                    self.string.append(temp1)
                self.st_pointer += 1
                print (" ".join(self.string), " " * (40-len(self.string)), " ".join(self.stack))
                if not self.stack and (self.st_pointer < len(self.tokens)):
                    self.stack = ["$", "P"]
            elif st_top in self.non_terms and token in self.predict[st_top]:
                if self.flag1:
                    self.errors += 1
                    self.flag1 = False
                self.stack.pop()
                rule = self.rules[self.predict[st_top][token]]
                for r in reversed(rule):
                    if r != "EPSILON":
                        self.stack.append(r)
                print (" ".join(self.string), " " * (40-len(self.string)), " ".join(self.stack))
            else:
                self.handle_error()
                if not self.flag1:
                    self.errors += 1
            if self.all_errors and not self.flag1:
                print (self.all_errors[-1])
                self.all_errors = []
        if self.flag1:
            self.errors += 1
            self.flag1 = False
        if self.errors == 0:
            print ("Accepted")
        else:
            print ("Rejected, Errors:",self.errors)

# Handles error recovery actions used
# Look ahead symbols used to rectify typos and allow parser to keep running after encountering errors
# Parser pops the stack until it synchronizes the stack with the current input symbol.
# Search through the current stack to see if there are any productions that could match the current token, if there is then pop the stack to that non-terminal
# If stack has only one production left, continue parsing the input tokens till it matches with that production.
# Insert a terminal for continuation of parsing.
# Removes tokens which are not part of our grammar
    def handle_error(self):
        tok = self.tokens[self.st_pointer]
        if tok is not "$":
            temp2 = (get_close_matches(tok.lower(), self.predict[self.stack[-1]].keys(), 1, cutoff=0.8) or [None])[0]
            if temp2 and temp2 is not tok:
                print ("Cannot recognise",tok)
                self.tokens[self.st_pointer] = temp2
                self.flag1 = False
                return
            elif tok not in self.terms:
                temp3 = self.tokens.pop(self.st_pointer)
                print ("Cannot recognise",temp3)
                self.flag1 = False
                return
        if self.tokens[self.st_pointer] in self.stack:
            while self.stack[-1] != self.tokens[self.st_pointer]:
                self.stack.pop()
            print ("String mismatch, check if all brackets are closed properly")
            return
        if self.flag1:
            for i in range(1, len(self.stack)):
                if self.tokens[self.st_pointer] in self.predict[self.stack[-i]].keys():
                    [self.stack.pop() for j in range(i)]
                    return
            output = []
            if len(self.stack) <= 2:
                while self.st_pointer < len(self.tokens)-1:
                    if self.tokens[self.st_pointer] in self.predict[self.stack[-1]].keys():
                        self.flag1 = False
                        return
                    output.append(self.tokens[self.st_pointer])
                    self.st_pointer += 1
                self.flag1 = False
            if not self.stack[-1] in self.terms:
                self.all_errors.append("Couldn't find: "+('/'.join(self.predict[self.stack[-1]].keys())))
                self.stack.pop()
            else:
                    print ("Expecting:", (self.stack[-1], self.tokens[self.st_pointer]))
                    self.tokens[self.st_pointer] = self.stack[-1]
            return

        self.flag1 = True

test = parser_main()
test.parse_tokens()
