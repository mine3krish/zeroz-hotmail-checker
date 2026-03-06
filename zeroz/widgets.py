"""
Reusable custom widget components for the ZEROZ GUI.
"""

import customtkinter as ctk
from zeroz.theme import COLORS, FONTS, CORNER_RADIUS


class StatCard(ctk.CTkFrame):
    """Compact stat card showing an icon, label, and value."""

    def __init__(self, master, label, icon, color, **kw):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
            **kw,
        )
        self._color = color

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 2))

        ctk.CTkLabel(
            top, text=icon, font=(FONTS["body"][0], 14),
            text_color=color,
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=label, font=FONTS["stat_label"],
            text_color=COLORS["grey"],
        ).pack(side="left", padx=(6, 0))

        self._value_label = ctk.CTkLabel(
            self, text="0", font=FONTS["stat_value"],
            text_color=color,
        )
        self._value_label.pack(padx=10, pady=(0, 10), anchor="w")

    def set_value(self, val):
        self._value_label.configure(text=str(val))


class SidebarSection(ctk.CTkFrame):
    """A titled section inside the sidebar."""

    def __init__(self, master, title, **kw):
        super().__init__(master, fg_color="transparent", **kw)

        header = ctk.CTkFrame(self, fg_color="transparent", height=28)
        header.pack(fill="x", padx=4, pady=(12, 4))
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text=title.upper(),
            font=(FONTS["section"][0], 12, "bold"),
            text_color=COLORS["accent"],
        ).pack(side="left")

        sep = ctk.CTkFrame(
            self, fg_color=COLORS["border"], height=1,
        )
        sep.pack(fill="x", padx=4, pady=(0, 6))


class ResultTextbox(ctk.CTkFrame):
    """A styled textbox for displaying results with color tags.

    Uses a raw tk.Text internally for maximum scroll performance.
    """

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=COLORS["surface"],
                         corner_radius=6, **kw)

        self._text = ctk.CTkTextbox(
            self,
            fg_color=COLORS["surface"],
            text_color=COLORS["white"],
            font=FONTS["mono_small"],
            wrap="none",
            activate_scrollbars=True,
            corner_radius=6,
        )
        self._text.pack(fill="both", expand=True, padx=2, pady=2)

        inner = self._text._textbox

        inner.tag_configure("GOOD", foreground=COLORS["green"])
        inner.tag_configure("2FA", foreground=COLORS["blue"])
        inner.tag_configure("BAD", foreground=COLORS["red"])
        inner.tag_configure("INVALID", foreground=COLORS["yellow"])
        inner.tag_configure("LOCKED", foreground=COLORS["magenta"])
        inner.tag_configure("ERROR", foreground=COLORS["grey"])
        inner.tag_configure("INFO", foreground=COLORS["accent"])

        self._text.configure(state="disabled")

    def append(self, text, tag=None):
        self._text.configure(state="normal")
        if tag:
            self._text._textbox.insert("end", text, tag)
        else:
            self._text._textbox.insert("end", text)
        self._text.configure(state="disabled")
        self._text._textbox.see("end")

    def clear(self):
        self._text.configure(state="normal")
        self._text._textbox.delete("1.0", "end")
        self._text.configure(state="disabled")

    def replace_all(self, lines):
        """Replace all content. `lines` = list of (tag, text)."""
        self._text.configure(state="normal")
        self._text._textbox.delete("1.0", "end")
        for tag, text in lines:
            self._text._textbox.insert("end", text, tag)
        self._text.configure(state="disabled")
