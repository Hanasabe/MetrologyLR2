import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from collections import Counter

import pyperclip
from tabulate import tabulate
from tree_sitter import Language, Parser
import tree_sitter_rust as rust_language


# Совместимая инициализация языка Rust для tree-sitter
try:
    RUST_LANGUAGE = Language(rust_language.language())
except TypeError:
    RUST_LANGUAGE = Language(rust_language.language)

PARSER = Parser()
try:
    PARSER.language = RUST_LANGUAGE
except AttributeError:
    PARSER.set_language(RUST_LANGUAGE)


class RustGilbMetricsAnalyzer:
    """
    Анализ метрик Джилба для Rust-кода.
    """

    CONTROL_NODES = {
        "if_expression",
        "while_expression",
        "while_let_expression",
        "for_expression",
        "loop_expression",
        #"match_expression",
        # "break_expression",
        "continue_expression",
        "return_expression",
        "yield_expression",
        "try_expression",
        "await_expression",
    }

    NESTING_NODES = {
        "if_expression",
        "while_expression",
        "while_let_expression",
        "for_expression",
        "loop_expression",
        "match_expression",
    }

    # Конкретные символы и ключевые токены Rust
    OPERATOR_SYMBOLS = {
        "+",
        "-",
        "*",
        "/",
        "%",
        "==",
        "!=",
        "<",
        "<=",
        ">",
        ">=",
        "&&",
        "||",
        "!",
        "&",
        "|",
        "^",
        "<<",
        ">>",
        "=",
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "&=",
        "|=",
        "^=",
        "<<=",
        ">>=",
        "..",
        "..=",
        "as",
        "?",
        "=>",
    }

    CONDITIONAL_KEYWORDS = {
    "if",
    #"else",
    #"match",
    }

    def __init__(self):
        self.total_operators = 0
        self.conditional_operators = 0
        self.max_nesting_level = 0
        self.current_nesting = -1
        self.operator_breakdown = Counter()

    def visit_controls(self, node):
        """
        Считает управляющие конструкции по узлам дерева.
        """
        if node is None:
            return
        
        if node.type == "match_expression":
            match_block = next((child for child in node.children if child.type == "match_block"),None)
            arms = []
            if match_block:
                arms = [child for child in match_block.children if child.type == "match_arm"]
            arm_count = len(arms)

            if arm_count > 0:
                # # считаем каждую ветку как условную конструкцию
                # self.total_operators += arm_count
                # self.conditional_operators += arm_count
                # self.operator_breakdown["match_arm"] += arm_count

                # увеличиваем вложенность СРАЗУ на количество веток
                self.current_nesting += arm_count
                self.max_nesting_level = max(
                    self.max_nesting_level, self.current_nesting
                )

            # обходим содержимое без повторного учета match_arm
            for child in node.children:
                if child.type != "match_arm":
                    self.visit_controls(child)
                else:
                    # внутри ветки просто идем дальше без увеличения вложенности
                    for sub in child.children:
                        self.visit_controls(sub)

            if arm_count > 0:
                self.current_nesting -= arm_count

            if node.type in self.CONTROL_NODES:
                self.total_operators += 1
                self.conditional_operators += 1
                self.operator_breakdown[node_type] += 1

            return

        node_type = node.type

        if node_type in self.CONTROL_NODES:
            self.total_operators += 1
            
            if node_type != "if_expression" and node_type != "while_expression" and node_type != "for_expression" and node_type != "loop_expression":
                
                self.conditional_operators += 1
                self.operator_breakdown[node_type] += 1

            if node_type in self.NESTING_NODES:
                self.current_nesting += 1
                self.max_nesting_level = max(
                    self.max_nesting_level, self.current_nesting
                )

                for child in node.children:
                    self.visit_controls(child)

                self.current_nesting -= 1
                return

        for child in node.children:
            self.visit_controls(child)

    def count_symbol_operators(self, node):
        """
        Считает реальные символы операторов из текста исходника.
        """
        if node is None:
            return

        # Лист дерева — у него есть конкретный текст токена
        if node.child_count == 0:
            token = node.text.decode("utf-8")

            # if token in self.CONDITIONAL_KEYWORDS:
            #     self.conditional_operators += 1
            #     self.operator_breakdown[token] += 1

            # parent_type = node.parent.type if node.parent else None

            # # Игнорируем ! в макросах (println!, vec! и т.д.)
            # if token == "!" and parent_type == "macro_invocation":
            #     return

            if token in self.OPERATOR_SYMBOLS:
                self.total_operators += 1
                self.operator_breakdown[token] += 1

                # Если хочешь считать => как оператор ветвления
                if token == "=>":
                    self.conditional_operators += 1
   

            return

        for child in node.children:
            self.count_symbol_operators(child)

    def calculate_metrics(self, code):
        tree = PARSER.parse(code.encode("utf-8"))
        root = tree.root_node

        self.visit_controls(root)
        self.count_symbol_operators(root)

        absolute_complexity = self.conditional_operators
        absolute_complexity += code.count("if")
        absolute_complexity += code.count("for")
        absolute_complexity += code.count("while")
        absolute_complexity += code.count("loop")
        absolute_complexity -= code.count("_ =>")
        relative_complexity = (
            absolute_complexity / self.total_operators
            if self.total_operators > 0
            else 0
        )

        return {
            "Абсолютная сложность (CL)": absolute_complexity,
            "Относительная сложность (cl)": round(relative_complexity, 4),
            "Макс. уровень вложенности (CLI)": self.max_nesting_level,
            "Всего операторов": self.total_operators,
        }, self.operator_breakdown
