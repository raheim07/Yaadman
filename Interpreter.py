# ============================================================
# PURPOSE: Runs YaadmanLang programs by walking the AST
# Name: Demario Scott (2106675)
# ============================================================

from platform import node
from Parser import parse, ASTNode, YaadmanSyntaxError


# CUSTOM ERROR TYPES
class YaadmanSemanticError(Exception):
    # Errors like the variable we never declare getting caught BEFORE running
    pass

class YaadmanRuntimeError(Exception):
    # Errors like dividing by zero being caught WHILE runnin
    pass

class ReturnSignal(Exception):
    # This one is not really a real error a just a trick to stop a function and send back a value
    # This ago run when we hit "Return x;" so we raise this to jump back to the function caller
    def __init__(self, value):
        self.value = value






# ENVIRONMENT (SYMBOL TABLE)
# Tracks every variable, name, type, and current value. Each function a gets its own Environment so variables no clash

class Environment:

    def __init__(self, parent=None):
        self.vars = {} #this store variable values {'x': 10}
        self.types = {} #this store variable types {'x': 'number'}
        self.parent = parent #this point to the outer scope

    def declare(self, name, var_type, lineno=0):
        # Declare a new variable (Mek x Number;)
        # Raises an error if the same variable is declared twice in the same scope
        if name in self.vars:
            raise YaadmanSemanticError(
                f"[Line {lineno}] Variable '{name}' is already declared in this scope."
            )
        self.vars[name] = None
        self.types[name] = var_type

    def set(self, name, value, lineno=0):
        #Assign a value to a variable (Set x To 5) first, looks in the current scope first, then outer scopes
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.set(name, value, lineno)
        else:
            raise YaadmanRuntimeError(
                f"[Line {lineno}] Cannot assign to '{name}' — variable was never declared."
            )

    def get(self, name, lineno=0):
        #Retrieve the value of a variable. first looks in current scope first, then outer scopes
        if name in self.vars:
            if self.vars[name] is None:
                raise YaadmanRuntimeError(
                    f"[Line {lineno}] Variable '{name}' was declared but never given a value."
                )
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name, lineno)
        else:
            raise YaadmanRuntimeError(
                f"[Line {lineno}] Variable '{name}' does not exist."
            )

    def is_declared(self, name):
        #This ago return True if the variable exists anywhere in scope chain
        if name in self.vars:
            return True
        return self.parent.is_declared(name) if self.parent else False





# SEMANTIC ANALYZER
# Walks the AST before execution to catch logical mistakes early.

class SemanticAnalyzer:

    def __init__(self):
        self.env = Environment() #symbol table for checking
        self.functions = {} #keeps track of defined functions

    def analyze(self, node):
        #Finds and calls the right check method based on node type eg. for a 'Declare' node it calls check_Declare()
        method = f'check_{node.node_type}'
        checker = getattr(self, method, self.generic_check)
        checker(node)

    def generic_check(self, node):
        #just check all children if no specific method exists
        for child in node.children:
            if isinstance(child, ASTNode):
                self.analyze(child)

    def check_Program(self, node):
        #This check every statement in the program
        for child in node.children:
            self.analyze(child)

    def check_Declare(self, node):
        #"Mek x Number"  register the variable in the symbol table
        self.env.declare(node.value['name'], node.value['type'], node.lineno)

    def check_Assign(self, node):
        #"Set x To 5"  make sure x was declared before we assign to it
        name = node.children[0].value
        if not self.env.is_declared(name):
            raise YaadmanSemanticError(
                f"[Line {node.lineno}] '{name}' must be declared with 'Mek' before assigning."
            )
        self.check_expr(node.children[1])  #use this to also check right hand side of the expression

    def check_expr(self, node):
        #check an expression if there is a problem
        if node.node_type == 'BinOp':
            #HGere the division by zero is caught at runtime by the Try/Ketch block
            self.check_expr(node.children[0])
            self.check_expr(node.children[1])

        elif node.node_type == 'Identifier':
            #Make sure the variable being used was declared
            if not self.env.is_declared(node.value):
                raise YaadmanSemanticError(
                    f"[Line {node.lineno}] Variable '{node.value}' used before declaration."
                )

        elif node.node_type == 'UnaryMinus':
            self.check_expr(node.children[0])

        elif node.node_type in ('FuncCallExpr', 'FuncCall'):
            #check all arguments passed to the function
            for arg in node.children:
                if isinstance(arg, ASTNode):
                    self.check_expr(arg)

    def check_Show(self, node):
        #This part "Show x, "hello";" checks each item being shown
        for child in node.children:
            self.check_expr(child)

    def check_Tek(self, node):
        #Here "Tek name Text;" taek declares and reads input, so register it
        name = node.value['name']
        var_type = node.value['type']
        if not self.env.is_declared(name):
            self.env.declare(name, var_type, node.lineno)

    def check_If(self, node):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.analyze(child)

    def check_IfElse(self, node):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.analyze(child)

    def check_While(self, node):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.analyze(child)

    def check_For(self, node):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.analyze(child)

    def check_TryCatch(self, node):
        #check both the Try block and the Ketch block
        for child in node.children:
            if isinstance(child, ASTNode):
                self.analyze(child)

    def check_FuncDef(self, node):
        #and just store the function name (I don't deeply check it here)
        self.functions[node.value] = node

    def check_FuncCall(self, node):
        for arg in node.children:
            if isinstance(arg, ASTNode):
                self.check_expr(arg)

    def check_Return(self, node):
        self.check_expr(node.children[0])

    def check_Condition(self, node):
        self.check_expr(node.children[0])
        self.check_expr(node.children[1])




    #These nodes are just containers that recurse into their children
    def check_ThenBody(self, node):
        for c in node.children: self.analyze(c)
    def check_ElseBody(self, node):
        for c in node.children: self.analyze(c)
    def check_TryBody(self, node):
        for c in node.children: self.analyze(c)
    def check_KetchBody(self, node):
        for c in node.children: self.analyze(c)
    def check_WhileBody(self, node):
        for c in node.children: self.analyze(c)
    def check_ForBody(self, node):
        for c in node.children: self.analyze(c)
    def check_FuncBody(self, node):
        for c in node.children: self.analyze(c)



    #the leaf nodes that doesnt really have anything to check inside them
    def check_Params(self, node): pass
    def check_Number(self, node): pass
    def check_StringLiteral(self, node): pass
    def check_BoolLiteral(self, node): pass
    def check_Identifier(self, node):
        if not self.env.is_declared(node.value):
            raise YaadmanSemanticError(
                f"[Line {node.lineno}] Variable '{node.value}' not declared."
            )






# INTERPRETER (EXECUTION ENGINE)
# Walks the AST and actually RUNS the program node by node

class Interpreter:

    def __init__(self):
        self.global_env = Environment()  #the main variable scope
        self.functions = {}              #this part stores all defined functions by name

    def exec_Program(self, node):
        #Entry point, rifgt here run every statement at the top level
        for child in node.children:
            self._exec(child, self.global_env)

    def _exec(self, node, env):
        #finds and calls the right _exec_ method for the node type 
        method = f'_exec_{node.node_type}'
        executor = getattr(self, method, None)
        if executor is None:
            raise YaadmanRuntimeError(
                f"Don't know how to execute node type: {node.node_type}"
            )
        return executor(node, env)




    #DECLARE
    def _exec_Declare(self, node, env):
        # "Mek x Number;" — add the variable to the current scope
        env.declare(node.value['name'], node.value['type'], node.lineno)

    #ASSIGN
    def _exec_Assign(self, node, env):
        # "Set x To 5 + 3;" — evaluate the right side and store it
        name = node.children[0].value
        value = self._eval(node.children[1], env)
        env.set(name, value, node.lineno)



    #SHOW

    def _exec_Show(self, node, env):
        #"Show "Hello", x;" and then evaluate each item and then print them side by side
        parts = []
        for child in node.children:
            val = self._eval(child, env)
            parts.append(str(val))
        print(" ".join(parts))


    #TEK (USER INPUT
    def _exec_Tek(self, node, env):
        
        #"Tek name Text;"

        #ask for your name
        name = node.value['name']
        var_type = node.value['type']
        if not env.is_declared(name):
            env.declare(name, var_type, node.lineno)
        raw = input(f"Enter value for '{name}' ({var_type}): ")
        if var_type == 'number':
            try:
                    #convert to float if decimal, int if whole number
                
                value = float(raw) if '.' in raw else int(raw)
            except ValueError:
                raise YaadmanRuntimeError(
                    f"[Line {node.lineno}] Expected a number for '{name}', got '{raw}'."
                )
        else:
            value = raw  #if i use this then text type stays as a string
        
        env.set(name, value, node.lineno)

    #IF
    def _exec_If(self, node, env):
        # children[0] = Condition, children[1] = ThenBody
        if self._eval(node.children[0], env):
            for stmt in node.children[1].children:
                self._exec(stmt, env)


    #IF-ELSE
    def _exec_IfElse(self, node, env):
        
        #children[0] = Condition, children[1] = ThenBody, children[2] = ElseBody
        if self._eval(node.children[0], env):
            
            for stmt in node.children[1].children:
                self._exec(stmt, env)
        else:
            for stmt in node.children[2].children:
                self._exec(stmt, env)

    #WHILE
    def _exec_While(self, node, env):
        
        #keep looping as long as the condition is true
        #children[0] = Condition, children[1] = WhileBody
        while self._eval(node.children[0], env):
            for stmt in node.children[1].children:
                self._exec(stmt, env)

    #FOR LOOP
    def _exec_For(self, node, env):
        #"For (Mek i Number : i < 10 : Set i To i + 1)"

        loop_env = Environment(parent=env)  #for loop gets its own scope

        self._exec(node.children[0], loop_env)  #declare the loop variable


        #Give the loop variable a starting value of 0 if not set
        init_name = node.children[0].value['name']
        if loop_env.vars[init_name] is None:
            loop_env.vars[init_name] = 0

        while self._eval(node.children[1], loop_env):
            for stmt in node.children[3].children:
                self._exec(stmt, loop_env)
            self._exec(node.children[2], loop_env)

    # children[0] = Declare, children[1] = Condition,
    # children[2] = Update (Assign), children[3] = ForBody





    #FUNCTION DEFINITION
    def _exec_FuncDef(self, node, env):
        #"Function add(a Number, b Number)"
        #Just store the function
        self.functions[node.value] = node

    #FUNCTION CALL (statement)
    def _exec_FuncCall(self, node, env):
        self._call_function(node, env)

    #FUNCTION CALL (expression)
    def _exec_FuncCallExpr(self, node, env):
        return self._call_function(node, env)



    def _call_function(self, node, env):
        
        #loook up the function by name
        func_name = node.value
        if func_name not in self.functions:
            raise YaadmanRuntimeError(
                f"[Line {node.lineno}] Function '{func_name}' is not defined."
            )

        func_node = self.functions[func_name]
        params = func_node.children[0].children #list of Param nodes
        body = func_node.children[1].children #ist of statements

        #evaluate all the arguments the caller passed in
        args = [self._eval(arg, env) for arg in node.children]

        #make sure the right number of arguments were passed
        if len(params) != len(args):
            raise YaadmanRuntimeError(
                f"[Line {node.lineno}] '{func_name}' needs {len(params)} "
                f"argument(s) but got {len(args)}."
            )

        #create a new local scope for the function
        func_env = Environment(parent=self.global_env)

        #bind each parameter to its argument value
        
        for param, arg_val in zip(params, args):
            func_env.declare(param.value['name'], param.value['type'], node.lineno)
            
            func_env.set(param.value['name'], arg_val, node.lineno)

        
        
        #run the function body then after it catch a Return if it fires
        try:
            for stmt in body:
                self._exec(stmt, func_env)
        except ReturnSignal as r:
            return r.value  #send the return value back to the caller

        return None  #function had no return statement




    #RETURN
    def _exec_Return(self, node, env):
        # Evaluate the return value and throw it up the call stack
        value = self._eval(node.children[0], env)
        raise ReturnSignal(value)

    #TRY amd KETCh
    def _exec_TryCatch(self, node, env):
        
        #try to run the try block
        #If a runtime error happens then it ago run the ketch block instead
        try_stmts = node.children[0].children
        ketch_stmts = node.children[1].children
        try:
            for stmt in try_stmts:
                self._exec(stmt, env)
        except YaadmanRuntimeError as e:
            
            #Store the error message in case the ketch block wants to show it
            env.vars['__error__'] = str(e)
            for stmt in ketch_stmts:
                self._exec(stmt, env)



    #EXPRESSION EVALUATOR
    #Calculates the value of any expression node and returns it
    def _eval(self, node, env):

        if node.node_type == 'Number':
            #A plain number
            return node.value

        elif node.node_type == 'StringLiteral':
            #A string
            return node.value


        elif node.node_type == 'BoolLiteral':
            #True or False
            return node.value

        elif node.node_type == 'Identifier':
            #a variable name on the symbol table
            
            return env.get(node.value, node.lineno)

        elif node.node_type == 'UnaryMinus':
            #Negative number
            val = self._eval(node.children[0], env)
            
            
            if val is None:
                raise YaadmanRuntimeError(
                    f"[Line {node.lineno}] Cannot negate a variable with no value."
                )
            return -val

        
        elif node.node_type == 'BinOp':
            #math operation
            left = self._eval(node.children[0], env)
            right = self._eval(node.children[1], env)
            op = node.value

            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/':
                
                if right == 0:
                    #division by zero at runtime
                    raise YaadmanRuntimeError(
                        f"[Line {node.lineno}] Division by zero."
                    )
                return left / right


        elif node.node_type == 'Condition':
            #comparison
            left = self._eval(node.children[0], env)
            right = self._eval(node.children[1], env)
            op = node.value
            if op == '>':  return left > right
            if op == '<':  return left < right
            if op == '==': return left == right
            if op == '>=': return left >= right
            if op == '<=': return left <= right

        elif node.node_type == 'FuncCallExpr':
            #a function call used inside an expression
            return self._call_function(node, env)


        else:
            raise YaadmanRuntimeError(
                f"[Line {node.lineno}] Cannot evaluate: {node.node_type}"
            )












#MAIN RUN FUNCTION
#This part is what the UI will call to run at the program then pass into the source code as a string


def run_program(source_code: str):

    print("═" * 55)
    print("   YaadmanLang — Executing Program")
    print("═" * 55)

    #Parse the source code into an AST
    try:
        ast = parse(source_code)
    except YaadmanSyntaxError as e:
        print(e)
        return

    #Run semantic analysis to catch errors before execution
    try:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        print("[✓] Semantic checks passed — no pre-run errors found.\n")
    except YaadmanSemanticError as e:
        print(f"[✗] Semantic Error — {e}")
        return

    #execute the program
    try:
        interpreter = Interpreter()

        #register all top-level functions first so they can be called later

        for child in ast.children:
            if isinstance(child, ASTNode) and child.node_type == 'FuncDef':
                interpreter.functions[child.value] = child

        interpreter.exec_Program(ast)

    except YaadmanRuntimeError as e:
        print(f"\n[✗] Runtime Error — {e}")





if __name__ == "__main__":
    # code = input()
    code = """
    Start {
        Function add(a Number, b Number) {
            Mek result Number;
            Set result To a + b;
            Return result;
        }

        Mek x Number;
        Set x To 2;

        Set x To x + 5;

        if (x > 10) {
            Show "x is greater than 10", x;
        } Else {
            Show "x is small";
        }
        
        add(3, 4);
    } Done;
    """

    run_program(code)
















