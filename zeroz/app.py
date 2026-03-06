"""
ZEROZ Hotmail Checker -- Modern GUI built with customtkinter.
"""

import os
import time
import queue
import threading
import itertools

import customtkinter as ctk
from tkinter import filedialog, messagebox

from zeroz.theme import (
    COLORS, FONTS, CORNER_RADIUS, SIDEBAR_WIDTH, WINDOW_SIZE,
    apply_theme,
)
from zeroz.widgets import StatCard, SidebarSection, ResultTextbox
from zeroz.checker import check_account


class ZerozApp:
    """Main application window."""

    def __init__(self):
        apply_theme()

        self.root = ctk.CTk()
        self.root.title("ZEROZ Hotmail Checker")
        self.root.configure(fg_color=COLORS["bg"])

        w, h = WINDOW_SIZE
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        self.root.minsize(860, 560)

        self._combos = []
        self._proxies = []
        self._proxy_iter = None
        self._proxy_lock = threading.Lock()
        self._running = False
        self._stop_evt = threading.Event()
        self._result_q = queue.Queue()
        self._stats = {
            "total": 0, "good": 0,
            "bad": 0, "invalid": 0, "locked": 0, "error": 0,
        }
        self._t_start = 0.0

        self._all_results = []
        self._good_list = []

        self._build_ui()
        self._poll_results()

    # ── proxy helpers ─────────────────────────────────────────────────────────

    def _make_proxy_dict(self, p):
        if not p:
            return None
        return {"http": f"http://{p}", "https": f"http://{p}"}

    def _next_proxy(self):
        with self._proxy_lock:
            if not self._proxy_iter:
                return None
            return self._make_proxy_dict(next(self._proxy_iter))

    # ══════════════════════════════════════════════════════════════════════════
    #  UI
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self._build_title_bar()
        self._build_sidebar()
        self._build_main_area()
        self._build_status_bar()

    def _build_title_bar(self):
        bar = ctk.CTkFrame(
            self.root, fg_color=COLORS["bg_dark"],
            height=48, corner_radius=0,
        )
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)

        ctk.CTkLabel(
            bar, text="  ZEROZ HOTMAIL CHECKER",
            font=FONTS["title_bar"],
            text_color=COLORS["accent"],
        ).pack(side="left", padx=12, pady=8)

        ctk.CTkLabel(
            bar, text="FREE & OPEN SOURCE",
            font=(FONTS["label_small"][0], 12),
            text_color=COLORS["green"],
        ).pack(side="left", padx=(0, 8), pady=8)

        ctk.CTkButton(
            bar, text="Telegram", font=(FONTS["label_small"][0], 12),
            fg_color=COLORS["btn"], hover_color="#2CA5E0",
            text_color=COLORS["white"], corner_radius=6,
            height=30, width=100,
            command=lambda: __import__("webbrowser").open(
                "https://t.me/zerozpanel"),
        ).pack(side="right", padx=12, pady=8)

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self.root, fg_color=COLORS["surface"],
            width=SIDEBAR_WIDTH, corner_radius=0,
        )
        sidebar.grid(row=1, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        scroll = ctk.CTkScrollableFrame(
            sidebar, fg_color=COLORS["surface"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        scroll.pack(fill="both", expand=True)

        # brand
        brand = ctk.CTkFrame(scroll, fg_color="transparent")
        brand.pack(fill="x", pady=(16, 0))
        ctk.CTkLabel(brand, text="ZEROZ", font=FONTS["brand"],
                     text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(brand, text="Hotmail Checker", font=FONTS["brand_sub"],
                     text_color=COLORS["grey"]).pack()
        ctk.CTkLabel(brand, text="v1.0.0  --  Free Edition",
                     font=(FONTS["label_small"][0], 11),
                     text_color=COLORS["green"]).pack(pady=(2, 0))

        # premium / download CTA
        cta = ctk.CTkFrame(scroll, fg_color=COLORS["blue_dim"],
                           corner_radius=8)
        cta.pack(fill="x", padx=8, pady=(12, 0))
        ctk.CTkLabel(
            cta, text="EXE & Premium Available",
            font=(FONTS["section"][0], 13, "bold"),
            text_color=COLORS["accent"],
        ).pack(padx=8, pady=(8, 2))
        ctk.CTkLabel(
            cta, text="Latest builds, premium features\nand direct inbox access",
            font=(FONTS["label_small"][0], 11),
            text_color=COLORS["grey"], justify="center",
        ).pack(padx=8)
        ctk.CTkButton(
            cta, text="Join Telegram",
            font=FONTS["btn_small"],
            fg_color="#2CA5E0", hover_color="#1A8FC4",
            text_color="#ffffff", corner_radius=8, height=32,
            command=lambda: __import__("webbrowser").open(
                "https://t.me/zerozpanel"),
        ).pack(fill="x", padx=8, pady=(4, 8))

        # combo
        sec = SidebarSection(scroll, "Combo File")
        sec.pack(fill="x", padx=8)
        self._lbl_combo = ctk.CTkLabel(
            sec, text="No file loaded", font=FONTS["label_small"],
            text_color=COLORS["grey"], anchor="w")
        self._lbl_combo.pack(fill="x", padx=4, pady=(0, 4))
        ctk.CTkButton(
            sec, text="Load Combo (.txt)", font=FONTS["btn_small"],
            fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["white"], corner_radius=8, height=38,
            command=self._load_combos,
        ).pack(fill="x", padx=4, pady=(0, 4))

        # proxy
        sec = SidebarSection(scroll, "Proxy")
        sec.pack(fill="x", padx=8)
        ctk.CTkLabel(
            sec, text="host:port  or  user:pass@host:port",
            font=(FONTS["label_small"][0], 11),
            text_color=COLORS["grey"], anchor="w", wraplength=260,
        ).pack(fill="x", padx=4)
        self._ent_proxy = ctk.CTkEntry(
            sec, placeholder_text="e.g. 1.2.3.4:8080",
            font=FONTS["mono_small"], fg_color=COLORS["input_bg"],
            border_color=COLORS["border"], text_color=COLORS["white"],
            corner_radius=8, height=36,
        )
        self._ent_proxy.pack(fill="x", padx=4, pady=(4, 4))
        ctk.CTkLabel(sec, text="-- or load a list --",
                     font=(FONTS["label_small"][0], 11),
                     text_color=COLORS["border"]).pack(pady=2)
        self._lbl_pfile = ctk.CTkLabel(
            sec, text="No proxy list loaded", font=FONTS["label_small"],
            text_color=COLORS["grey"], anchor="w")
        self._lbl_pfile.pack(fill="x", padx=4, pady=(0, 4))
        ctk.CTkButton(
            sec, text="Load Proxy List (.txt)", font=FONTS["btn_small"],
            fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["white"], corner_radius=8, height=38,
            command=self._load_proxies,
        ).pack(fill="x", padx=4, pady=(0, 4))

        # settings
        sec = SidebarSection(scroll, "Settings")
        sec.pack(fill="x", padx=8)
        self._var_threads = ctk.IntVar(value=10)
        self._var_timeout = ctk.IntVar(value=20)
        self._var_retries = ctk.IntVar(value=2)
        for label, var, lo, hi in [
            ("Threads", self._var_threads, 1, 100),
            ("Timeout (s)", self._var_timeout, 5, 120),
            ("Retries", self._var_retries, 0, 5),
        ]:
            row = ctk.CTkFrame(sec, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=3)
            ctk.CTkLabel(row, text=label, font=FONTS["label_small"],
                         text_color=COLORS["white"], anchor="w",
                         width=90).pack(side="left")
            val_lbl = ctk.CTkLabel(row, text=str(var.get()),
                                   font=FONTS["mono_small"],
                                   text_color=COLORS["accent"], width=36)
            val_lbl.pack(side="right")
            ctk.CTkSlider(
                row, from_=lo, to=hi, variable=var,
                number_of_steps=hi - lo,
                fg_color=COLORS["input_bg"],
                progress_color=COLORS["accent"],
                button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
                height=16, width=100,
            ).pack(side="right", padx=(4, 4))
            var.trace_add(
                "write",
                lambda *_a, v=var, l=val_lbl: l.configure(text=str(v.get())),
            )

        # controls
        sec = SidebarSection(scroll, "Controls")
        sec.pack(fill="x", padx=8)
        self._btn_start = ctk.CTkButton(
            sec, text="START", font=FONTS["btn"],
            fg_color=COLORS["green_dim"], hover_color=COLORS["green"],
            text_color=COLORS["green"], corner_radius=8, height=44,
            command=self._start,
        )
        self._btn_start.pack(fill="x", padx=4, pady=(0, 6))
        self._btn_stop = ctk.CTkButton(
            sec, text="STOP", font=FONTS["btn"],
            fg_color=COLORS["red_dim"], hover_color=COLORS["red"],
            text_color=COLORS["red"], corner_radius=8, height=44,
            state="disabled", command=self._stop,
        )
        self._btn_stop.pack(fill="x", padx=4, pady=(0, 6))

        btn_row = ctk.CTkFrame(sec, fg_color="transparent")
        btn_row.pack(fill="x", padx=4, pady=(0, 4))
        ctk.CTkButton(
            btn_row, text="Clear", font=FONTS["btn_small"],
            fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["white"], corner_radius=8, height=32,
            command=self._clear,
        ).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ctk.CTkButton(
            btn_row, text="Export", font=FONTS["btn_small"],
            fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["white"], corner_radius=8, height=32,
            command=self._export,
        ).pack(side="left", expand=True, fill="x", padx=(3, 0))

    def _build_main_area(self):
        main = ctk.CTkFrame(self.root, fg_color=COLORS["bg"],
                            corner_radius=0)
        main.grid(row=1, column=1, sticky="nsew")
        main.grid_rowconfigure(2, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # stat cards
        stats_frame = ctk.CTkFrame(main, fg_color="transparent")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        for i in range(6):
            stats_frame.grid_columnconfigure(i, weight=1)
        stat_defs = [
            ("Total",   "total",   "#",   COLORS["white"]),
            ("Good",    "good",    "HIT", COLORS["green"]),
            ("Bad",     "bad",     "X",   COLORS["red"]),
            ("Invalid", "invalid", "?",   COLORS["yellow"]),
            ("Locked",  "locked",  "LCK", COLORS["magenta"]),
            ("Error",   "error",   "!",   COLORS["grey"]),
        ]
        for i in range(6):
            stats_frame.grid_columnconfigure(i, weight=1)
        self._stat_cards = {}
        for i, (label, key, icon, color) in enumerate(stat_defs):
            card = StatCard(stats_frame, label=label, icon=icon, color=color)
            card.grid(row=0, column=i, sticky="ew", padx=3, pady=3)
            self._stat_cards[key] = card

        # progress
        prog = ctk.CTkFrame(main, fg_color="transparent")
        prog.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 0))
        prog.grid_columnconfigure(0, weight=1)
        self._progress_bar = ctk.CTkProgressBar(
            prog, fg_color=COLORS["input_bg"],
            progress_color=COLORS["accent"], corner_radius=6, height=14,
        )
        self._progress_bar.grid(row=0, column=0, sticky="ew")
        self._progress_bar.set(0)
        self._lbl_progress = ctk.CTkLabel(
            prog, text="0 / 0   (0%)", font=FONTS["label_small"],
            text_color=COLORS["grey"],
        )
        self._lbl_progress.grid(row=0, column=1, padx=(10, 0))
        self._lbl_cpm = ctk.CTkLabel(
            prog, text="CPM: 0",
            font=(FONTS["mono"][0], 14, "bold"),
            text_color=COLORS["accent"],
        )
        self._lbl_cpm.grid(row=0, column=2, padx=(12, 0))

        # tabs
        self._tabs = ctk.CTkTabview(
            main, fg_color=COLORS["surface"],
            segmented_button_fg_color=COLORS["input_bg"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["input_bg"],
            segmented_button_unselected_hover_color=COLORS["btn_hover"],
            text_color=COLORS["white"],
            corner_radius=CORNER_RADIUS,
            border_width=1, border_color=COLORS["border"],
        )
        self._tabs.grid(row=2, column=0, sticky="nsew", padx=12, pady=(8, 10))

        tab_all = self._tabs.add("All Results")
        tab_good = self._tabs.add("Good Hits")
        tab_premium = self._tabs.add("2FA / Inbox  [PREMIUM]")

        self._build_all_tab(tab_all)
        self._build_good_tab(tab_good)
        self._build_premium_tab(tab_premium)

    def _build_all_tab(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        fbar = ctk.CTkFrame(parent, fg_color="transparent")
        fbar.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 4))
        ctk.CTkLabel(fbar, text="Filter:", font=FONTS["label_small"],
                     text_color=COLORS["grey"]).pack(side="left")
        self._filter_var = ctk.StringVar()
        ctk.CTkEntry(
            fbar, textvariable=self._filter_var, width=200, height=30,
            font=FONTS["mono_small"], fg_color=COLORS["input_bg"],
            border_color=COLORS["border"], text_color=COLORS["white"],
            placeholder_text="Search results...", corner_radius=6,
        ).pack(side="left", padx=(6, 0))
        self._filter_var.trace_add("write", lambda *_: self._apply_filter())

        self._txt_all = ResultTextbox(parent)
        self._txt_all.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

    def _build_good_tab(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        hbar = ctk.CTkFrame(parent, fg_color="transparent")
        hbar.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 4))
        ctk.CTkButton(
            hbar, text="Copy All", font=FONTS["btn_small"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_dark"], corner_radius=6, height=28,
            width=100, command=self._copy_good,
        ).pack(side="right")

        self._txt_good = ResultTextbox(parent)
        self._txt_good.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

    def _build_premium_tab(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkLabel(
            wrap, text="PREMIUM FEATURE",
            font=(FONTS["brand"][0], 22, "bold"),
            text_color=COLORS["accent"],
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            wrap,
            text=(
                "2FA detection, inbox access, inbox count,\n"
                "and direct inbox login are premium features.\n\n"
                "Join our Telegram to get the Premium version:"
            ),
            font=FONTS["label"],
            text_color=COLORS["grey"],
            justify="center",
        ).pack(pady=(0, 16))

        ctk.CTkButton(
            wrap, text="Get Premium  --  Join Telegram",
            font=FONTS["btn"],
            fg_color="#2CA5E0", hover_color="#1A8FC4",
            text_color="#ffffff", corner_radius=10, height=48,
            width=320,
            command=lambda: __import__("webbrowser").open(
                "https://t.me/zerozpanel"),
        ).pack()

        ctk.CTkLabel(
            wrap, text="t.me/zerozpanel",
            font=FONTS["mono_small"],
            text_color=COLORS["border"],
        ).pack(pady=(10, 0))

    def _build_status_bar(self):
        bar = ctk.CTkFrame(self.root, fg_color=COLORS["bg_dark"],
                           height=30, corner_radius=0)
        bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)
        self._lbl_status = ctk.CTkLabel(
            bar, text="Ready", font=FONTS["status"],
            text_color=COLORS["grey"],
        )
        self._lbl_status.pack(side="left", padx=12)
        ctk.CTkLabel(
            bar, text="ZEROZ v1.0.0  |  Free & Open Source  |  t.me/zerozpanel",
            font=(FONTS["status"][0], 12), text_color=COLORS["border"],
        ).pack(side="right", padx=12)

    # ══════════════════════════════════════════════════════════════════════════
    #  File loading
    # ══════════════════════════════════════════════════════════════════════════

    def _load_combos(self):
        path = filedialog.askopenfilename(
            title="Select combo file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        with open(path, encoding="utf-8", errors="ignore") as f:
            self._combos = [l.strip() for l in f if l.strip() and ":" in l]
        name = os.path.basename(path)
        self._lbl_combo.configure(
            text=f"{name}  ({len(self._combos)} combos)",
            text_color=COLORS["green"])
        self._set_status(f"Loaded {len(self._combos)} combos from {name}")

    def _load_proxies(self):
        path = filedialog.askopenfilename(
            title="Select proxy list",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        with open(path, encoding="utf-8", errors="ignore") as f:
            self._proxies = [
                l.strip() for l in f
                if l.strip() and not l.strip().startswith("#")]
        self._proxy_iter = itertools.cycle(self._proxies)
        name = os.path.basename(path)
        self._lbl_pfile.configure(
            text=f"{name}  ({len(self._proxies)} proxies)",
            text_color=COLORS["green"])
        self._set_status(f"Loaded {len(self._proxies)} proxies from {name}")

    # ══════════════════════════════════════════════════════════════════════════
    #  Checker control
    # ══════════════════════════════════════════════════════════════════════════

    def _start(self):
        if not self._combos:
            messagebox.showwarning("No combos",
                                   "Please load a combo file first.")
            return
        if self._running:
            return

        single = self._ent_proxy.get().strip()
        if single:
            self._proxy_iter = itertools.cycle([single])
        elif not self._proxies:
            self._proxy_iter = None

        self._running = True
        self._stop_evt.clear()
        self._t_start = time.time()
        for k in self._stats:
            self._stats[k] = 0
        self._update_stat_cards()
        self._progress_bar.set(0)

        self._btn_start.configure(state="disabled")
        self._btn_stop.configure(state="normal")
        self._set_status("Running...")

        combos = list(self._combos)
        self._total_combos = len(combos)

        threading.Thread(
            target=self._run_worker,
            args=(combos, self._var_threads.get(),
                  self._var_timeout.get(), self._var_retries.get()),
            daemon=True,
        ).start()

    def _stop(self):
        self._stop_evt.set()
        self._set_status("Stopping...")

    def _run_worker(self, combos, threads_n, timeout_v, retries_v):
        q = queue.Queue()
        for combo in combos:
            q.put(combo)

        def do_check(combo):
            if self._stop_evt.is_set():
                return
            email, _, pwd = combo.partition(":")
            email, pwd = email.strip(), pwd.strip()
            result, detail = "ERROR", "not run"
            for attempt in range(1 + retries_v):
                if self._stop_evt.is_set():
                    return
                px = self._next_proxy()
                try:
                    result, detail = check_account(
                        email, pwd, proxies=px, timeout=timeout_v)
                except Exception as ex:
                    result, detail = "ERROR", str(ex)
                if result != "ERROR":
                    break
                time.sleep(1.2 * (attempt + 1))
            self._result_q.put((result, email, pwd, detail))

        workers = []
        for _ in range(min(threads_n, len(combos))):
            def worker_loop():
                while not self._stop_evt.is_set():
                    try:
                        combo = q.get_nowait()
                    except queue.Empty:
                        break
                    do_check(combo)
                    q.task_done()
            t = threading.Thread(target=worker_loop, daemon=True)
            t.start()
            workers.append(t)

        for w in workers:
            w.join()
        self._result_q.put(("__DONE__", "", "", ""))

    # ══════════════════════════════════════════════════════════════════════════
    #  Result polling & display
    # ══════════════════════════════════════════════════════════════════════════

    def _poll_results(self):
        batch = 0
        try:
            while batch < 50:
                item = self._result_q.get_nowait()
                result, email, pwd, detail = item
                if result == "__DONE__":
                    self._on_done()
                    break
                self._process_result(result, email, pwd, detail)
                batch += 1
        except queue.Empty:
            pass
        self.root.after(80, self._poll_results)

    def _process_result(self, result, email, pwd, detail):
        self._stats["total"] += 1

        if result == "2FA":
            display_result = "LOCKED"
            display_detail = "2FA detected -- upgrade to Premium for 2FA capture"
            self._stats["locked"] += 1
        else:
            display_result = result
            display_detail = detail
            key = result.lower().replace("-", "")
            if key in self._stats:
                self._stats[key] += 1

        combo = f"{email}:{pwd}"
        line = f"[{display_result:<7}]  {combo:<45}  {display_detail}\n"

        self._all_results.append((display_result, line))
        self._update_stat_cards()
        self._update_progress()

        flt = self._filter_var.get().lower()
        if not flt or flt in line.lower():
            self._txt_all.append(line, display_result)

        if result == "GOOD":
            self._good_list.append((email, pwd, detail))
            self._txt_good.append(
                f"{combo}  |  {detail}\n", "GOOD")

    def _update_stat_cards(self):
        for key, card in self._stat_cards.items():
            card.set_value(self._stats[key])

    def _update_progress(self):
        total = getattr(self, "_total_combos", 0)
        checked = self._stats["total"]
        if total > 0:
            pct = checked / total
            self._progress_bar.set(pct)
            self._lbl_progress.configure(
                text=f"{checked} / {total}   ({pct:.0%})")
        elapsed = max(time.time() - self._t_start, 1)
        cpm = int((checked / elapsed) * 60)
        self._lbl_cpm.configure(text=f"CPM: {cpm}")

    def _on_done(self):
        self._running = False
        self._btn_start.configure(state="normal")
        self._btn_stop.configure(state="disabled")
        elapsed = time.time() - self._t_start
        cpm = int((self._stats["total"] / max(elapsed, 1)) * 60)
        self._set_status(
            f"Done  |  Total={self._stats['total']}  "
            f"Good={self._stats['good']}  "
            f"Locked={self._stats['locked']}  "
            f"CPM={cpm}  Time={elapsed:.0f}s")
        self._progress_bar.set(1)

    def _apply_filter(self):
        flt = self._filter_var.get().lower()
        filtered = [
            (tag, text) for tag, text in self._all_results
            if not flt or flt in text.lower()
        ]
        self._txt_all.replace_all(filtered)

    # ══════════════════════════════════════════════════════════════════════════
    #  Actions
    # ══════════════════════════════════════════════════════════════════════════

    def _set_status(self, msg):
        self._lbl_status.configure(text=msg)

    def _clear(self):
        self._all_results.clear()
        self._good_list.clear()
        self._txt_all.clear()
        self._txt_good.clear()
        for k in self._stats:
            self._stats[k] = 0
        self._update_stat_cards()
        self._progress_bar.set(0)
        self._lbl_progress.configure(text="0 / 0   (0%)")
        self._lbl_cpm.configure(text="CPM: 0")
        self._set_status("Cleared")

    def _copy_good(self):
        lines = [f"{e}:{p}  |  {d}" for e, p, d in self._good_list]
        if not lines:
            messagebox.showinfo("Copy", "No good accounts found yet.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(lines))
        self._set_status(f"Copied {len(lines)} good account(s) to clipboard")

    def _export(self):
        accounts = self._good_list
        if not accounts:
            messagebox.showinfo("Export", "No good accounts to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="good_accounts.txt")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            for e, p, d in accounts:
                f.write(f"{e}:{p}  |  {d}\n")
        self._set_status(f"Exported {len(accounts)} account(s) to {path}")

    def run(self):
        self.root.mainloop()
