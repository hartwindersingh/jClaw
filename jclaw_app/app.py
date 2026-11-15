"""Desktop interface for jClaw Engineering Suite.

Developer: Hartwinder Singh
Copyright (c) 2026 Hartwinder Singh
"""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .metadata import APP_NAME, APP_VERSION, DEVELOPER, COPYRIGHT, LICENSE
from .core import scanner, git_ops, ollama_client, runner, audit


class JClawApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1080x720")
        self.minsize(820, 560)
        self.project = None
        self.report = None
        menu = tk.Menu(self)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="About jClaw", command=self.about)
        menu.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu)
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Button(top, text="Choose Project", command=self.choose_project).pack(side="left")
        self.path_label = ttk.Label(top, text="No project selected")
        self.path_label.pack(side="left", padx=10, fill="x", expand=True)
        actions = ttk.Frame(self, padding=(10, 0, 10, 10))
        actions.pack(fill="x")
        for label, callback in (("Scan Project", self.scan), ("Git Status", self.show_status),
                                ("Git Diff", self.show_diff), ("Run Tests", self.run_tests)):
            ttk.Button(actions, text=label, command=callback).pack(side="left", padx=(0, 6))
        self.output = tk.Text(self, wrap="word", font=("Consolas", 10), padx=10, pady=10)
        self.output.pack(fill="both", expand=True, padx=10, pady=5)
        chat = ttk.LabelFrame(self, text="Ask Local Model (Ollama)", padding=8)
        chat.pack(fill="x", padx=10, pady=10)
        row = ttk.Frame(chat)
        row.pack(fill="x")
        self.model_var = tk.StringVar()
        self.models = ttk.Combobox(row, textvariable=self.model_var, state="readonly", width=34)
        self.models.pack(side="left")
        ttk.Button(row, text="Refresh Models", command=self.refresh_models).pack(side="left", padx=6)
        self.prompt_var = tk.StringVar()
        entry = ttk.Entry(chat, textvariable=self.prompt_var)
        entry.pack(fill="x", pady=7)
        entry.bind("<Return>", lambda _event: self.ask())
        ttk.Button(chat, text="Ask", command=self.ask).pack(anchor="e")
        self.write("Welcome to jClaw. Choose a project folder to begin.")

    def write(self, value):
        self.output.insert("end", value + ("" if value.endswith("\n") else "\n"))
        self.output.see("end")

    def choose_project(self):
        chosen = filedialog.askdirectory(title="Select project folder")
        if chosen:
            self.project = Path(chosen)
            self.report = None
            self.path_label.config(text=str(self.project))
            audit.record("project_selected", {"path": str(self.project)})
            self.write(f"Project selected: {self.project}")

    def require_project(self):
        if self.project is None:
            messagebox.showinfo(APP_NAME, "Choose a project folder first.")
            return False
        return True

    def scan(self):
        if not self.require_project():
            return
        try:
            self.report = scanner.scan_project(self.project)
            self.write(scanner.format_summary(self.report))
            audit.record("project_scanned", {"path": str(self.project), "files": self.report["file_count"]})
        except Exception as exc:
            messagebox.showerror("Scan failed", str(exc))

    def show_status(self):
        if self.require_project():
            try:
                self.write("Git status:\n" + git_ops.status(self.project))
            except Exception as exc:
                messagebox.showerror("Git status unavailable", str(exc))

    def show_diff(self):
        if self.require_project():
            try:
                self.write("Git diff:\n" + (git_ops.diff(self.project) or "No changes detected."))
            except Exception as exc:
                messagebox.showerror("Git diff unavailable", str(exc))

    def run_tests(self):
        if not self.require_project():
            return
        if not messagebox.askyesno("Run tests", "Tests can execute project code. Run tests only for a project you trust. Continue?"):
            return
        code, output = runner.run_tests(self.project)
        self.write(f"Test exit code: {code}\n{output}")
        audit.record("tests_run", {"path": str(self.project), "exit_code": code})

    def refresh_models(self):
        try:
            names = ollama_client.list_models()
            self.models["values"] = names
            if names:
                self.model_var.set(names[0])
            self.write("Ollama models: " + (", ".join(names) if names else "No downloaded models found."))
        except Exception as exc:
            messagebox.showerror("Ollama unavailable", str(exc))

    def ask(self):
        prompt, model = self.prompt_var.get().strip(), self.model_var.get().strip()
        if not prompt:
            return
        if not model:
            messagebox.showinfo("Select a model", "Refresh models and select a downloaded Ollama model first.")
            return
        context = scanner.format_summary(self.report) if self.report else ""
        self.write(f"You: {prompt}\nWorking with local model {model}...")
        self.update_idletasks()
        try:
            answer = ollama_client.chat(model, prompt, context)
            self.write("jClaw: " + answer)
            audit.record("local_model_chat", {"model": model})
        except Exception as exc:
            messagebox.showerror("Local model request failed", str(exc))
        self.prompt_var.set("")

    def about(self):
        messagebox.showinfo(f"About {APP_NAME}",
            f"{APP_NAME}\nVersion {APP_VERSION}\n\n"
            "A local-first workspace for repository inspection, Git review, testing and local-model assistance.\n\n"
            f"Developer: {DEVELOPER}\n{COPYRIGHT}\nLicence: {LICENSE}\n\n"
            "Designed to complement OpenClaw; not affiliated with or endorsed by OpenClaw or Anthropic.")


def main():
    JClawApp().mainloop()


if __name__ == "__main__":
    main()
