# OHM'S LAW & POWER CALCULATOR
# ND1 Mechatronics Engineering mini project.
# This standalone application uses Python's built-in Tkinter library.
# Run: python ohms_law.py

import csv
import math
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk


# Every calculation mode has two known inputs and a displayed formula.
# Keeping these in one place makes it easy to update the interface.
METHODS = {
    "Voltage": [
        ("Current and resistance", "Current", "Resistance", "V = I × R"),
        ("Power and current", "Power", "Current", "V = P ÷ I"),
        ("Power and resistance", "Power", "Resistance", "V = √(P × R)"),
    ],
    "Current": [
        ("Voltage and resistance", "Voltage", "Resistance", "I = V ÷ R"),
        ("Power and voltage", "Power", "Voltage", "I = P ÷ V"),
        ("Power and resistance", "Power", "Resistance", "I = √(P ÷ R)"),
    ],
    "Resistance": [
        ("Voltage and current", "Voltage", "Current", "R = V ÷ I"),
        ("Voltage and power", "Voltage", "Power", "R = V² ÷ P"),
        ("Power and current", "Power", "Current", "R = P ÷ I²"),
    ],
    "Power": [
        ("Voltage and current", "Voltage", "Current", "P = V × I"),
        ("Current and resistance", "Current", "Resistance", "P = I² × R"),
        ("Voltage and resistance", "Voltage", "Resistance", "P = V² ÷ R"),
    ],
}

UNITS = {"Voltage": "V", "Current": "A", "Resistance": "Ω", "Power": "W"}
SYMBOLS = {"Voltage": "V", "Current": "I", "Resistance": "R", "Power": "P"}


# This function deliberately converts typed strings with float(), as required.
def parse_number(raw_text, field_name):
    try:
        number = float(raw_text.strip())
    except (ValueError, AttributeError):
        raise ValueError(f"Enter a valid number for {field_name.lower()}.") from None
    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be a finite number.")
    if number < 0:
        raise ValueError(f"{field_name} cannot be negative in this basic DC model.")
    return number


def calculate_electrical(target, method_index, a, b):
    """Return a correct electrical result for one of the 12 formulas.

    a and b are values in the order shown by METHODS[target][method_index].
    """
    if target not in METHODS:
        raise ValueError("Choose voltage, current, resistance, or power.")
    if not isinstance(method_index, int) or method_index not in range(3):
        raise ValueError("Choose a valid calculation method.")
    if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in (a, b)):
        raise ValueError("Both inputs must be finite numbers.")
    if a < 0 or b < 0:
        raise ValueError("Negative values are outside this basic DC model.")

    # if/elif/else keeps the formulas explicit and explainable in a presentation.
    if target == "Voltage":
        if method_index == 0:
            result = a * b
        elif method_index == 1:
            result = safe_divide(a, b, "Current must be above zero to find voltage from power.")
        else:
            result = math.sqrt(a * b)
    elif target == "Current":
        if method_index == 0:
            result = safe_divide(a, b, "Resistance must be above zero to calculate current.")
        elif method_index == 1:
            result = safe_divide(a, b, "Voltage must be above zero to find current from power.")
        else:
            result = math.sqrt(safe_divide(a, b, "Resistance must be above zero."))
    elif target == "Resistance":
        if method_index == 0:
            result = safe_divide(a, b, "Current must be above zero to calculate resistance.")
        elif method_index == 1:
            result = safe_divide(a * a, b, "Power must be above zero to calculate resistance.")
        else:
            result = safe_divide(a, b * b, "Current must be above zero to calculate resistance.")
    else:  # target == "Power"
        if method_index == 0:
            result = a * b
        elif method_index == 1:
            result = a * a * b
        else:
            result = safe_divide(a * a, b, "Resistance must be above zero to calculate power.")

    if not math.isfinite(result):
        raise ValueError("The result is too large; use smaller input values.")
    return result


def safe_divide(numerator, denominator, message):
    if denominator == 0:
        raise ValueError(message)
    return numerator / denominator


def derive_metrics(target, method_index, a, b, result):
    """Fill in other circuit values when they are mathematically determined."""
    specification = METHODS[target][method_index]
    values = {specification[1]: a, specification[2]: b, target: result}

    # Iterate so that a newly discovered value can unlock another formula.
    for _ in range(4):
        v, i, r, p = (values.get(key) for key in ("Voltage", "Current", "Resistance", "Power"))
        if "Voltage" not in values and i is not None and r is not None:
            values["Voltage"] = i * r
        if "Current" not in values and v is not None and r is not None and r != 0:
            values["Current"] = v / r
        if "Resistance" not in values and v is not None and i is not None and i != 0:
            values["Resistance"] = v / i
        if "Power" not in values:
            if v is not None and i is not None:
                values["Power"] = v * i
            elif i is not None and r is not None:
                values["Power"] = i * i * r
    return {key: values.get(key) for key in UNITS}


def display_quantity(value, unit):
    """Format results with readable engineering prefixes without changing math."""
    if value is None or not math.isfinite(value):
        return "—"
    if value == 0:
        return f"0 {unit}"
    for threshold, prefix in ((1e9, "G"), (1e6, "M"), (1e3, "k"),
                              (1, ""), (1e-3, "m"), (1e-6, "µ"), (1e-9, "n")):
        if abs(value) >= threshold:
            return f"{value / threshold:.5g} {prefix}{unit}"
    return f"{value:.4e} {unit}"


def substituted_formula(target, method_index, a, b):
    """Show the actual numbers in the chosen equation, not only the answer."""
    symbol = SYMBOLS[target]
    if method_index == 0:
        if target in ("Current", "Resistance"):
            expression = f"{a:g} ÷ {b:g}"
        elif target == "Power":
            expression = f"{a:g} × {b:g}"
        else:
            expression = f"{a:g} × {b:g}"
    elif method_index == 1:
        if target == "Voltage" or target == "Current":
            expression = f"{a:g} ÷ {b:g}"
        elif target == "Resistance":
            expression = f"{a:g}² ÷ {b:g}"
        else:
            expression = f"{a:g}² × {b:g}"
    else:
        if target == "Voltage":
            expression = f"√({a:g} × {b:g})"
        elif target == "Current":
            expression = f"√({a:g} ÷ {b:g})"
        elif target == "Resistance":
            expression = f"{a:g} ÷ {b:g}²"
        else:
            expression = f"{a:g}² ÷ {b:g}"
    return f"{symbol} = {expression}"


# Colors have roles: cyan = active electrical quantity; amber = power/caution.
BG = "#0B1320"
SURFACE = "#132235"
SURFACE_ALT = "#1A2C40"
BORDER = "#2B4158"
TEXT = "#F0F5F9"
MUTED = "#9AAFC0"
ACCENT = "#50DBE7"
AMBER = "#F3B868"
GREEN = "#79DAB4"
ERROR = "#FF9696"
FONT = "DejaVu Sans"


class OhmsApp(tk.Tk):
    """A single-screen workbench: choose → enter → calculate → review."""

    def __init__(self):
        super().__init__()
        self.title("VoltLab | Ohm's Law & Power")
        self.geometry("1250x740")
        self.minsize(1060, 710)
        self.configure(bg=BG)
        self.target = "Voltage"
        self.mode_index = 0
        self.history = []
        self.metric_labels = {}
        self.result_value = None
        self.live_metrics = {name: None for name in UNITS}
        self.animation_phase = 0.0
        self.flow_paused = False
        self.make_styles()
        self.build_header()
        self.build_body()
        self.choose_target("Voltage")
        self.bind("<Return>", lambda event: self.calculate())
        self.bind("<Escape>", lambda event: self.reset_inputs())
        self.bind("<Control-Shift-C>", lambda event: self.copy_result())
        # A single repeating Tkinter callback keeps the illustration moving.
        self.after(50, self.animate_current_flow)

    def make_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("History.Treeview", background=SURFACE, foreground=TEXT,
                        fieldbackground=SURFACE, borderwidth=0, rowheight=33,
                        font=(FONT, 10))
        style.configure("History.Treeview.Heading", background=SURFACE_ALT,
                        foreground=MUTED, font=(FONT, 9, "bold"), borderwidth=0)
        style.map("History.Treeview", background=[("selected", "#254A60")],
                  foreground=[("selected", "#FFFFFF")])
        style.configure("Mode.TCombobox", padding=7, fieldbackground=SURFACE_ALT,
                        background=SURFACE_ALT, foreground=TEXT)
        style.map("Mode.TCombobox",
                  fieldbackground=[("readonly", SURFACE_ALT)],
                  foreground=[("readonly", TEXT)],
                  selectbackground=[("readonly", SURFACE_ALT)],
                  selectforeground=[("readonly", TEXT)])
        self.option_add("*TCombobox*Listbox.background", SURFACE_ALT)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)

    def label(self, parent, text, size=11, color=TEXT, weight="normal", **kwargs):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=(FONT, size, weight), **kwargs)

    def panel(self, parent, **kwargs):
        return tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER,
                        highlightthickness=1, **kwargs)

    def button(self, parent, text, command, bg=ACCENT, fg=BG, width=None):
        option = {"text": text, "command": command, "bg": bg, "fg": fg,
                  "activebackground": bg, "activeforeground": fg,
                  "relief": "flat", "bd": 0, "cursor": "hand2",
                  "font": (FONT, 10, "bold"), "padx": 15, "pady": 11}
        if width is not None:
            option["width"] = width
        return tk.Button(parent, **option)

    def build_header(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=30, pady=(24, 15))
        logo = tk.Frame(header, bg=ACCENT, width=49, height=49)
        logo.pack(side="left")
        logo.pack_propagate(False)
        tk.Label(logo, text="Ω", bg=ACCENT, fg=BG,
                 font=(FONT, 22, "bold")).pack(expand=True)
        title_block = tk.Frame(header, bg=BG)
        title_block.pack(side="left", padx=16)
        self.label(title_block, "VOLTLAB", 19, TEXT, "bold").pack(anchor="w")
        self.label(title_block, "OHM'S LAW  /  POWER WORKBENCH", 9, MUTED,
                   "bold").pack(anchor="w", pady=(3, 0))
        right = tk.Frame(header, bg=BG)
        right.pack(side="right")
        self.label(right, "IDEAL DC RESISTIVE CIRCUITS", 9, ACCENT,
                   "bold").pack(anchor="e")
        self.label(right, "ENTER calculate    •    ESC clear", 9, MUTED).pack(
            anchor="e", pady=(5, 0))

    def build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        body.columnconfigure(0, weight=6)
        body.columnconfigure(1, weight=4)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=6)
        right.rowconfigure(1, weight=4)

        self.build_calculator(left)
        self.build_history(left)
        self.build_visual(right)
        self.build_metrics(right)

    def build_calculator(self, parent):
        card = self.panel(parent)
        card.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        wrap = tk.Frame(card, bg=SURFACE)
        wrap.pack(fill="both", expand=True, padx=23, pady=20)
        self.label(wrap, "01  /  SELECT WHAT TO CALCULATE", 9, ACCENT,
                   "bold").pack(anchor="w", pady=(0, 13))

        options = tk.Frame(wrap, bg=SURFACE)
        options.pack(fill="x")
        self.target_buttons = {}
        for index, (name, symbol) in enumerate(SYMBOLS.items()):
            options.columnconfigure(index, weight=1)
            b = tk.Button(options, text=f"{symbol}\n{name}", height=2,
                          command=lambda n=name: self.choose_target(n),
                          font=(FONT, 10, "bold"), relief="flat", bd=0,
                          cursor="hand2", padx=8, pady=8,
                          activeforeground=TEXT, highlightthickness=0)
            b.grid(row=0, column=index, padx=(0 if index == 0 else 5, 0),
                   sticky="ew")
            self.target_buttons[name] = b

        method_header = tk.Frame(wrap, bg=SURFACE)
        method_header.pack(fill="x", pady=(20, 8))
        self.label(method_header, "02  /  USE THESE KNOWN VALUES", 9,
                   ACCENT, "bold").pack(side="left")
        self.method_var = tk.StringVar()
        self.method_box = ttk.Combobox(wrap, textvariable=self.method_var,
                                      state="readonly", style="Mode.TCombobox",
                                      font=(FONT, 11))
        self.method_box.pack(fill="x")
        self.method_box.bind("<<ComboboxSelected>>", self.method_changed)

        input_row = tk.Frame(wrap, bg=SURFACE)
        input_row.pack(fill="x", pady=(17, 0))
        self.entries = []
        self.field_titles = []
        for j in range(2):
            column = tk.Frame(input_row, bg=SURFACE)
            column.pack(side="left", fill="x", expand=True,
                        padx=(0, 8) if j == 0 else (8, 0))
            field_title = self.label(column, "", 10, MUTED, "bold")
            field_title.pack(anchor="w", pady=(0, 8))
            entry = tk.Entry(column, bg=SURFACE_ALT, fg=TEXT, insertbackground=ACCENT,
                             font=(FONT, 16), relief="flat", bd=0,
                             highlightthickness=1, highlightbackground=BORDER,
                             highlightcolor=ACCENT, justify="left")
            entry.pack(fill="x", ipady=10, ipadx=12)
            self.entries.append(entry)
            self.field_titles.append(field_title)

        action = tk.Frame(wrap, bg=SURFACE)
        action.pack(fill="x", pady=(17, 0))
        self.button(action, "CALCULATE  →", self.calculate).pack(
            side="left", fill="x", expand=True)
        self.button(action, "RESET", self.reset_inputs, bg=SURFACE_ALT,
                    fg=TEXT).pack(side="left", padx=(10, 0))
        self.status = self.label(wrap, "", 10, MUTED, wraplength=600,
                                 justify="left")
        self.status.pack(fill="x", anchor="w", pady=(14, 0))

    def build_history(self, parent):
        history_card = self.panel(parent)
        history_card.grid(row=1, column=0, sticky="nsew")
        heading = tk.Frame(history_card, bg=SURFACE)
        heading.pack(fill="x", padx=22, pady=(18, 11))
        self.label(heading, "SESSION HISTORY", 11, TEXT, "bold").pack(side="left")
        self.button(heading, "Export CSV", self.export_history,
                    SURFACE_ALT, TEXT).pack(side="right", padx=(8, 0))
        self.button(heading, "Clear", self.clear_history,
                    SURFACE_ALT, TEXT).pack(side="right")
        table_area = tk.Frame(history_card, bg=SURFACE)
        table_area.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        columns = ("time", "target", "formula", "result")
        self.history_tree = ttk.Treeview(table_area, columns=columns,
                                         show="headings", height=5,
                                         style="History.Treeview")
        widths = {"time": 80, "target": 100, "formula": 130, "result": 140}
        for column in columns:
            self.history_tree.heading(column, text=column.upper())
            self.history_tree.column(column, width=widths[column], minwidth=70,
                                     stretch=True, anchor="w")
        self.history_tree.pack(side="left", fill="both", expand=True)
        bar = ttk.Scrollbar(table_area, orient="vertical",
                            command=self.history_tree.yview)
        bar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=bar.set)

    def build_visual(self, parent):
        card = self.panel(parent)
        card.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        header = tk.Frame(card, bg=SURFACE)
        header.pack(fill="x", padx=17, pady=(12, 1))
        title = tk.Frame(header, bg=SURFACE)
        title.pack(side="left", fill="x", expand=True)
        self.label(title, "CIRCUIT • LIVE VALUES", 11, TEXT, "bold").pack(anchor="w")
        self.label(title, "Illustration • ideal one-resistor DC circuit", 9, MUTED).pack(anchor="w", pady=(3, 0))
        # A visible pause control makes the continuously repeating dots optional.
        self.flow_button = self.button(header, "Pause flow", self.toggle_flow,
                                       SURFACE_ALT, TEXT)
        self.flow_button.configure(padx=12, pady=7, state="disabled")
        self.flow_button.pack(side="right")
        self.circuit_canvas = tk.Canvas(card, bg=SURFACE,
                                        highlightthickness=0, height=186)
        self.circuit_canvas.pack(fill="both", expand=True, padx=13, pady=(0, 0))
        self.circuit_canvas.bind("<Configure>", self.draw_circuit)
        footer = tk.Frame(card, bg=SURFACE)
        footer.pack(fill="x", padx=18, pady=(0, 9))
        self.label(footer, "FORMULA", 9, MUTED, "bold").pack(side="left")
        self.formula_display = self.label(footer, "V = I × R", 14, ACCENT, "bold")
        self.formula_display.pack(side="left", padx=(12, 0))
        # This concise caption explains that dot movement is not a measurement.
        self.explanation = self.label(card, "Enter two values to populate the circuit.",
                                      9, MUTED, wraplength=430, justify="left")
        self.explanation.pack(fill="x", anchor="w", padx=18, pady=(0, 12))

    def build_metrics(self, parent):
        card = self.panel(parent)
        card.grid(row=1, column=0, sticky="nsew")
        upper = tk.Frame(card, bg=SURFACE)
        upper.pack(fill="x", padx=20, pady=(13, 7))
        heading = tk.Frame(upper, bg=SURFACE)
        heading.pack(fill="x")
        self.label(heading, "CALCULATION OUTPUT", 10, TEXT,
                   "bold").pack(side="left")
        self.button(heading, "Copy result", self.copy_result, SURFACE_ALT,
                    TEXT).pack(side="right")
        self.result_label = self.label(upper, "Awaiting inputs", 22, ACCENT, "bold")
        self.result_label.pack(anchor="w", pady=(4, 0))
        self.steps_label = self.label(upper, "Enter both known values to calculate.",
                                      9, MUTED, wraplength=400, justify="left")
        self.steps_label.pack(anchor="w", pady=(2, 0))
        grid = tk.Frame(card, bg=SURFACE)
        grid.pack(fill="both", expand=True, padx=20, pady=(0, 13))
        for index, metric in enumerate(UNITS):
            grid.columnconfigure(index % 2, weight=1)
            block = tk.Frame(grid, bg=SURFACE_ALT)
            block.grid(row=index // 2, column=index % 2,
                       sticky="nsew", padx=(0, 6) if index % 2 == 0 else (6, 0),
                       pady=(0, 8) if index < 2 else (2, 0))
            self.label(block, metric.upper(), 9, MUTED, "bold").pack(
                anchor="w", padx=13, pady=(7, 2))
            metric_label = self.label(block, "—", 13,
                                      AMBER if metric == "Power" else TEXT, "bold")
            metric_label.pack(anchor="w", padx=13, pady=(0, 7))
            self.metric_labels[metric] = metric_label

    def choose_target(self, name):
        self.target = name
        self.mode_index = 0
        for target, button in self.target_buttons.items():
            selected = name == target
            button.configure(bg=ACCENT if selected else SURFACE_ALT,
                             fg=BG if selected else TEXT,
                             activebackground=ACCENT if selected else SURFACE_ALT)
        self.method_box["values"] = [spec[0] for spec in METHODS[name]]
        self.method_box.current(0)
        self.refresh_fields()

    def method_changed(self, event=None):
        self.mode_index = self.method_box.current()
        self.refresh_fields()

    def refresh_fields(self):
        method = METHODS[self.target][self.mode_index]
        for index, name in enumerate(method[1:3]):
            self.field_titles[index].configure(text=f"{name}  ({UNITS[name]})")
            self.entries[index].delete(0, "end")
        self.formula_display.configure(text=method[3])
        self.explanation.configure(text="Enter two values to populate the circuit. Dots only move after a valid nonzero-current calculation.")
        self.status.configure(text="Ready. Enter both known values.", fg=MUTED)
        self.result_label.configure(text="Awaiting inputs", fg=ACCENT)
        self.steps_label.configure(text="The substituted equation will appear here.")
        self.result_value = None
        self.live_metrics = {name: None for name in UNITS}
        self.flow_paused = False
        self.flow_button.configure(text="Pause flow", state="disabled")
        for label in self.metric_labels.values():
            label.configure(text="—")
        self.entries[0].focus_set()
        self.draw_circuit()

    def calculate(self):
        method = METHODS[self.target][self.mode_index]
        try:
            a = parse_number(self.entries[0].get(), method[1])
            b = parse_number(self.entries[1].get(), method[2])
            result = calculate_electrical(self.target, self.mode_index, a, b)
        except ValueError as error:
            self.status.configure(text=str(error), fg=ERROR)
            self.result_label.configure(text="Check your inputs", fg=ERROR)
            # Never leave a previous successful calculation looking current.
            self.live_metrics = {name: None for name in UNITS}
            self.result_value = None
            self.flow_button.configure(state="disabled", text="Pause flow")
            self.flow_paused = False
            for label in self.metric_labels.values():
                label.configure(text="—")
            self.draw_circuit()
            return
        self.result_value = (result, UNITS[self.target])
        formatted = display_quantity(result, UNITS[self.target])
        self.result_label.configure(text=formatted, fg=ACCENT)
        self.steps_label.configure(
            text=f"{substituted_formula(self.target, self.mode_index, a, b)}  =  {formatted}")
        self.status.configure(text="Calculation successful. Values use ideal DC equations.",
                              fg=GREEN)
        metrics = derive_metrics(self.target, self.mode_index, a, b, result)
        self.live_metrics = metrics
        self.flow_paused = False
        current = metrics.get("Current")
        self.flow_button.configure(text="Pause flow", state="normal" if current is not None and current > 0 else "disabled")
        for name, label in self.metric_labels.items():
            label.configure(text=display_quantity(metrics[name], UNITS[name]))
        now = datetime.now().strftime("%H:%M:%S")
        record = (now, self.target, method[3], formatted, a, b)
        self.history.append(record)
        self.history_tree.insert("", 0, values=record[:4])
        self.explanation.configure(text=self.build_explanation(metrics))
        self.draw_circuit()

    def reset_inputs(self):
        self.refresh_fields()

    def copy_result(self):
        if self.result_value is None:
            self.status.configure(text="Calculate a result before copying.", fg=ERROR)
            return
        value, unit = self.result_value
        self.clipboard_clear()
        self.clipboard_append(f"{value:.12g} {unit}")
        self.status.configure(text="Result copied to clipboard.", fg=GREEN)

    def clear_history(self):
        if not self.history:
            return
        self.history.clear()
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self.status.configure(text="Session history cleared.", fg=MUTED)

    def build_explanation(self, metrics):
        """Briefly explain the indicator without confusing it for real sensors."""
        current = metrics.get("Current")
        if current is not None and current > 0:
            return ("Dots show simulated conventional current (+ to −). "
                    "Speed is illustrative, not a physical measurement. Pause anytime.")
        return "No current animation: the calculated current is zero or unavailable."

    def toggle_flow(self):
        """Pause or resume the dots without changing calculated measurements."""
        if self.live_metrics.get("Current") is None or self.live_metrics["Current"] <= 0:
            return
        self.flow_paused = not self.flow_paused
        self.flow_button.configure(text="Resume flow" if self.flow_paused else "Pause flow")
        self.draw_circuit()

    def flow_step(self):
        """Map current to readable animation speed, not physical drift velocity."""
        current = self.live_metrics.get("Current")
        if current is None or current <= 0:
            return 0.0
        # Logarithmic scaling keeps large currents from racing off-screen.
        return min(0.02, 0.002 + 0.004 * math.log10(1 + current * 10))

    def animate_current_flow(self):
        """Tkinter's event loop refreshes moving markers until the window closes."""
        if not self.flow_paused and self.flow_step() > 0:
            self.animation_phase = (self.animation_phase + self.flow_step()) % 1.0
            self.draw_circuit()
        self.after(50, self.animate_current_flow)

    def draw_value_chip(self, canvas, x, y, title, value, color, active=False):
        width, height = 132, 36
        fill = "#1E344A" if not active else "#214F60"
        outline = color if active else BORDER
        canvas.create_rectangle(x, y, x + width, y + height,
                                outline=outline, width=2 if active else 1,
                                fill=fill)
        canvas.create_text(x + 9, y + 10, text=title, anchor="w",
                           fill=MUTED, font=(FONT, 8, "bold"))
        canvas.create_text(x + 9, y + 26, text=value, anchor="w",
                           fill=color, font=(FONT, 10, "bold"))

    def export_history(self):
        if not self.history:
            messagebox.showinfo("No history", "Run at least one calculation to export a CSV.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            initialfile="voltlab_history.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Time", "Target", "Formula", "Result",
                                 "First input (SI)", "Second input (SI)"])
                for record in self.history:
                    writer.writerow(record)
            self.status.configure(text="History exported successfully.", fg=GREEN)
        except OSError as error:
            messagebox.showerror("Export failed", f"Could not save your CSV: {error}")

    def draw_circuit(self, event=None):
        """Draw a DC circuit and its values; animate positive-to-negative flow."""
        c = self.circuit_canvas
        c.delete("all")
        w, h = max(c.winfo_width(), 375), max(c.winfo_height(), 185)
        left, right = 74, w - 37
        top, bottom = 83, max(126, h - 65)
        battery_top, battery_bottom = top + 16, bottom - 14
        midpoint = (top + bottom) / 2
        r_start, r_end = w * 0.45, w * 0.66
        current = self.live_metrics.get("Current")
        values = {key: display_quantity(self.live_metrics.get(key), unit)
                  for key, unit in UNITS.items()}
        wire = "#7993A7"

        # The longer battery line is positive; conventional current leaves +,
        # goes right through the resistor, down, then left back to negative.
        c.create_line(left, top, r_start, top, fill=wire, width=3)
        c.create_line(r_end, top, right, top, right, bottom,
                      left, bottom, left, battery_bottom, fill=wire, width=3)
        c.create_line(left, top, left, battery_top, fill=wire, width=3)
        zigzag = [(r_start, top)]
        for index in range(1, 9):
            x = r_start + (r_end - r_start) * index / 9
            zigzag.append((x, top + (-10 if index % 2 else 10)))
        zigzag.append((r_end, top))
        c.create_line(*[v for pair in zigzag for v in pair],
                      fill=AMBER, width=3)
        c.create_line(left - 15, battery_top, left + 15, battery_top,
                      fill=ACCENT, width=4)
        c.create_line(left - 8, battery_bottom, left + 8, battery_bottom,
                      fill=ACCENT, width=4)
        c.create_text(left - 24, battery_top, text="+", fill=ACCENT,
                      font=(FONT, 10, "bold"))
        c.create_text(left - 22, battery_bottom, text="−", fill=ACCENT,
                      font=(FONT, 10, "bold"))
        c.create_text(right + 12, midpoint, text="↓", fill=MUTED,
                      font=(FONT, 17, "bold"))

        # Markers move along the conventional clockwise current direction.
        # Small gaps are intentional: the dots should not cross the battery.
        segments = [(left, top, right, top),
                    (right, top, right, bottom),
                    (right, bottom, left, bottom),
                    (left, bottom, left, battery_bottom)]
        lengths = [math.hypot(x2-x1, y2-y1) for x1, y1, x2, y2 in segments]
        total_length = sum(lengths)
        if current is not None and current > 0 and total_length > 0:
            for index in range(5):
                distance = ((self.animation_phase + index / 5) % 1) * total_length
                for (x1, y1, x2, y2), length in zip(segments, lengths):
                    if distance <= length:
                        t = distance / length if length else 0
                        px, py = x1 + (x2-x1)*t, y1 + (y2-y1)*t
                        c.create_oval(px-3, py-3, px+3, py+3, fill=ACCENT,
                                      outline="")
                        break
                    distance -= length

        # Position two measurement chips above and two below the circuit.
        # A colored border identifies the quantity the user selected.
        self.draw_value_chip(c, 4, 5, "VOLTAGE · V", values["Voltage"],
                             ACCENT, self.target == "Voltage")
        self.draw_value_chip(c, w-136, 5, "RESISTANCE · R", values["Resistance"],
                             AMBER, self.target == "Resistance")
        self.draw_value_chip(c, 4, h-43, "CURRENT · I", values["Current"],
                             ACCENT, self.target == "Current")
        self.draw_value_chip(c, w-136, h-43, "POWER · P", values["Power"],
                             AMBER, self.target == "Power")



if __name__ == "__main__":
    app = OhmsApp()
    app.mainloop()  # Tkinter's event loop keeps the window interactive until closed.
