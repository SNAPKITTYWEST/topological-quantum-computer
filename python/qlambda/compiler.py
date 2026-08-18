"""Q-Lambda lexer, parser, reversible QIR synthesizer, and uncompute pass."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Dict, Iterable, List, Optional, Tuple, Union


class TokenType(Enum):
    KW_QBIT = "qbit"
    KW_LET = "let"
    KW_REVERSED = "reversed"
    KW_WITH = "with"
    KW_DO = "do"
    KW_ORACLE = "oracle"
    OP_ROTR = ">>>"
    OP_SHR = ">>"
    OP_XOR = "^"
    OP_AND = "&"
    OP_OR = "|"
    OP_NOT = "~"
    OP_ASSIGN = "="
    OP_ADD = "+"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACK = "["
    RBRACK = "]"
    COMMA = ","
    COLON = ":"
    SEMI = ";"
    IDENT = "IDENT"
    INTEGER = "INTEGER"
    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    line: int
    col: int


class Lexer:
    TOKEN_REGEX: Tuple[Tuple[TokenType, str], ...] = (
        (TokenType.KW_QBIT, r"\bqbit\b"),
        (TokenType.KW_LET, r"\blet\b"),
        (TokenType.KW_REVERSED, r"\breversed\b"),
        (TokenType.KW_WITH, r"\bwith\b"),
        (TokenType.KW_DO, r"\bdo\b"),
        (TokenType.KW_ORACLE, r"\boracle\b"),
        (TokenType.OP_ROTR, r">>>"),
        (TokenType.OP_SHR, r">>"),
        (TokenType.OP_XOR, r"\^"),
        (TokenType.OP_AND, r"&"),
        (TokenType.OP_OR, r"\|"),
        (TokenType.OP_NOT, r"~"),
        (TokenType.OP_ASSIGN, r"="),
        (TokenType.OP_ADD, r"\+"),
        (TokenType.LPAREN, r"\("),
        (TokenType.RPAREN, r"\)"),
        (TokenType.LBRACE, r"\{"),
        (TokenType.RBRACE, r"\}"),
        (TokenType.LBRACK, r"\["),
        (TokenType.RBRACK, r"\]"),
        (TokenType.COMMA, r","),
        (TokenType.COLON, r":"),
        (TokenType.SEMI, r";"),
        (TokenType.INTEGER, r"\b\d+\b"),
        (TokenType.IDENT, r"[a-zA-Z_][a-zA-Z0-9_]*"),
    )

    def __init__(self, source: str):
        self.source = re.sub(r"//.*", "", expand_unroll_directives(source))
        self.pos = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        compiled = [(kind, re.compile(pattern)) for kind, pattern in self.TOKEN_REGEX]
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char == "\n":
                self.line += 1
                self.col = 1
                self.pos += 1
                continue
            if char.isspace():
                self.col += 1
                self.pos += 1
                continue

            for tok_type, regex in compiled:
                match = regex.match(self.source, self.pos)
                if match:
                    value = match.group(0)
                    tokens.append(Token(tok_type, value, self.line, self.col))
                    self.pos += len(value)
                    self.col += len(value)
                    break
            else:
                raise SyntaxError(f"Unexpected character {char!r} at line {self.line}, col {self.col}")
        tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return tokens


class ASTNode:
    """Base class for Q-Lambda AST nodes."""


@dataclass(frozen=True)
class TypeNode(ASTNode):
    name: str
    size: int


class ExprNode(ASTNode):
    """Base class for Q-Lambda expressions."""


@dataclass(frozen=True)
class VarExpr(ExprNode):
    name: str


@dataclass(frozen=True)
class IntLiteralExpr(ExprNode):
    value: int


@dataclass(frozen=True)
class BinOpExpr(ExprNode):
    op: TokenType
    left: ExprNode
    right: ExprNode


@dataclass(frozen=True)
class UnOpExpr(ExprNode):
    op: TokenType
    operand: ExprNode


class StmtNode(ASTNode):
    """Base class for Q-Lambda statements."""


@dataclass(frozen=True)
class LetStmt(StmtNode):
    var_name: str
    var_type: TypeNode
    value: ExprNode


@dataclass(frozen=True)
class WithDoStmt(StmtNode):
    bindings: List[LetStmt]
    body: List[StmtNode]


@dataclass(frozen=True)
class ReversedBlockStmt(StmtNode):
    body: List[StmtNode]


@dataclass(frozen=True)
class OracleDeclStmt(StmtNode):
    name: str
    params: List[Tuple[str, TypeNode]]
    returns: TypeNode
    body: List[StmtNode]


class Parser:
    PRECEDENCE = {
        TokenType.OP_XOR: 1,
        TokenType.OP_OR: 1,
        TokenType.OP_AND: 2,
        TokenType.OP_ADD: 2,
        TokenType.OP_ROTR: 3,
        TokenType.OP_SHR: 3,
    }

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected_type: TokenType) -> Token:
        current = self.peek()
        if current.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type.value}, got {current.type.value} "
                f"({current.value!r}) at line {current.line}"
            )
        self.pos += 1
        return current

    def parse(self) -> List[StmtNode]:
        nodes: List[StmtNode] = []
        while self.peek().type != TokenType.EOF:
            nodes.append(self.parse_statement())
        return nodes

    def parse_statement(self) -> StmtNode:
        token = self.peek()
        if token.type == TokenType.KW_LET:
            return self.parse_let()
        if token.type == TokenType.KW_WITH:
            return self.parse_with_do()
        if token.type == TokenType.KW_REVERSED:
            return self.parse_reversed()
        if token.type == TokenType.KW_ORACLE:
            return self.parse_oracle()
        raise SyntaxError(f"Unexpected statement starting with {token.value!r}")

    def parse_let(self) -> LetStmt:
        self.consume(TokenType.KW_LET)
        var_name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.COLON)
        var_type = self.parse_type()
        self.consume(TokenType.OP_ASSIGN)
        value = self.parse_expr()
        self.consume(TokenType.SEMI)
        return LetStmt(var_name, var_type, value)

    def parse_type(self) -> TypeNode:
        type_name = self.consume(TokenType.KW_QBIT).value
        self.consume(TokenType.LBRACK)
        size = int(self.consume(TokenType.INTEGER).value)
        self.consume(TokenType.RBRACK)
        return TypeNode(type_name, size)

    def parse_with_do(self) -> WithDoStmt:
        self.consume(TokenType.KW_WITH)
        self.consume(TokenType.LPAREN)
        bindings: List[LetStmt] = []
        while self.peek().type != TokenType.RPAREN:
            bindings.append(self.parse_let())
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.KW_DO)
        body = self.parse_block()
        return WithDoStmt(bindings, body)

    def parse_reversed(self) -> ReversedBlockStmt:
        self.consume(TokenType.KW_REVERSED)
        return ReversedBlockStmt(self.parse_block())

    def parse_oracle(self) -> OracleDeclStmt:
        self.consume(TokenType.KW_ORACLE)
        name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.LPAREN)
        params: List[Tuple[str, TypeNode]] = []
        while self.peek().type != TokenType.RPAREN:
            param_name = self.consume(TokenType.IDENT).value
            self.consume(TokenType.COLON)
            params.append((param_name, self.parse_type()))
            if self.peek().type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.COLON)
        returns = self.parse_type()
        body = self.parse_block()
        return OracleDeclStmt(name, params, returns, body)

    def parse_block(self) -> List[StmtNode]:
        self.consume(TokenType.LBRACE)
        body: List[StmtNode] = []
        while self.peek().type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.consume(TokenType.RBRACE)
        return body

    def parse_expr(self) -> ExprNode:
        return self.parse_binary_expr(0)

    def parse_binary_expr(self, precedence: int) -> ExprNode:
        left = self.parse_primary()
        while True:
            op = self.peek().type
            if op not in self.PRECEDENCE or self.PRECEDENCE[op] < precedence:
                break
            self.consume(op)
            right = self.parse_binary_expr(self.PRECEDENCE[op] + 1)
            left = BinOpExpr(op, left, right)
        return left

    def parse_primary(self) -> ExprNode:
        token = self.peek()
        if token.type == TokenType.OP_NOT:
            self.consume(TokenType.OP_NOT)
            return UnOpExpr(TokenType.OP_NOT, self.parse_primary())
        if token.type == TokenType.IDENT:
            return VarExpr(self.consume(TokenType.IDENT).value)
        if token.type == TokenType.INTEGER:
            return IntLiteralExpr(int(self.consume(TokenType.INTEGER).value))
        if token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            expr = self.parse_expr()
            self.consume(TokenType.RPAREN)
            return expr
        raise SyntaxError(f"Unexpected expression token: {token.value!r}")


@dataclass(frozen=True)
class QIRInstruction:
    gate: str
    controls: Tuple[int, ...]
    targets: Tuple[int, ...]
    params: Tuple[Union[int, float], ...] = ()


class QIREngine:
    def __init__(self):
        self.qubit_counter = 0
        self.instructions: List[QIRInstruction] = []
        self.scopes: List[Dict[str, List[int]]] = [{}]

    def allocate(self, name: str, size: int) -> List[int]:
        if size <= 0:
            raise ValueError("qbit register size must be positive")
        qids = list(range(self.qubit_counter, self.qubit_counter + size))
        self.qubit_counter += size
        self.scopes[-1][name] = qids
        return qids

    def resolve(self, name: str) -> List[int]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise NameError(f"Quantum register {name!r} not found")

    def emit(
        self,
        gate: str,
        controls: Iterable[int] = (),
        targets: Iterable[int] = (),
        params: Iterable[Union[int, float]] = (),
    ) -> None:
        self.instructions.append(
            QIRInstruction(gate, tuple(controls), tuple(targets), tuple(params))
        )

    def push_scope(self) -> None:
        self.scopes.append({})

    def pop_scope(self) -> Dict[str, List[int]]:
        if len(self.scopes) == 1:
            raise RuntimeError("cannot pop root scope")
        return self.scopes.pop()


class QLambdaCompiler:
    def __init__(self, ast: List[StmtNode]):
        self.ast = ast
        self.qir = QIREngine()

    def compile(self) -> List[QIRInstruction]:
        for node in self.ast:
            self.visit(node)
        return self.qir.instructions

    def visit(self, node: StmtNode) -> None:
        if isinstance(node, OracleDeclStmt):
            self.visit_oracle(node)
        elif isinstance(node, LetStmt):
            self.visit_let(node)
        elif isinstance(node, WithDoStmt):
            self.visit_with_do(node)
        elif isinstance(node, ReversedBlockStmt):
            self.visit_reversed(node)
        else:
            raise NotImplementedError(type(node).__name__)

    def visit_oracle(self, node: OracleDeclStmt) -> None:
        self.qir.push_scope()
        for param_name, param_type in node.params:
            self.qir.allocate(param_name, param_type.size)
        self.qir.allocate(f"{node.name}_out", node.returns.size)
        for stmt in node.body:
            self.visit(stmt)
        self.qir.pop_scope()

    def visit_let(self, node: LetStmt) -> None:
        target = self.qir.allocate(node.var_name, node.var_type.size)
        self.synthesize_expr(node.value, target)

    def visit_with_do(self, node: WithDoStmt) -> None:
        self.qir.push_scope()
        binding_start = len(self.qir.instructions)
        for binding in node.bindings:
            self.visit_let(binding)
        binding_end = len(self.qir.instructions)
        for stmt in node.body:
            self.visit(stmt)
        self.qir.instructions.extend(self.invert_circuit(self.qir.instructions[binding_start:binding_end]))
        self.qir.pop_scope()

    def visit_reversed(self, node: ReversedBlockStmt) -> None:
        marker = len(self.qir.instructions)
        for stmt in node.body:
            self.visit(stmt)
        self.qir.instructions = self.qir.instructions[:marker] + self.invert_circuit(
            self.qir.instructions[marker:]
        )

    def synthesize_expr(self, expr: ExprNode, target: List[int]) -> None:
        if isinstance(expr, VarExpr):
            self.copy_register(self.qir.resolve(expr.name), target)
        elif isinstance(expr, IntLiteralExpr):
            for index, qid in enumerate(target):
                if (expr.value >> index) & 1:
                    self.qir.emit("X", targets=[qid])
        elif isinstance(expr, UnOpExpr) and expr.op == TokenType.OP_NOT:
            self.synthesize_expr(expr.operand, target)
            for qid in target:
                self.qir.emit("X", targets=[qid])
        elif isinstance(expr, BinOpExpr):
            self.synthesize_binop(expr, target)
        else:
            raise NotImplementedError(f"Cannot synthesize {expr!r}")

    def synthesize_binop(self, expr: BinOpExpr, target: List[int]) -> None:
        if expr.op == TokenType.OP_XOR:
            self.synthesize_expr(expr.left, target)
            self.synthesize_expr(expr.right, target)
        elif expr.op == TokenType.OP_AND:
            marker = len(self.qir.instructions)
            left = self.temp("_and_l", len(target))
            right = self.temp("_and_r", len(target))
            self.synthesize_expr(expr.left, left)
            self.synthesize_expr(expr.right, right)
            temp_program = self.qir.instructions[marker:]
            for lq, rq, tq in zip(left, right, target):
                self.qir.emit("CCX", controls=[lq, rq], targets=[tq])
            self.qir.instructions.extend(self.invert_circuit(temp_program))
        elif expr.op == TokenType.OP_ROTR:
            shift = self.literal_shift(expr.right)
            src = self.temp("_rotr", len(target))
            self.synthesize_expr(expr.left, src)
            width = len(target)
            for index, tq in enumerate(target):
                self.qir.emit("CX", controls=[src[(index + shift) % width]], targets=[tq])
        elif expr.op == TokenType.OP_SHR:
            shift = self.literal_shift(expr.right)
            src = self.temp("_shr", len(target))
            self.synthesize_expr(expr.left, src)
            for index, tq in enumerate(target):
                src_index = index + shift
                if src_index < len(src):
                    self.qir.emit("CX", controls=[src[src_index]], targets=[tq])
        elif expr.op == TokenType.OP_ADD:
            self.synthesize_modular_add(expr.left, expr.right, target)
        else:
            raise NotImplementedError(f"Unsupported operator {expr.op.value}")

    def synthesize_modular_add(self, left_expr: ExprNode, right_expr: ExprNode, target: List[int]) -> None:
        width = len(target)
        left = self.temp("_add_l", width)
        right = self.temp("_add_r", width)
        carry = self.temp("_carry", width + 1)
        self.synthesize_expr(left_expr, left)
        self.synthesize_expr(right_expr, right)
        self.copy_register(left, target)

        for index in range(width):
            self.qir.emit("CCX", controls=[target[index], right[index]], targets=[carry[index + 1]])
            self.qir.emit("CX", controls=[target[index]], targets=[right[index]])
            self.qir.emit("CCX", controls=[right[index], carry[index]], targets=[carry[index + 1]])
            self.qir.emit("CX", controls=[right[index]], targets=[target[index]])

        for index in range(width - 1, -1, -1):
            self.qir.emit("CX", controls=[right[index]], targets=[target[index]])
            self.qir.emit("CCX", controls=[right[index], carry[index]], targets=[carry[index + 1]])
            self.qir.emit("CX", controls=[target[index]], targets=[right[index]])
            self.qir.emit("CCX", controls=[target[index], right[index]], targets=[carry[index + 1]])

    def copy_register(self, source: List[int], target: List[int]) -> None:
        if len(source) < len(target):
            raise ValueError("source register is narrower than target register")
        for src, dst in zip(source, target):
            self.qir.emit("CX", controls=[src], targets=[dst])

    def temp(self, prefix: str, size: int) -> List[int]:
        return self.qir.allocate(f"{prefix}_{self.qir.qubit_counter}", size)

    @staticmethod
    def literal_shift(expr: ExprNode) -> int:
        if not isinstance(expr, IntLiteralExpr):
            raise TypeError("shift/rotate amount must be an integer literal")
        return expr.value

    @staticmethod
    def invert_circuit(instructions: List[QIRInstruction]) -> List[QIRInstruction]:
        inverted: List[QIRInstruction] = []
        for inst in reversed(instructions):
            if inst.gate in {"X", "CX", "CCX", "H"}:
                inverted.append(inst)
            elif inst.gate == "T":
                inverted.append(QIRInstruction("TDG", inst.controls, inst.targets, inst.params))
            elif inst.gate == "TDG":
                inverted.append(QIRInstruction("T", inst.controls, inst.targets, inst.params))
            elif inst.gate == "ROTR":
                shift, width = int(inst.params[0]), int(inst.params[1])
                inverted.append(QIRInstruction("ROTR", inst.controls, inst.targets, ((width - shift) % width, width)))
            else:
                inverted.append(QIRInstruction(f"{inst.gate}_DAGGER", inst.controls, inst.targets, inst.params))
        return inverted


def expand_unroll_directives(source: str) -> str:
    pattern = re.compile(r"#unroll\s+(\d+)\s+for\s+(\w+)\s+in\s+(\d+)\.\.(\d+)\s*\{", re.M)
    while True:
        match = pattern.search(source)
        if not match:
            return source
        count = int(match.group(1))
        var = match.group(2)
        start = int(match.group(3))
        end = int(match.group(4))
        body_start = match.end()
        depth = 1
        pos = body_start
        while pos < len(source) and depth:
            if source[pos] == "{":
                depth += 1
            elif source[pos] == "}":
                depth -= 1
            pos += 1
        body = source[body_start : pos - 1]
        if count != end - start + 1:
            raise ValueError("unroll count must match inclusive range length")
        expanded = "\n".join(
            body.replace(f"{{{var}}}", str(value)).replace(f"${var}", str(value))
            for value in range(start, end + 1)
        )
        source = source[: match.start()] + expanded + source[pos:]


def compile_source(source: str) -> List[QIRInstruction]:
    return QLambdaCompiler(Parser(Lexer(source).tokenize()).parse()).compile()
