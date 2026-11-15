"""Desktop interface for jClaw Engineering Suite.

Developer: Hartwinder Singh
Copyright (c) 2026 Hartwinder Singh
"""
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .metadata import APP_NAME, APP_VERSION, DEVELOPER, COPYRIGHT, LICENSE
from .core import scanner, git_ops, ollama_client, runner, audit, openclaw_client


class JClawApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1120x800")
        self.minsize(860, 620)
        self.project = None
        self.report = None
        self.events = queue.Queue()
        self._build_menu()
        self._build_project_bar()
        self._build_tabs()
        self.after(120, self._poll_events)
        self.write("Welcome to jClaw. Choose a project folder to begin.")

    def _build_menu(self):
        menu = tk.Menu(self)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="About jClaw", command=self.about)
        menu.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu)

    def _build_project_bar(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Button(top, text="Choose Project", command=self.choose_project).pack(side="left")
        self.path_label = ttk.Label(top, text="No project selected")
        self.path_label.pack(side="left", padx=10, fill="x", expand=True)
        actions = ttk.Frame(self, padding=(10, 0, 10, 8))
        actions.pack(fill="x")
        for label, callback in (("Scan Project", self.scan), ("Git Status", self.show_status),
                                ("Git Diff", self.show_diff), ("Run Tests", self.run_tests)):
            ttk.Button(actions, text=label, command=callback).pack(side="left", padx=(0, 6))

    def _build_tabs(self):
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=10, pady=5)
        local = ttk.Frame(tabs, padding=8)
        cloud = ttk.Frame(tabs, padding=8)
        tabs.add(local, text="Local Ollama")
        tabs.add(cloud, text="OpenClaw Gateway")
        self.output = tk.Text(local, wrap="word", font=("Consolas", 10), padx=10, pady=10, height=20)
        self.output.pack(fill="both", expand=True)
        row = ttk.Frame(local)
        row.pack(fill="x", pady=(8, 0))
        self.model_var = tk.StringVar()
        self.models = ttk.Combobox(row, textvariable=self.model_var, state="readonly", width=34)
        self.models.pack(side="left")
        ttk.Button(row, text="Refresh Models", command=self.refresh_models).pack(side="left", padx=6)
        self.prompt_var = tk.StringVar()
        ttk.Entry(local, textvariable=self.prompt_var).pack(fill="x", pady=7)
        ttk.Button(local, text="Ask Local Model", command=self.ask_local).pack(anchor="e")

        settings = ttk.LabelFrame(cloud, text="Gateway connection", padding=10)
        settings.pack(fill="x")
        self.cli_var = tk.StringVar(value="openclaw")
        self.agent_var = tk.StringVar(value="main")
        self.session_var = tk.StringVar(value="jclaw-engineering")
        ttk.Label(settings, text="OpenClaw CLI path").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(settings, textvariable=self.cli_var, width=48).grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        ttk.Label(settings, text="Agent ID").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(settings, textvariable=self.agent_var, width=24).grid(row=1, column=1, sticky="w", padx=4, pady=4)
        ttk.Label(settings, text="Session key (optional)").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(settings, textvariable=self.session_var, width=32).grid(row=2, column=1, sticky="w", padx=4, pady=4)
        settings.columnconfigure(1, weight=1)
        buttons = ttk.Frame(cloud)
        buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Check Gateway", command=self.check_gateway).pack(side="left")
        ttk.Label(buttons, text="Agent turns are sent through OpenClaw's configured Gateway.").pack(side="left", padx=10)
        self.oc_output = tk.Text(cloud, wrap="word", font=("Consolas", 10), padx=10, pady=10, height=18)
        self.oc_output.pack(fill="both", expand=True)
        self.oc_prompt = tk.StringVar()
        ttk.Entry(cloud, textvariable=self.oc_prompt).pack(fill="x", pady=7)
        ttk.Button(cloud, text="Send Engineering Task to OpenClaw", command=self.ask_openclaw).pack(anchor="e")

    def write(self, value):
        self.output.insert("end", value + ("" if value.endswith("\n") else "\n"))
        self.output.see("end")

    def _write_oc(self, value):
        self.oc_output.insert("end", value + ("" if value.endswith("\n") else "\n"))
        self.oc_output.see("end")

    def _background(self, label, function):
        self._write_oc(label + " …")
        def work():
            try:
                value = function()
                self.events.put(("ok", label, value))
            except Exception as exc:
                self.events.put(("error", label, str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def _poll_events(self):
        try:
            while True:
                kind, label, value = self.events.get_nowait()
                if kind in ("ok", "local"):
                    self._write_oc(label + " completed:\n" + str(value))
                else:
                    self._write_oc(label + " failed:\n" + str(value))
        except queue.Empty:
            pass
        self.after(120, self._poll_events)

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

    def ask_local(self):
        prompt, model = self.prompt_var.get().strip(), self.model_var.get().strip()
        if not prompt:
            return
        if not model:
            messagebox.showinfo("Select a model", "Refresh models and select a downloaded Ollama model first.")
            return
        context = scanner.format_summary(self.report) if self.report else ""
        self.write(f"You: {prompt}\nWorking with local model {model}...")
        def work():
            try:
                answer = ollama_client.chat(model, prompt, context)
                self.events.put(("local", "Local model", answer))
                audit.record("local_model_chat", {"model": model})
            except Exception as exc:
                self.events.put(("local_error", "Local model", str(exc)))
        threading.Thread(target=work, daemon=True).start()
        self.prompt_var.set("")

    def check_gateway(self):
        executable = self.cli_var.get().strip() or None
        self._background("Gateway status", lambda: openclaw_client.gateway_status(executable))

    def ask_openclaw(self):
        prompt = self.oc_prompt.get().strip()
        if not prompt:
            return
        agent = self.agent_var.get().strip() or "main"
        session = self.session_var.get().strip() or None
        context = scanner.format_summary(self.report) if self.report else "No project scan has been run."
        project = str(self.project) if self.project else "No local project folder selected."
        task = ("You are assisting from jClaw Engineering Suite, a software-engineering workspace. "
                "The selected local project path is: " + project + "\n"
                "Project inventory context (metadata only; not full source):\n" + context[:18000] +
                "\n\nUser's engineering request:\n" + prompt +
                "\n\nDo not claim to have read local files unless your configured OpenClaw tools can access this path. "
                "Do not modify files, run commands, install packages, or publish changes without explicit user approval.")
        self._write_oc("You: " + prompt)
        executable = self.cli_var.get().strip() or None
        cwd = str(self.project) if self.project else None
        self._background("OpenClaw agent", lambda: openclaw_client.ask_agent(
            task, agent_id=agent, session_key=session, executable=executable, cwd=cwd))
        audit.record("openclaw_task_submitted", {"agent": agent, "project": project})
        self.oc_prompt.set("")

    def about(self):
        messagebox.showinfo(f"About {APP_NAME}",
            f"{APP_NAME}\nVersion {APP_VERSION}\n\n"
            "A local-first engineering workspace with OpenClaw Gateway agent delegation and local Ollama assistance.\n\n"
            f"Developer: {DEVELOPER}\n{COPYRIGHT}\nLicence: {LICENSE}\n\n"
            "jClaw is an independent project and is not affiliated with or endorsed by OpenClaw or Anthropic.")


def main():
    JClawApp().mainloop()


if __name__ == "__main__":
    main()
