import math
import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import numpy as np

# ==========================================================
# MATRIX LAB | NUMPY EDITION (AURORA DESIGN)
# 3x3 matrix calculator powered by NumPy
# ==========================================================

BG, SIDE, BG2 = "#070B17", "#0A1020", "#0C1326"
GLASS, GLASS2, GLASS3, BORDER = "#101A30", "#16233D", "#1D2C4A", "#2A3C60"
PURPLE, CYAN, MINT, PINK, GOLD = "#7C5CFC", "#36C6F0", "#35D49A", "#FF6B81", "#FFD479"
WHITE, MUTED = "#F4F7FF", "#8FA0C2"
ACC = {"A": PURPLE, "B": CYAN}
FONT = "Segoe UI"
R3 = range(3)

PRESETS = {
    "Sample 1": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    "Sample 2": [[9, 8, 7], [6, 5, 4], [3, 2, 1]],
    "Sample 3": [[2, 0, 1], [3, 4, 5], [1, 2, 3]],
    "Invertible": [[2, 1, 1], [1, 3, 2], [1, 0, 0]],
    "Identity": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    "Diagonal": [[2, 0, 0], [0, 5, 0], [0, 0, 8]],
    "Zero Matrix": [[0] * 3 for _ in range(3)],
}


# ==========================================================
# NUMPY ENGINE
# ==========================================================
def inv(a):
    if abs(np.linalg.det(a)) < 1e-10:
        raise ValueError("Matrix is singular; the inverse does not exist.")
    return np.linalg.inv(a)


def same(a, b):
    return "Matrices are equal  ✓" if np.allclose(a, b) else "Matrices are not equal  ✗"


# name: (function(A, B, s), explanation)
OPS = {
    "Addition (A + B)": (lambda A, B, s: A + B, "np.add: matching elements are added."),
    "Subtraction (A - B)": (lambda A, B, s: A - B, "np.subtract: matching elements are subtracted."),
    "Matrix Multiplication (A × B)": (lambda A, B, s: A @ B, "A @ B: rows of A times columns of B."),
    "Element-wise Multiplication": (lambda A, B, s: A * B, "A * B: matching elements are multiplied."),
    "Transpose of A": (lambda A, B, s: A.T, "A.T: rows and columns of A are exchanged."),
    "Transpose of B": (lambda A, B, s: B.T, "B.T: rows and columns of B are exchanged."),
    "Determinant of A": (lambda A, B, s: float(np.linalg.det(A)), "np.linalg.det(A)"),
    "Determinant of B": (lambda A, B, s: float(np.linalg.det(B)), "np.linalg.det(B)"),
    "Inverse of A": (lambda A, B, s: inv(A), "np.linalg.inv(A): the inverse of Matrix A."),
    "Inverse of B": (lambda A, B, s: inv(B), "np.linalg.inv(B): the inverse of Matrix B."),
    "Trace of A": (lambda A, B, s: float(np.trace(A)), "np.trace(A): sum of the main diagonal."),
    "Trace of B": (lambda A, B, s: float(np.trace(B)), "np.trace(B): sum of the main diagonal."),
    "Scalar Multiplication of A": (lambda A, B, s: A * s, "Every element of A is multiplied by the scalar."),
    "Scalar Multiplication of B": (lambda A, B, s: B * s, "Every element of B is multiplied by the scalar."),
    "Equality Check": (lambda A, B, s: same(A, B), "np.allclose(A, B): all values are compared."),
}


def fmt(v):
    if isinstance(v, (float, np.floating)):
        v = float(v)
        if abs(v) < 1e-9:
            v = 0.0
        return f"{v:.4f}".rstrip("0").rstrip(".") or "0"
    return str(v)


def matrix_text(m):
    return "\n".join("    ".join(fmt(x) for x in row) for row in m)


def result_text(r):
    return matrix_text(r) if isinstance(r, np.ndarray) else (r if isinstance(r, str) else fmt(r))


# ==========================================================
# ANIMATION / WIDGET HELPERS
# ==========================================================
def ease(t):
    return 1 - (1 - min(1, max(0, t))) ** 3


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Btn(tk.Label):
    """Flat button with a smooth colour fade on hover."""

    def __init__(self, parent, text, command, bg=GLASS3, hover=PURPLE, fg=WHITE,
                 size=9, anchor="center", padx=14, pady=9):
        super().__init__(parent, text=text, bg=bg, fg=fg, cursor="hand2", anchor=anchor,
                         font=(FONT, size, "bold"), padx=padx, pady=pady)
        self.base, self.hov, self.cmd, self.t, self.dir, self.job = bg, hover, command, 0.0, 0, None
        self.bind("<Enter>", lambda e: self._go(1))
        self.bind("<Leave>", lambda e: self._go(-1))
        self.bind("<Button-1>", lambda e: self.cmd())

    def _go(self, d):
        self.dir = d
        if not self.job:
            self._step()

    def _step(self):
        self.t = min(1, max(0, self.t + self.dir * 0.2))
        self.config(bg=mix(self.base, self.hov, self.t))
        self.job = self.after(16, self._step) if 0 < self.t < 1 else None

    def set_base(self, color):
        self.base = color
        self.config(bg=mix(self.base, self.hov, self.t))


class Scroll(tk.Frame):
    """Scrollable page so nothing is ever cut off at the bottom."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.cv = tk.Canvas(self, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=self.cv.yview, style="Dark.Vertical.TScrollbar")
        self.cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.cv.pack(side="left", fill="both", expand=True)
        self.body = tk.Frame(self.cv, bg=BG)
        self.win = self.cv.create_window((0, 0), window=self.body, anchor="nw")
        self.body.bind("<Configure>", lambda e: self.cv.configure(scrollregion=self.cv.bbox("all")))
        self.cv.bind("<Configure>", lambda e: self.cv.itemconfigure(self.win, width=e.width))


# ==========================================================
# WINDOW + STYLE
# ==========================================================
root = tk.Tk()
root.title("Matrix Lab | NumPy Edition")
root.geometry("1280x800")
root.minsize(1000, 640)
root.configure(bg=BG)
try:
    root.state("zoomed")
except tk.TclError:
    pass

style = ttk.Style()
style.theme_use("clam")
style.configure("Glass.TCombobox", fieldbackground=GLASS3, background=GLASS3, foreground=WHITE,
                arrowcolor=CYAN, bordercolor=BORDER, lightcolor=GLASS3, darkcolor=GLASS3, padding=7)
style.map("Glass.TCombobox", fieldbackground=[("readonly", GLASS3)], foreground=[("readonly", WHITE)],
          selectbackground=[("readonly", GLASS3)], selectforeground=[("readonly", WHITE)])
style.configure("Dark.Vertical.TScrollbar", background=GLASS3, troughcolor=BG, bordercolor=BG,
                arrowcolor=BG, lightcolor=GLASS3, darkcolor=GLASS3)
root.option_add("*TCombobox*Listbox.background", GLASS2)
root.option_add("*TCombobox*Listbox.foreground", WHITE)
root.option_add("*TCombobox*Listbox.selectBackground", PURPLE)
root.option_add("*TCombobox*Listbox.font", (FONT, 10))

entries, history, state = {}, [], {"result": None}
status_var = tk.StringVar(value="Ready  •  Enter values or choose a preset")
count_var = tk.StringVar(value="0")


def label(parent, text, color=WHITE, size=10, bold=False, **kw):
    return tk.Label(parent, text=text, fg=color, bg=kw.pop("bg", parent.cget("bg")),
                    font=(FONT, size, "bold" if bold else "normal"), **kw)


def panel(parent, accent=BORDER):
    return tk.Frame(parent, bg=GLASS, highlightbackground=accent, highlightthickness=1)


# ==========================================================
# LAYOUT: sidebar | (stage + status bar)
# ==========================================================
SIDE_W = 244
sidebar = tk.Frame(root, bg=SIDE, width=SIDE_W)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)
tk.Frame(root, bg=BORDER, width=1).pack(side="left", fill="y")

main = tk.Frame(root, bg=BG)
main.pack(side="left", fill="both", expand=True)
statusbar = tk.Frame(main, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
statusbar.pack(side="bottom", fill="x")
stage = tk.Frame(main, bg=BG)
stage.pack(side="top", fill="both", expand=True)

dot = label(statusbar, "●", MINT, 10, True)
dot.pack(side="left", padx=(14, 6), pady=8)
label(statusbar, "", MUTED, 9, textvariable=status_var, anchor="w").pack(side="left", fill="x", expand=True)
clock = label(statusbar, "", CYAN, 9, True)
clock.pack(side="right", padx=14)

label(sidebar, "∑", CYAN, 28, True).place(x=22, y=14)
label(sidebar, "MATRIX LAB", WHITE, 14, True).place(x=64, y=22)
label(sidebar, "NUMPY EDITION", MUTED, 7, True).place(x=65, y=46)
tk.Frame(sidebar, bg=BORDER, height=1).place(x=20, y=84, width=SIDE_W - 40)
label(sidebar, "NAVIGATION", MUTED, 8, True).place(x=22, y=102)

NAV = [("Workspace", "▦   Workspace"), ("History", "◷   History"), ("About", "ⓘ   About")]
NAV_Y0, NAV_STEP = 132, 52
indicator = tk.Frame(sidebar, bg=PURPLE, width=4)
indicator.place(x=0, y=NAV_Y0 + 4, height=36)
nav_btns, pages = {}, {}
current = {"name": None, "ind_y": NAV_Y0 + 4}


def move_indicator(target, i=0, start=None):
    start = current["ind_y"] if start is None else start
    indicator.place_configure(y=int(start + (target - start) * ease(i / 14)))
    if i < 14:
        root.after(16, move_indicator, target, i + 1, start)
    else:
        current["ind_y"] = target


def show_page(name):
    if name == current["name"]:
        return
    if current["name"]:
        pages[current["name"]].place_forget()
    current["name"] = name
    new = pages[name]
    for n, b in nav_btns.items():
        b.set_base(GLASS2 if n == name else SIDE)
        b.config(fg=WHITE if n == name else MUTED)
    move_indicator(NAV_Y0 + 4 + [n for n, _ in NAV].index(name) * NAV_STEP)

    def slide(i=0):
        new.place(x=int(60 * (1 - ease(i / 14))), y=0, relwidth=1, relheight=1)
        if i < 14:
            root.after(16, slide, i + 1)
    slide()


for i, (key, text) in enumerate(NAV):
    b = Btn(sidebar, text, lambda k=key: show_page(k), bg=SIDE, hover=GLASS3, fg=MUTED,
            size=10, anchor="w", padx=18, pady=0)
    b.place(x=14, y=NAV_Y0 + i * NAV_STEP, width=SIDE_W - 28, height=44)
    nav_btns[key] = b

footer = tk.Frame(sidebar, bg=GLASS, highlightbackground=BORDER, highlightthickness=1)
footer.place(x=14, rely=1.0, y=-18, anchor="sw", width=SIDE_W - 28)
label(footer, "CALCULATIONS", MUTED, 8, True).pack(anchor="w", padx=14, pady=(12, 0))
label(footer, "", CYAN, 26, True, textvariable=count_var).pack(anchor="w", padx=14)
Btn(footer, "▶  Quick Calculate", lambda: calculate(True), bg=PURPLE, hover="#6040E0",
    pady=10).pack(fill="x", padx=12, pady=(6, 12))


# ==========================================================
# MATRIX HELPERS
# ==========================================================
def read_matrix(name):
    out = []
    for r, row in enumerate(entries[name]):
        vals = []
        for c, e in enumerate(row):
            t = e.get().strip()
            if not t:
                raise ValueError(f"Matrix {name}: cell [{r + 1},{c + 1}] is empty.")
            try:
                vals.append(float(t))
            except ValueError:
                raise ValueError(f"Matrix {name}: '{t}' is not a valid number.")
        out.append(vals)
    return np.array(out)


def set_matrix(name, m):
    for r in R3:
        for c in R3:
            e = entries[name][r][c]
            e.delete(0, tk.END)
            e.insert(0, str(m[r][c]))
    refresh_insights()


# ==========================================================
# PAGE 1: WORKSPACE
# ==========================================================
ws = Scroll(stage)
pages["Workspace"] = ws
W = ws.body
PAD = 32

head = tk.Frame(W, bg=BG)
head.pack(fill="x", padx=PAD, pady=(26, 14))
label(head, "Matrix Operations", WHITE, 26, True).pack(anchor="w")
label(head, "Explore and calculate 3 × 3 matrices with the NumPy engine.", MUTED, 10).pack(anchor="w", pady=(2, 0))

row = tk.Frame(W, bg=BG)
row.pack(fill="x", padx=PAD - 7, pady=(0, 16))
for c in range(2):
    row.grid_columnconfigure(c, weight=1, uniform="m")
insight_vars = {}


def matrix_card(name, preset, col):
    accent = ACC[name]
    box = panel(row, accent)
    box.grid(row=0, column=col, sticky="nsew", padx=7)
    top = tk.Frame(box, bg=GLASS)
    top.pack(fill="x", padx=14, pady=(14, 8))
    label(top, f"MATRIX {name}", accent, 12, True).pack(side="left")
    label(top, "3 × 3", MUTED, 8, True).pack(side="right")

    var = tk.StringVar(value=preset)
    ttk.Combobox(box, textvariable=var, values=list(PRESETS), state="readonly",
                 style="Glass.TCombobox").pack(fill="x", padx=14, pady=(0, 10))

    grid = tk.Frame(box, bg=GLASS)
    grid.pack(padx=10, pady=2)
    cells_ = []
    for r in R3:
        line = []
        for c in R3:
            e = tk.Entry(grid, width=7, justify="center", bg=GLASS3, fg=WHITE, insertbackground=CYAN,
                         relief="flat", bd=0, font=(FONT, 13, "bold"), highlightthickness=1,
                         highlightbackground=BORDER, highlightcolor=accent)
            e.grid(row=r, column=c, padx=4, pady=4, ipady=9)
            e.insert(0, str(PRESETS[preset][r][c]))
            e.bind("<KeyRelease>", lambda ev: refresh_insights())
            line.append(e)
        cells_.append(line)
    entries[name] = cells_

    def apply():
        set_matrix(name, PRESETS[var.get()])
        status_var.set(f"Preset '{var.get()}' applied to Matrix {name}")

    def clear():
        set_matrix(name, PRESETS["Zero Matrix"])
        status_var.set(f"Matrix {name} cleared.")

    acts = tk.Frame(box, bg=GLASS)
    acts.pack(fill="x", padx=12, pady=(10, 8))
    Btn(acts, "↧ Apply Preset", apply, hover=accent).pack(side="left", fill="x", expand=True, padx=(0, 4))
    Btn(acts, "⌫ Clear", clear, hover=PINK).pack(side="left", fill="x", expand=True, padx=(4, 0))

    # live NumPy insights
    ins = tk.Frame(box, bg=BG2)
    ins.pack(fill="x", padx=14, pady=(4, 14))
    for k, key in enumerate(("DET", "RANK", "TRACE", "NORM")):
        v = tk.StringVar(value="—")
        insight_vars[(name, key)] = v
        cell = tk.Frame(ins, bg=BG2)
        cell.grid(row=0, column=k, sticky="ew", padx=6, pady=8)
        ins.grid_columnconfigure(k, weight=1, uniform="i")
        label(cell, key, MUTED, 7, True).pack(anchor="w")
        label(cell, "", accent, 12, True, textvariable=v).pack(anchor="w")


def refresh_insights():
    for n in ACC:
        try:
            m = read_matrix(n)
            vals = (fmt(np.linalg.det(m)), str(np.linalg.matrix_rank(m)), fmt(np.trace(m)), fmt(np.linalg.norm(m)))
        except Exception:
            vals = ("—",) * 4
        for key, v in zip(("DET", "RANK", "TRACE", "NORM"), vals):
            insight_vars[(n, key)].set(v)


matrix_card("A", "Sample 1", 0)
matrix_card("B", "Sample 2", 1)

# ---- operation center ----
op_panel = panel(W, PURPLE)
op_panel.pack(fill="x", padx=PAD, pady=(0, 16))
oh = tk.Frame(op_panel, bg=GLASS)
oh.pack(fill="x", padx=18, pady=(16, 4))
label(oh, "⚙  OPERATION CENTER", WHITE, 11, True).pack(side="left")
label(oh, "CHOOSE AN OPERATION  •  ADD A SCALAR IF NEEDED", MUTED, 8, True).pack(side="right")

op_var, sc_var = tk.StringVar(value=list(OPS)[0]), tk.StringVar(value="2")
ctl = tk.Frame(op_panel, bg=GLASS)
ctl.pack(fill="x", padx=14, pady=(8, 6))
ctl.grid_columnconfigure(0, weight=4)
ctl.grid_columnconfigure(1, weight=1)
label(ctl, "OPERATION", MUTED, 8, True).grid(row=0, column=0, sticky="w", padx=5)
ttk.Combobox(ctl, textvariable=op_var, values=list(OPS), state="readonly",
             style="Glass.TCombobox").grid(row=1, column=0, sticky="ew", padx=5, pady=(5, 0))
label(ctl, "SCALAR", MUTED, 8, True).grid(row=0, column=1, sticky="w", padx=5)
sc_entry = tk.Entry(ctl, textvariable=sc_var, bg=GLASS3, fg=WHITE, insertbackground=CYAN, relief="flat",
                    font=(FONT, 11), highlightthickness=1, highlightbackground=BORDER, highlightcolor=CYAN,
                    disabledbackground=GLASS, disabledforeground=BORDER)
sc_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=(5, 0), ipady=7)


def update_controls(*_):
    sc_entry.config(state="normal" if "Scalar" in op_var.get() else "disabled")


op_var.trace_add("write", update_controls)
update_controls()


def swap():
    a, b = read_matrix("A"), read_matrix("B")
    set_matrix("A", b.tolist())
    set_matrix("B", a.tolist())
    status_var.set("Matrices A and B swapped.")


def reset_all():
    for n in ACC:
        set_matrix(n, PRESETS["Zero Matrix"])
    sc_var.set("2")
    op_var.set(list(OPS)[0])
    status_var.set("All matrices cleared and controls reset.")


btns = tk.Frame(op_panel, bg=GLASS)
btns.pack(fill="x", padx=14, pady=(10, 16))
Btn(btns, "⇄ Swap", swap).pack(side="left", padx=5)
Btn(btns, "↺ Reset", reset_all, hover=PINK).pack(side="left", padx=5)
Btn(btns, "▶  CALCULATE", lambda: calculate(), bg=PURPLE, hover="#6040E0", padx=22).pack(side="left", padx=5)
Btn(btns, "▣ Copy Result", lambda: copy_result()).pack(side="right", padx=5)

# ---- result ----
res_panel = panel(W, CYAN)
res_panel.pack(fill="x", padx=PAD, pady=(0, 36))
rh = tk.Frame(res_panel, bg=GLASS)
rh.pack(fill="x", padx=18, pady=(16, 4))
label(rh, "✦  RESULT CONSOLE", CYAN, 11, True).pack(side="left")
res_state = label(rh, "WAITING", MUTED, 8, True)
res_state.pack(side="right")
res_title = label(res_panel, "Your result will appear here", WHITE, 17, True)
res_title.pack(anchor="w", padx=18, pady=(4, 0))
res_sub = label(res_panel, "Choose an operation above and press Calculate.", MUTED, 9)
res_sub.pack(anchor="w", padx=18, pady=(0, 12))

res_area = tk.Frame(res_panel, bg=GLASS)
res_area.pack(fill="x", padx=18, pady=(0, 10))
res_grid = tk.Frame(res_area, bg=GLASS)
for c in R3:
    res_grid.grid_columnconfigure(c, weight=1, uniform="r")
cells = []
for r in R3:
    line = []
    for c in R3:
        l = tk.Label(res_grid, text="—", height=2, bg=BG2, fg=WHITE, font=(FONT, 15, "bold"),
                     highlightthickness=1, highlightbackground=BORDER)
        l.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        line.append(l)
    cells.append(line)
res_scalar = tk.Label(res_area, text="", bg=BG2, fg=MINT, font=(FONT, 24, "bold"), padx=26, pady=18,
                      highlightthickness=1, highlightbackground=BORDER)
res_detail = tk.Label(res_panel, text="", bg=GLASS, fg=MUTED, font=(FONT, 9), justify="left", anchor="w")
res_detail.pack(fill="x", padx=18, pady=(0, 18))
res_panel.bind("<Configure>", lambda e: res_detail.config(wraplength=max(200, e.width - 40)))

anim = {"job": None}


def animate_result(res):
    if anim["job"]:
        root.after_cancel(anim["job"])
    res_grid.pack_forget()
    res_scalar.pack_forget()
    frames = 30
    is_mat = isinstance(res, np.ndarray)
    (res_grid if is_mat else res_scalar).pack(fill="x" if is_mat else None, anchor="w")

    def step(i):
        t = i / frames
        if is_mat:
            for r in R3:
                for c in R3:
                    ti = ease(t * 1.7 - (r * 3 + c) * 0.07)
                    cells[r][c].config(text=fmt(float(res[r][c]) * ti), bg=mix(PURPLE, BG2, ti))
        elif isinstance(res, str):
            res_scalar.config(text=res, fg=mix(BG2, MINT, ease(t)))
        else:
            res_scalar.config(text=fmt(res * ease(t)), fg=mix(BG2, MINT, ease(t * 2)))
        anim["job"] = root.after(18, step, i + 1) if i < frames else None
    step(0)


def show_result(res, title, details):
    state["result"] = res
    res_title.config(text=title)
    res_sub.config(text="Calculation completed successfully.")
    res_detail.config(text=details)
    res_state.config(text="✓ COMPLETE", fg=MINT)
    animate_result(res)


def calculate(go_home=False):
    try:
        if go_home:
            show_page("Workspace")
        A, B, op = read_matrix("A"), read_matrix("B"), op_var.get()
        s = float(sc_var.get()) if "Scalar" in op else 0.0
        fn, expl = OPS[op]
        res = fn(A, B, s)
        show_result(res, op, expl)
        history.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "op": op, "details": expl, "result": res})
        count_var.set(str(len(history)))
        refresh_history()
        refresh_insights()
        status_var.set(f"✓ Calculation completed  •  {op}")
        root.update_idletasks()
        total = W.winfo_height()
        if total > 0:
            ws.cv.yview_moveto(max(0, (res_panel.winfo_y() - 10) / total))
    except np.linalg.LinAlgError:
        res_state.config(text="⚠ ERROR", fg=PINK)
        status_var.set("Calculation failed  •  singular matrix")
        messagebox.showerror("Calculation Error", "Matrix is singular; inverse does not exist.")
    except Exception as err:
        res_state.config(text="⚠ ERROR", fg=PINK)
        status_var.set("Calculation failed  •  check your inputs.")
        messagebox.showerror("Calculation Error", str(err))


def copy_result():
    if state["result"] is None:
        messagebox.showinfo("Copy Result", "Please calculate a result first.")
        return
    root.clipboard_clear()
    root.clipboard_append(result_text(state["result"]))
    res_state.config(text="✓ COPIED", fg=MINT)
    status_var.set("Result copied to clipboard.")


# ==========================================================
# PAGE 2: HISTORY
# ==========================================================
hp = Scroll(stage)
pages["History"] = hp
HB = hp.body
hh = tk.Frame(HB, bg=BG)
hh.pack(fill="x", padx=PAD, pady=(26, 14))
label(hh, "Calculation History", WHITE, 26, True).pack(side="left")
Btn(hh, "Clear History", lambda: clear_history(), hover=PINK).pack(side="right")
hist_box = panel(HB, PURPLE)
hist_box.pack(fill="x", padx=PAD, pady=(0, 36))
hist_text = tk.Text(hist_box, height=24, bg=BG2, fg=WHITE, font=("Consolas", 10), relief="flat", bd=0,
                    padx=16, pady=14, wrap="word", highlightthickness=0, state="disabled")
hist_text.pack(fill="x", padx=2, pady=2)
hist_text.tag_config("head", foreground=CYAN, font=("Consolas", 10, "bold"))
hist_text.tag_config("body", foreground=MUTED)
hist_text.tag_config("res", foreground=MINT, font=("Consolas", 11, "bold"))
hist_text.tag_config("sep", foreground=BORDER)


def refresh_history():
    hist_text.config(state="normal")
    hist_text.delete("1.0", tk.END)
    if not history:
        hist_text.insert(tk.END, "No calculations yet.\n\nRun a calculation and it will be saved here.", "body")
    for i, item in enumerate(history, 1):
        hist_text.insert(tk.END, f"#{i}  {item['time']}  |  {item['op']}\n", "head")
        hist_text.insert(tk.END, item["details"] + "\n", "body")
        hist_text.insert(tk.END, result_text(item["result"]) + "\n", "res")
        hist_text.insert(tk.END, "─" * 60 + "\n\n", "sep")
    hist_text.config(state="disabled")


def clear_history():
    history.clear()
    count_var.set("0")
    refresh_history()
    status_var.set("Calculation history cleared.")


# ==========================================================
# PAGE 3: ABOUT
# ==========================================================
ap = Scroll(stage)
pages["About"] = ap
label(ap.body, "About Matrix Lab", WHITE, 26, True).pack(anchor="w", padx=PAD, pady=(26, 14))
ab = panel(ap.body, CYAN)
ab.pack(fill="x", padx=PAD, pady=(0, 36))
about = tk.Label(ab, justify="left", anchor="w", bg=GLASS, fg=MUTED, font=(FONT, 10), text=(
    "Matrix Lab NumPy Edition is a 3×3 matrix calculator built with Python, Tkinter and NumPy.\n\n"
    "FEATURES\n"
    "•  Two editable matrices (A and B) with presets\n"
    "•  Live NumPy insights: determinant, rank, trace and norm\n"
    "•  Addition, subtraction, matrix and element-wise multiplication\n"
    "•  Transpose, determinant, inverse, trace, scalar multiplication, equality check\n"
    "•  Animated results, calculation history and copy to clipboard\n\n"
    "TECHNOLOGY\n"
    "Python  •  Tkinter  •  NumPy (pip install numpy)"))
about.pack(fill="x", padx=20, pady=20)
ab.bind("<Configure>", lambda e: about.config(wraplength=max(200, e.width - 50)))


# ==========================================================
# GLOBAL ANIMATIONS + SCROLLING
# ==========================================================
def pulse():
    dot.config(fg=mix(BG2, MINT, 0.3 + 0.7 * (1 + math.sin(time.time() * 3)) / 2))
    root.after(50, pulse)


def tick():
    clock.config(text=datetime.now().strftime("%a %d %b   %H:%M:%S"))
    root.after(1000, tick)


def wheel(e):
    page = pages.get(current["name"])
    if page:
        d = -1 if (e.num == 4 or (e.num != 5 and e.delta > 0)) else 1
        page.cv.yview_scroll(d * 3, "units")


root.bind_all("<MouseWheel>", wheel)
root.bind_all("<Button-4>", wheel)
root.bind_all("<Button-5>", wheel)

# ==========================================================
# START
# ==========================================================
refresh_history()
refresh_insights()
show_result(np.zeros((3, 3)), "No calculation yet", "Choose an operation and click Calculate. Your answer will appear here.")
res_state.config(text="WAITING", fg=MUTED)
show_page("Workspace")
pulse()
tick()
root.mainloop()