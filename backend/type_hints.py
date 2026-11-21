"""
Argument type hints for the Function Runner.

For every parameter of a function we work out:
  * what kind of value it expects (number, text, list, dict, ...)
  * a ready-to-run JSON example value
  * allowed choices (when the code compares it against a fixed set of strings)

Sources, in order of trust:
  1. type annotation   (open-source libraries are fully annotated)
  2. default value     (e.g. account_type="savings" -> text)
  3. usage in the body (e.g. accounts[account_id]["balance"] > 0
                        -> dict of records keyed by account_id, with a numeric balance)
  4. parameter name    (e.g. *_id -> text, is_* -> bool, plural -> list)

Sources 3 and 4 are heuristics, so results are flagged as "inferred".
"""

import ast
import json
import re
from typing import Any, Dict, List, Optional

# ─── Name heuristics ─────────────────────────────────────────

_BOOL_PREFIXES = ("is_", "has_", "can_", "should_", "allow_", "include_", "use_", "enable_")
_NUMBER_WORDS = {
    "amount": 1000, "price": 250, "cost": 250, "fee": 50, "fare": 120, "salary": 50000,
    "balance": 5000, "income": 60000, "monthly_income": 60000, "debt": 1000, "principal": 10000,
    "rate": 5.5, "percent": 10, "percentage": 10, "discount": 10, "tax": 5,
    "score": 85, "marks": 85, "credit_score": 720, "rating": 4.5, "gpa": 3.5, "cgpa": 3.5,
    "age": 25, "years": 2, "months": 12, "days": 30, "hours": 8, "minutes": 30,
    "quantity": 2, "qty": 2, "count": 3, "limit": 10, "top_n": 5, "n": 5, "size": 10,
    "distance": 12.5, "distance_km": 12.5, "km": 12.5, "duration": 30, "weight": 2.5,
    "threshold": 75, "min_percent": 75, "capacity": 50, "slots": 10, "total_slots": 10,
    "credits": 3, "semester": 1, "year": 2026, "level": 1, "stock": 100, "attempts": 3,
    "latitude": 23.81, "longitude": 90.41, "lat": 23.81, "lon": 90.41, "lng": 90.41,
}
_NUMBER_SUFFIXES = ("_amount", "_price", "_cost", "_fee", "_rate", "_percent", "_score",
                    "_count", "_days", "_hours", "_minutes", "_years", "_months", "_km",
                    "_limit", "_total", "_qty", "_quantity", "_age", "_balance", "_income",
                    "_slots", "_marks", "_capacity", "_weight", "_distance", "_duration")
_NUMBER_PREFIXES = ("num_", "total_", "max_", "min_", "avg_")
_STRING_WORDS = {
    "name": "Alice", "first_name": "Alice", "last_name": "Rahman", "email": "alice@example.com",
    "phone": "01700000000", "address": "Dhaka", "city": "Dhaka", "code": "SAVE10",
    "reason": "Requested by user", "status": "active", "date": "2026-01-15",
    "start_date": "2026-01-15", "end_date": "2026-02-15", "due_date": "2026-02-15",
    "time": "10:00", "description": "Sample description", "title": "Sample title",
    "category": "general", "type": "standard", "role": "student", "department": "CSE",
    "password": "Passw0rd!", "username": "alice", "query": "alice", "keyword": "alice",
    "text": "hello world", "message": "hello", "location": "Dhaka", "pickup": "Gulshan",
    "dropoff": "Dhanmondi", "method": "card", "payment_method": "card", "grade": "A",
    "currency": "BDT", "card_number": "4111111111111111", "url": "https://example.com",
    "path": "/tmp/example.txt", "s": "hello world", "string": "hello world", "value": "hello",
    "slot": "10:00", "time_slot": "10:00", "shift": "morning", "day": "Monday", "gender": "female",
    "blood_group": "A+", "priority": "normal", "vehicle_type": "car", "plate": "DHA-1234",
}

# unannotated names that are (almost) always Python objects, not data
_OBJECT_NAMES = {"cls": "class", "klass": "class", "func": "function", "fn": "function",
                 "callback": "function", "f": "function", "wrapped": "function", "decorator": "function"}

# values that usually mean "this record can't be used" — avoid them as the default example
_TERMINAL_STATES = {"cancelled", "canceled", "completed", "closed", "inactive", "expired", "blocked",
                    "suspended", "rejected", "deleted", "failed", "banned", "frozen", "discharged",
                    "returned", "delivered", "refunded", "paid", "graduated", "terminated", "resolved",
                    "dropped", "archived", "unavailable", "occupied", "full", "lost", "damaged"}


def _id_example(name: str) -> str:
    base = name[:-3] if name.endswith("_id") else name
    prefix = "".join(w[0] for w in base.split("_") if w).upper() or "ID"
    if len(prefix) == 1:
        prefix = base[:3].upper()
    return f"{prefix}001"


def _is_plural(name: str) -> bool:
    last = name.split("_")[-1]
    return len(last) > 3 and last.endswith("s") and not last.endswith(("ss", "us", "is"))


def _number_from_name(name: str) -> Optional[float]:
    if name in _NUMBER_WORDS:
        return _NUMBER_WORDS[name]
    for word, val in _NUMBER_WORDS.items():
        if name.endswith("_" + word):
            return val
    if name.endswith(_NUMBER_SUFFIXES) or name.startswith(_NUMBER_PREFIXES):
        return 10
    return None


def _guess_from_name(name: str) -> Optional[str]:
    """Return a kind guessed only from the parameter name."""
    if name.startswith(_BOOL_PREFIXES):
        return "bool"
    if name.endswith(("_id", "_code", "_name", "_type", "_date", "_email", "_status", "_slot", "_time")) \
            or name in _STRING_WORDS:
        return "string"
    if _number_from_name(name) is not None:
        return "number"
    if _is_plural(name) or name.endswith(("_list", "_ids")):
        return "list"
    if name.endswith(("_map", "_dict", "_config", "_data", "_info", "_record", "_details")):
        return "dict"
    return None


# ─── Usage analysis ──────────────────────────────────────────

_LIST_METHODS = {"append", "extend", "insert", "remove", "sort", "reverse"}
_DICT_METHODS = {"items", "keys", "values", "update", "setdefault", "popitem"}
_STR_METHODS = {"lower", "upper", "strip", "lstrip", "rstrip", "split", "startswith", "endswith",
                "replace", "isdigit", "isalpha", "isalnum", "isnumeric", "title", "capitalize",
                "find", "zfill", "encode", "casefold", "isupper", "islower", "isspace", "splitlines"}
_NUM_FUNCS = {"round", "abs", "int", "float", "pow", "divmod"}
_SEQ_FUNCS = {"sum", "max", "min", "sorted", "enumerate", "reversed", "any", "all", "list", "set", "tuple"}
_ARITH = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)


class _Usage:
    """Signals collected about one value (a parameter, a record field or a list element)."""

    def __init__(self):
        self.votes: Dict[str, int] = {}
        self.fields: Dict[str, "_Usage"] = {}      # record["field"] / record.get("field")
        self.items: Optional["_Usage"] = None      # values of a dict / elements of a list
        self.key_param: Optional[str] = None       # collection[<param>]
        self.key_name: Optional[str] = None        # name of the key variable (for labels/examples)
        self.choices: List[Any] = []
        self.tuple_size: int = 0

    def vote(self, kind: str, weight: int = 1):
        self.votes[kind] = self.votes.get(kind, 0) + weight

    def field(self, name: str) -> "_Usage":
        return self.fields.setdefault(name, _Usage())

    def item(self) -> "_Usage":
        if self.items is None:
            self.items = _Usage()
        return self.items


def _merge(dst: _Usage, src: _Usage, mapping: Dict[str, str], depth: int = 0):
    if src.key_name and not dst.key_name:
        dst.key_name = src.key_name
    if src.key_param and not dst.key_param and src.key_param in mapping:
        dst.key_param = mapping[src.key_param]
    for k, n in src.votes.items():
        dst.vote(k, n)
    for c in src.choices:
        if c not in dst.choices:
            dst.choices.append(c)
    if depth > 4:
        return
    for f, fu in src.fields.items():
        _merge(dst.field(f), fu, mapping, depth + 1)
    if src.items is not None:
        _merge(dst.item(), src.items, mapping, depth + 1)


class _Analyzer:
    def __init__(self, func: ast.AST, params: List[str],
                 module_funcs: Optional[Dict[str, ast.AST]] = None, depth: int = 0):
        self.func = func
        self.module_funcs = module_funcs or {}
        self.depth = depth
        self.params = set(params)
        self.parents: Dict[ast.AST, ast.AST] = {}
        for node in ast.walk(func):
            for child in ast.iter_child_nodes(node):
                self.parents[child] = node
        # local names bound to literal string lists, e.g. valid_types = ["a", "b"]
        self.const_lists: Dict[str, List[Any]] = {}
        # loop variables / aliases -> the _Usage they describe
        self.aliases: Dict[str, _Usage] = {}
        self.usage: Dict[str, _Usage] = {p: _Usage() for p in params}

    # -- entry point ------------------------------------------------
    def run(self) -> Dict[str, _Usage]:
        for node in ast.walk(self.func):
            if isinstance(node, ast.Assign) and isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                vals = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
                if vals and len(vals) == len(node.value.elts):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            self.const_lists[t.id] = vals
        # two passes so loop aliases defined later in walk order are known
        for _ in range(2):
            self._bind_aliases()
        for node in ast.walk(self.func):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                target = self._usage_of_name(node.id)
                if target is not None:
                    self._analyze(node, target)
        return self.usage

    def _usage_of_name(self, name: str) -> Optional[_Usage]:
        if name in self.usage:
            return self.usage[name]
        return self.aliases.get(name)

    def _expr_usage(self, expr: ast.AST) -> Optional[_Usage]:
        """Map an expression like p, p[k], p[k]["f"], p.values() to the _Usage it denotes."""
        if isinstance(expr, ast.Name):
            return self._usage_of_name(expr.id)
        if isinstance(expr, ast.Subscript):
            base = self._expr_usage(expr.value)
            if base is None:
                return None
            sl = expr.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                return base.field(sl.value)
            if isinstance(sl, ast.Slice):
                return base
            return base.item()
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute):
            base = self._expr_usage(expr.func.value)
            if base is None:
                return None
            if expr.func.attr == "get" and expr.args:
                a0 = expr.args[0]
                if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                    return base.field(a0.value)
                return base.item()
        return None

    def _bind_aliases(self):
        for node in ast.walk(self.func):
            # for x in <collection> / comprehension generators
            if isinstance(node, (ast.For, ast.comprehension)):
                it, target = node.iter, node.target
                if isinstance(it, ast.Call) and isinstance(it.func, ast.Attribute) and it.func.attr in ("values", "items", "keys"):
                    coll = self._expr_usage(it.func.value)
                    if coll is None:
                        continue
                    coll.vote("dict", 3)
                    if it.func.attr == "values" and isinstance(target, ast.Name):
                        self.aliases[target.id] = coll.item()
                    elif it.func.attr == "items" and isinstance(target, ast.Tuple) and len(target.elts) == 2 \
                            and isinstance(target.elts[1], ast.Name):
                        self.aliases[target.elts[1].id] = coll.item()
                    continue
                if isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id == "enumerate" and it.args:
                    coll = self._expr_usage(it.args[0])
                    if coll is not None and isinstance(target, ast.Tuple) and len(target.elts) == 2 \
                            and isinstance(target.elts[1], ast.Name):
                        coll.vote("list", 2)
                        self.aliases[target.elts[1].id] = coll.item()
                    continue
                coll = self._expr_usage(it)
                if coll is not None:
                    coll.vote("iterable", 2)
                    if isinstance(target, ast.Name):
                        self.aliases[target.id] = coll.item()
            # x = p[k]  /  x = p.get(k)   -> alias to the record
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                if isinstance(node.value, (ast.Subscript, ast.Call)):
                    u = self._expr_usage(node.value)
                    if u is not None and node.targets[0].id not in self.params:
                        self.aliases[node.targets[0].id] = u

    def _merge_callee(self, callee: ast.AST, call: ast.Call, u: _Usage):
        """`u` is passed as positional arg `index` to a helper in the same file."""
        cargs = callee.args.posonlyargs + callee.args.args
        index = None
        for i, a in enumerate(call.args):
            if self._expr_usage(a) is u:
                index = i
                break
        if index is None or index >= len(cargs) or callee is self.func:
            return
        names = [a.arg for a in cargs]
        sub = _Analyzer(callee, names, self.module_funcs, self.depth + 1).run()
        # callee param name -> our param name, for args passed straight through
        mapping = {names[i]: a.id for i, a in enumerate(call.args[:len(names)])
                   if isinstance(a, ast.Name) and a.id in self.params}
        _merge(u, sub[names[index]], mapping)

    # -- per-occurrence analysis -------------------------------------
    def _analyze(self, node: ast.AST, u: _Usage):
        """Look at how `node` (an expression denoting `u`) is used by its parent."""
        parent = self.parents.get(node)
        if parent is None:
            return

        if isinstance(parent, ast.Subscript) and parent.slice is node:
            u.vote("key", 1)   # used as a lookup key -> usually an id string
            return

        if isinstance(parent, ast.Subscript) and parent.value is node:
            sl = parent.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                u.vote("record", 2)
                self._analyze(parent, u.field(sl.value))
            elif isinstance(sl, ast.Constant) and isinstance(sl.value, int):
                u.vote("list", 2)
                self._analyze(parent, u.item())
            elif isinstance(sl, ast.Slice):
                u.vote("sequence", 2)
            else:
                u.vote("dict", 3)
                if isinstance(sl, ast.Name):
                    u.key_name = u.key_name or sl.id
                    if sl.id in self.params:
                        u.key_param = sl.id
                self._analyze(parent, u.item())
            return

        if isinstance(parent, ast.Attribute) and parent.value is node:
            call = self.parents.get(parent)
            attr = parent.attr
            if attr in _LIST_METHODS:
                u.vote("list", 3)
            elif attr in _DICT_METHODS:
                u.vote("dict", 3)
            elif attr in _STR_METHODS or attr in ("join", "format"):
                u.vote("string", 3)
            elif attr == "get" and isinstance(call, ast.Call) and call.args:
                a0 = call.args[0]
                if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                    u.vote("record", 2)
                    f = u.field(a0.value)
                    if len(call.args) > 1 and isinstance(call.args[1], ast.Constant):
                        self._vote_constant(f, call.args[1].value, 2)
                    self._analyze(call, f)
                else:
                    u.vote("dict", 3)
                    if isinstance(a0, ast.Name):
                        u.key_name = u.key_name or a0.id
                        if a0.id in self.params:
                            u.key_param = a0.id
                    self._analyze(call, u.item())
            return

        if isinstance(parent, ast.Compare):
            self._analyze_compare(node, parent, u)
            return

        if isinstance(parent, ast.BinOp) and isinstance(parent.op, _ARITH):
            other = parent.right if parent.left is node else parent.left
            if isinstance(other, ast.Constant) and isinstance(other.value, str):
                u.vote("string", 2)
            elif isinstance(other, (ast.List, ast.ListComp)):
                u.vote("list", 2)
            elif isinstance(parent.op, ast.Mod) and parent.left is node and isinstance(other, ast.Tuple):
                u.vote("string", 1)
            else:
                u.vote("number", 2)
            return

        if isinstance(parent, ast.AugAssign) and isinstance(parent.op, _ARITH):
            if isinstance(parent.value, ast.Constant) and isinstance(parent.value.value, str):
                u.vote("string", 2)
            else:
                u.vote("number", 2)
            return

        if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, ast.USub):
            u.vote("number", 2)
            return

        if isinstance(parent, ast.Call) and node in parent.args and isinstance(parent.func, ast.Name):
            fname = parent.func.id
            if fname in _NUM_FUNCS or (fname in ("min", "max") and len(parent.args) > 1):
                u.vote("number", 2)
            elif fname in _SEQ_FUNCS:
                u.vote("iterable", 2)
                if fname == "sum":
                    u.item().vote("number", 2)
            elif fname == "len":
                u.vote("sized", 1)
            elif fname in self.module_funcs and self.depth < 2:
                self._merge_callee(self.module_funcs[fname], parent, u)
            return

        # sum(x["f"] for x in ...) / max([...]) -> elements are numbers
        if isinstance(parent, (ast.GeneratorExp, ast.ListComp)) and parent.elt is node:
            call = self.parents.get(parent)
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in ("sum", "max", "min") \
                    and len(call.args) == 1:
                u.vote("number", 2)
            return

        # a, b = param  -> a fixed-size list (tuple); look at how the parts are used
        if isinstance(parent, ast.Assign) and parent.value is node and len(parent.targets) == 1 \
                and isinstance(parent.targets[0], ast.Tuple):
            u.vote("list", 3)
            u.tuple_size = len(parent.targets[0].elts)
            for elt in parent.targets[0].elts:
                if isinstance(elt, ast.Name) and elt.id not in self.params:
                    self.aliases.setdefault(elt.id, u.item())
            return

        if isinstance(parent, (ast.If, ast.While, ast.IfExp)) and parent.test is node:
            u.vote("bool_ctx", 1)
            return
        if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, ast.Not):
            u.vote("bool_ctx", 1)
            return
        if isinstance(parent, ast.BoolOp):
            u.vote("bool_ctx", 1)
            return
        if isinstance(parent, ast.comprehension) and node in parent.ifs:
            u.vote("bool_ctx", 1)
            return

        # stored into another record: record["x"] = param  -> nothing to learn

    def _vote_constant(self, u: _Usage, value: Any, weight: int):
        if isinstance(value, bool):
            u.vote("bool", weight)
        elif isinstance(value, (int, float)):
            u.vote("number", weight)
        elif isinstance(value, str):
            u.vote("string", weight)
        elif isinstance(value, list):
            u.vote("list", weight)
        elif isinstance(value, dict):
            u.vote("dict", weight)

    def _analyze_compare(self, node: ast.AST, cmp: ast.Compare, u: _Usage):
        operands = [cmp.left] + cmp.comparators
        for i, op in enumerate(cmp.ops):
            left, right = operands[i], operands[i + 1]
            if node is not left and node is not right:
                continue
            other = right if node is left else left
            if isinstance(op, (ast.In, ast.NotIn)):
                if node is left:
                    # param in <something>
                    choices = None
                    if isinstance(other, (ast.List, ast.Tuple, ast.Set)):
                        choices = [e.value for e in other.elts if isinstance(e, ast.Constant)]
                    elif isinstance(other, ast.Name) and other.id in self.const_lists:
                        choices = self.const_lists[other.id]
                    if choices:
                        for c in choices:
                            self._vote_constant(u, c, 3)
                            if c not in u.choices:
                                u.choices.append(c)
                    else:
                        coll = self._expr_usage(other)
                        if coll is not None and isinstance(node, ast.Name):
                            coll.key_name = coll.key_name or node.id
                            if coll.key_param is None and node.id in self.params:
                                coll.key_param = node.id
                else:
                    # <something> in param
                    u.vote("container", 2)
                    if isinstance(other, ast.Constant) and isinstance(other.value, str) and len(other.value) <= 2:
                        u.vote("string", 1)
                    elif isinstance(other, ast.Name) and other.id in self.params:
                        u.key_param = u.key_param or other.id
                continue
            if isinstance(op, (ast.Is, ast.IsNot)):
                continue
            if isinstance(other, ast.Constant):
                if isinstance(op, (ast.Eq, ast.NotEq)):
                    self._vote_constant(u, other.value, 3)
                    if isinstance(other.value, str) and other.value not in u.choices:
                        u.choices.append(other.value)
                elif other.value is not None:
                    self._vote_constant(u, other.value, 3)
            elif isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                u.vote("number", 2)


# ─── Turning signals into a type ─────────────────────────────

def _decide(u: _Usage, name: str) -> str:
    v = u.votes
    if v.get("dict", 0) >= 3 or (u.items is not None and u.key_param):
        return "dict"
    if u.fields and v.get("iterable", 0) == 0 and v.get("list", 0) == 0:
        return "record"
    if v.get("list", 0) or v.get("iterable", 0) or v.get("sequence", 0):
        if v.get("string", 0) > v.get("list", 0) + v.get("iterable", 0):
            return "string"
        return "list"
    scalar = {k: v.get(k, 0) for k in ("number", "string", "bool")}
    best = max(scalar, key=scalar.get)
    if scalar[best] > 0:
        return best
    if v.get("container", 0) or v.get("sized", 0):
        guess = _guess_from_name(name)
        if guess in ("dict", "list", "string"):
            return guess
        return "list"
    guess = _guess_from_name(name)
    if guess:
        return guess
    if v.get("key", 0):
        return "string"
    if v.get("bool_ctx", 0):
        return "bool"
    return "any"


def _example(u: _Usage, name: str, kind: str, examples: Dict[str, Any], depth: int = 0) -> Any:
    if u.choices:
        usable = [c for c in u.choices if not (isinstance(c, str) and c.lower() in _TERMINAL_STATES)]
        return (usable or u.choices)[0]
    if kind == "number":
        n = _number_from_name(name)
        return n if n is not None else 10
    if kind == "string":
        if name in examples and isinstance(examples[name], str):
            return examples[name]
        if name.endswith("_id") or name == "id":
            return _id_example(name)
        for word, val in _STRING_WORDS.items():
            if name == word or name.endswith("_" + word):
                return val
        return "sample"
    if kind == "bool":
        return True
    if depth > 3:
        return {} if kind in ("dict", "record") else []
    if kind == "record":
        out = {}
        for f, fu in u.fields.items():
            fk = _decide(fu, f)
            out[f] = _example(fu, f, fk, examples, depth + 1) if fk != "any" else "sample"
        return out
    if kind == "dict":
        item = u.items or _Usage()
        item_name = _singular(name)
        item_kind = _decide(item, item_name) if (item.votes or item.fields) else "any"
        key = examples.get(u.key_param) if u.key_param else None
        if not isinstance(key, (str, int)):
            if u.key_name and u.key_name in _STRING_WORDS:
                key = _STRING_WORDS[u.key_name]
            elif u.key_name and u.key_name.endswith("_id"):
                key = _id_example(u.key_name)
            elif depth == 0:
                key = _id_example(item_name + "_id")
            else:
                key = "key1"
        if item_kind == "any":
            return {}
        return {str(key): _example(item, item_name, item_kind, examples, depth + 1)}
    if kind == "list":
        item = u.items or _Usage()
        item_name = _singular(name)
        if not (item.votes or item.fields):
            g = _guess_from_name(item_name)
            if g in ("number", "string"):
                return [_example(item, item_name, g, examples, depth + 1)] * 3 if g == "number" else \
                       [_example(item, item_name, g, examples, depth + 1)]
            return []
        item_kind = _decide(item, item_name)
        ex = _example(item, item_name, item_kind, examples, depth + 1)
        if u.tuple_size:
            if item_kind == "number" and isinstance(ex, (int, float)):
                return [round(ex + i * 0.01, 2) if isinstance(ex, float) else ex + i for i in range(u.tuple_size)]
            return [ex] * u.tuple_size
        if item_kind == "number":
            return [ex, ex * 2 if isinstance(ex, (int, float)) else ex, ex]
        return [ex]
    return None


def _singular(name: str) -> str:
    if name.endswith("ies"):
        return name[:-3] + "y"
    if name.endswith("ses"):
        return name[:-2]
    if name.endswith("s") and not name.endswith("ss"):
        return name[:-1]
    return name + "_item"


def _fields_text(fields) -> str:
    names = list(fields)
    return ", ".join(names[:6]) + (", …" if len(names) > 6 else "")


def _describe(u: _Usage, name: str, kind: str, depth: int = 0) -> str:
    """Plain-English description of what to pass."""
    if kind == "record":
        return f"One record with: {_fields_text(u.fields)}" if u.fields else "A dictionary"
    if kind == "dict":
        item = u.items or _Usage()
        item_kind = _decide(item, _singular(name)) if (item.votes or item.fields) else "any"
        key = u.key_param or u.key_name
        by = f" keyed by {key}" if key else ""
        if item_kind == "record" and item.fields:
            return f"Records{by}, each with: {_fields_text(item.fields)}"
        if item_kind == "any":
            return f"A dictionary{by}" + (" (can be empty: {})" if not item.votes else "")
        return f"A dictionary{by}, values are {_plural(item_kind)}"
    if kind == "list":
        item = u.items or _Usage()
        if item.votes or item.fields:
            item_kind = _decide(item, _singular(name))
            if item_kind == "record" and item.fields:
                return f"A list of records, each with: {_fields_text(item.fields)}"
            if u.tuple_size:
                return f"A pair/tuple of {u.tuple_size} {_plural(item_kind)}"
            return f"A list of {_plural(item_kind)}"
        return "A list"
    return _short(kind)


def _plural(kind: str) -> str:
    return {"string": "texts", "number": "numbers", "bool": "true/false values", "record": "dictionaries",
            "dict": "dictionaries", "list": "lists"}.get(kind, "values")


def _short(kind: str) -> str:
    return {"string": "text", "record": "dict", "any": "any value"}.get(kind, kind)


# ─── Annotation-based hints (libraries) ──────────────────────

_ANN_SIMPLE = {
    "str": ("string", "hello"), "int": ("number", 1), "float": ("number", 1.5),
    "bool": ("bool", True), "bytes": ("string", "hello"), "None": ("null", None),
    "list": ("list", []), "List": ("list", []), "Sequence": ("list", []), "Iterable": ("list", []),
    "Collection": ("list", []), "tuple": ("list", []), "Tuple": ("list", []), "set": ("list", []),
    "Set": ("list", []), "frozenset": ("list", []), "Iterator": ("list", []),
    "dict": ("dict", {}), "Dict": ("dict", {}), "Mapping": ("dict", {}), "MutableMapping": ("dict", {}),
    "Any": ("any", None), "object": ("any", None),
    "PathLike": ("string", "/tmp/example.txt"), "StrPath": ("string", "/tmp/example.txt"),
}
_ANN_ELEM_EXAMPLE = {"str": "hello", "int": 1, "float": 1.5, "bool": True}


def _ann_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        # string annotation, e.g. "Request"
        try:
            return _ann_name(ast.parse(node.value, mode="eval").body)
        except SyntaxError:
            return node.value
    return ""


def _from_annotation(ann: ast.AST):
    """Return (kind, example, choices, json_ok)."""
    if isinstance(ann, ast.Constant) and isinstance(ann.value, str):
        try:
            ann = ast.parse(ann.value, mode="eval").body
        except SyntaxError:
            return "object", None, [], False
    if isinstance(ann, ast.Constant) and ann.value is None:
        return "null", None, [], True
    # X | Y
    if isinstance(ann, ast.BinOp) and isinstance(ann.op, ast.BitOr):
        parts = _flatten_union(ann)
        return _first_usable(parts)
    if isinstance(ann, ast.Subscript):
        outer = _ann_name(ann.value)
        inner = ann.slice
        elts = inner.elts if isinstance(inner, ast.Tuple) else [inner]
        if outer in ("Optional", "Union"):
            return _first_usable(elts)
        if outer == "Literal":
            choices = [e.value for e in elts if isinstance(e, ast.Constant)]
            return ("string" if choices and isinstance(choices[0], str) else "any"), \
                   (choices[0] if choices else None), choices, True
        if outer in ("Annotated", "Final", "ClassVar", "Required", "NotRequired"):
            return _from_annotation(elts[0])
        if outer in ("Callable", "type", "Type"):
            return "object", None, [], False
        if outer in _ANN_SIMPLE:
            kind, ex, _, _ = (*_ANN_SIMPLE[outer], None, None)
            if kind == "list" and elts:
                e = _ann_name(elts[0])
                if e in _ANN_ELEM_EXAMPLE:
                    return "list", [_ANN_ELEM_EXAMPLE[e]], [], True
            if kind == "dict" and len(elts) == 2:
                k, v = _ann_name(elts[0]), _ann_name(elts[1])
                if k == "str" and v in _ANN_ELEM_EXAMPLE:
                    return "dict", {"key": _ANN_ELEM_EXAMPLE[v]}, [], True
            return kind, ex, [], True
        return "object", None, [], False
    name = _ann_name(ann)
    if name in _ANN_SIMPLE:
        kind, ex = _ANN_SIMPLE[name]
        return kind, ex, [], True
    return "object", None, [], False


def _flatten_union(node: ast.AST) -> List[ast.AST]:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return _flatten_union(node.left) + _flatten_union(node.right)
    return [node]


def _first_usable(parts: List[ast.AST]):
    results = [_from_annotation(p) for p in parts]
    for r in results:
        if r[0] not in ("null", "object", "any"):
            return r
    for r in results:
        if r[0] != "null":
            return r
    return results[0] if results else ("any", None, [], True)


# ─── Public API ──────────────────────────────────────────────

def _literal(node: Optional[ast.AST]):
    """(has_literal_value, value) for a default expression."""
    if node is None:
        return False, None
    try:
        value = ast.literal_eval(node)
    except Exception:
        return False, None
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return False, None   # e.g. Ellipsis, sets of objects
    return True, value


def param_hints(func: ast.AST, skip_first: bool = False,
                module_funcs: Optional[Dict[str, ast.AST]] = None) -> List[Dict[str, Any]]:
    """Describe every parameter of `func` (an ast.FunctionDef / AsyncFunctionDef)."""
    a = func.args
    positional = a.posonlyargs + a.args
    pos_defaults = [None] * (len(positional) - len(a.defaults)) + list(a.defaults)

    entries = []  # (arg, kind, default_node)
    for i, arg in enumerate(positional):
        kind = "positional_only" if i < len(a.posonlyargs) else "positional"
        entries.append((arg, kind, pos_defaults[i]))
    if a.vararg:
        entries.append((a.vararg, "var_positional", None))
    for arg, d in zip(a.kwonlyargs, a.kw_defaults):
        entries.append((arg, "keyword_only", d))
    if a.kwarg:
        entries.append((a.kwarg, "var_keyword", None))

    if skip_first and entries and entries[0][1].startswith("positional") and entries[0][0].arg in ("self", "cls"):
        entries = entries[1:]

    usage = _Analyzer(func, [e[0].arg for e in entries], module_funcs).run()
    # plain (unannotated) code: an argument we learn nothing about is most likely text
    unannotated = all(e[0].annotation is None for e in entries)

    # pass 1: everything except collections, so dict keys can reuse id examples
    examples: Dict[str, Any] = {}
    decided: Dict[str, Dict[str, Any]] = {}
    for arg, kind, default in entries:
        name = arg.arg
        u = usage[name]
        has_lit, lit = _literal(default)
        info: Dict[str, Any] = {
            "name": name,
            "kind": kind,
            "required": default is None and kind in ("positional", "positional_only", "keyword_only"),
            "default": ast.unparse(default) if default is not None else None,
            "annotation": ast.unparse(arg.annotation) if arg.annotation is not None else None,
            "choices": [],
            "json_ok": True,
        }
        if kind == "var_positional":
            info.update(type="list", label="extra positional values (JSON list)", example=[], source="signature")
        elif kind == "var_keyword":
            info.update(type="dict", label="extra keyword values (JSON object)", example={}, source="signature")
        elif arg.annotation is not None:
            t, ex, choices, ok = _from_annotation(arg.annotation)
            if has_lit and (lit is not None or ex is None):
                ex = lit
            info.update(type=t, label=info["annotation"], example=ex, choices=choices,
                        json_ok=ok or has_lit, source="type hint")
            if not ok:
                info["note"] = f"Needs a {info['annotation']} object — cannot be typed as JSON" + \
                               (", leave empty to use the default" if default is not None else "")
        elif name in _OBJECT_NAMES and not has_lit:
            info.update(type="object", label="a Python object", example=None, json_ok=False,
                        source="guessed from name",
                        note=f"Needs a real Python {_OBJECT_NAMES[name]} — can't be typed into a form")
        elif has_lit and lit is not None and not u.fields and u.items is None:
            t = _kind_of_value(lit)
            info.update(type=t, label=_short(t), example=lit, source="default value")
            info["choices"] = u.choices
        else:
            t = _decide(u, name)
            if t == "any" and has_lit and lit is None:
                t = _guess_from_name(name) or "any"
            info.update(type=t, label=None, source="inferred from code" if u.votes else "guessed from name")
            if not u.votes and t == "any":
                if unannotated:
                    t = "string"
                    info.update(type=t, source="guessed (unused or passed through)")
                else:
                    info["source"] = "unknown"
            info["choices"] = u.choices
        if info["type"] in ("number", "string", "bool"):
            if "example" not in info:
                info["example"] = _example(u, name, info["type"], examples)
            examples[name] = info["example"]
        decided[name] = info

    # pass 2: collections and anything still missing an example
    for arg, kind, default in entries:
        name = arg.arg
        info = decided[name]
        u = usage[name]
        if "example" not in info:
            info["example"] = _example(u, name, info["type"], examples)
        if info.get("label") is None:
            info["label"] = _describe(u, name, info["type"])
        info["example_json"] = json.dumps(info["example"], ensure_ascii=False) \
            if info["json_ok"] and info["example"] is not None or info["type"] == "null" else ""
    return [decided[e[0].arg] for e in entries]


def _kind_of_value(v: Any) -> str:
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, (list, tuple, set)):
        return "list"
    if isinstance(v, dict):
        return "dict"
    return "any"
