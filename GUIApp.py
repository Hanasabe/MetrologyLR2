import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
from parser import RustGilbMetricsAnalyzer


class GilbMetricsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор метрик Джилба (Rust)")
        self.root.configure(bg="#999999")
        self.root.geometry("712x500")
        self.root.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            width=50,
            height=25,
            wrap="none",
            font=("Consolas", 10)
        )
        self.text_area.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        self.text_area.insert("1.0", "Введите код на Rust для анализа...")

        btn_frame = tk.Frame(main_frame, bg="#ffffff")
        btn_frame.grid(row=1, column=0, pady=4)

        tk.Button(
            btn_frame,
            text="Открыть файл",
            command=self.load_file,
            width=25
        ).grid(row=0, column=0, padx=2)

        tk.Button(
            btn_frame,
            text="Рассчитать метрики",
            command=self.analyze_code,
            width=25
        ).grid(row=0, column=1, padx=2)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=1, rowspan=2, padx=4, pady=4, sticky="nsew")

        metrics_frame = tk.Frame(self.notebook)
        self.metrics_tree = ttk.Treeview(
            metrics_frame,
            columns=("metric", "value"),
            show="headings",
            height=20
        )
        self.metrics_tree.heading("metric", text="Метрика")
        self.metrics_tree.heading("value", text="Значение")
        self.metrics_tree.column("metric", width=220, anchor="w")
        self.metrics_tree.column("value", width=120, anchor="center")
        self.metrics_tree.pack(fill="both", expand=True)

        self.notebook.add(metrics_frame, text="Метрики")

        breakdown_frame = tk.Frame(self.notebook)
        self.breakdown_tree = ttk.Treeview(
            breakdown_frame,
            columns=("type", "count"),
            show="headings",
            height=20
        )
        self.breakdown_tree.heading("type", text="Тип узла")
        self.breakdown_tree.heading("count", text="Количество")
        self.breakdown_tree.column("type", width=220, anchor="w")
        self.breakdown_tree.column("count", width=120, anchor="center")
        self.breakdown_tree.pack(fill="both", expand=True)

        self.notebook.add(breakdown_frame, text="Разбиение")

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def load_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Rust files", "*.rs"), ("All files", "*.*")]
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, f.read())

    def analyze_code(self):
        code = self.text_area.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Ошибка", "Введите код для анализа")
            return

        try:
            analyzer = RustGilbMetricsAnalyzer()
            metrics, breakdown = analyzer.calculate_metrics(code)

            for item in self.metrics_tree.get_children():
                self.metrics_tree.delete(item)
            for key, value in metrics.items():
                self.metrics_tree.insert("", tk.END, values=(key, value))

            for item in self.breakdown_tree.get_children():
                self.breakdown_tree.delete(item)
            if breakdown:
                for key, value in breakdown.most_common():
                    self.breakdown_tree.insert("", tk.END, values=(key, value))

            self.notebook.select(0)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при анализе кода: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GilbMetricsApp(root)
    root.mainloop()