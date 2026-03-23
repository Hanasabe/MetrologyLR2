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
        "match_expression",
        "break_expression",
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
        "+", "-", "*", "/", "%",
        "==", "!=", "<", "<=", ">", ">=",
        "&&", "||", "!",
        "&", "|", "^", "<<", ">>",
        "=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=",
        "..", "..=",
        "as", "?",
        "=>",
    }

    def __init__(self):
        self.total_operators = 0
        self.conditional_operators = 0
        self.max_nesting_level = 0
        self.current_nesting = 0
        self.operator_breakdown = Counter()

    def visit_controls(self, node):
        """
        Считает управляющие конструкции по узлам дерева.
        """
        if node is None:
            return

        node_type = node.type

        if node_type in self.CONTROL_NODES:
            self.total_operators += 1
            self.conditional_operators += 1
            self.operator_breakdown[node_type] += 1

            if node_type in self.NESTING_NODES:
                self.current_nesting += 1
                self.max_nesting_level = max(self.max_nesting_level, self.current_nesting)

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
        relative_complexity = (
            absolute_complexity / self.total_operators
            if self.total_operators > 0 else 0
        )

        return {
            "Абсолютная сложность (CL)": absolute_complexity,
            "Относительная сложность (cl)": round(relative_complexity, 4),
            "Макс. уровень вложенности (CLI)": self.max_nesting_level,
            "Всего операторов": self.total_operators,
        }, self.operator_breakdown