import tkinter as tk

class StyleGUI:
    def __init__(self): 

        self.style_values = {
            "BG_COLOR": "#23272f",
            "BTN_BG": "#334155",
            "BTN_FG": "#f1f5f9",
            "BTN_ACTIVE_BG": "#475569",
            "BTN_ACTIVE_FG": "#ffffff",
            "TEXT_BG": "#1e293b",
            "TEXT_FG": "#f1f5f9",
            "LABEL_FG": "#a3a3a3",
            "FONT": ("Consolas", 12),
            "BTN_FONT": ("Segoe UI", 11, "bold"),
        }

    def button(self, parent, **kwargs):
        style = self.style_values
        kwargs.setdefault("font", style["BTN_FONT"])
        kwargs.setdefault("bg", style["BTN_BG"])
        kwargs.setdefault("fg", style["BTN_FG"])
        kwargs.setdefault("activebackground", style["BTN_ACTIVE_BG"])
        kwargs.setdefault("activeforeground", style["BTN_ACTIVE_FG"])
        return tk.Button(
            parent,
            relief="flat",
            cursor="hand2",
            bd=0,
            highlightthickness=0,
            pady=7, padx=14,
            **kwargs
        )

    def label(self, parent, **kwargs):
        style = self.style_values
        kwargs.setdefault("font", style["FONT"])
        kwargs.setdefault("bg", style["BG_COLOR"])
        kwargs.setdefault("fg", style["LABEL_FG"])
        return tk.Label(parent, **kwargs)

    def frame(self, parent, **kwargs):
        style = self.style_values
        kwargs.setdefault("bg", style["BG_COLOR"])
        return tk.Frame(parent, **kwargs)

    def labelframe(self, parent, text):
        style = self.style_values
        return tk.LabelFrame(
            parent,
            text=text,
            bg=style["BG_COLOR"],
            fg=style["LABEL_FG"],
            font=(style["FONT"][0], 13, "bold"),
            bd=2,
            relief="ridge",
            labelanchor="nw",
            padx=12, pady=8
        )

    def entry(self, parent, **kwargs):
        style = self.style_values
        kwargs.setdefault("font", style["FONT"])
        kwargs.setdefault("bg", style["TEXT_BG"])
        kwargs.setdefault("fg", style["TEXT_FG"])
        kwargs.setdefault("insertbackground", style["TEXT_FG"])
        kwargs.setdefault("relief", "solid")
        kwargs.setdefault("bd", 1)
        kwargs.setdefault("width", 32)
        return tk.Entry(parent, **kwargs)

    def radiobutton(self, parent, **kwargs):
        style = self.style_values
        kwargs.setdefault("font", style["FONT"])
        kwargs.setdefault("bg", style["BG_COLOR"])
        kwargs.setdefault("fg", style["TEXT_FG"])
        kwargs.setdefault("activebackground", style["BG_COLOR"])
        kwargs.setdefault("activeforeground", style["BTN_ACTIVE_FG"])
        kwargs.setdefault("selectcolor", style["BTN_BG"])
        kwargs.setdefault("highlightthickness", 0)
        return tk.Radiobutton(parent, **kwargs)
    
    def text(self,parent,**kwargs):
        style = self.style_values
        kwargs.setdefault("bg",style["TEXT_BG"])
        kwargs.setdefault("fg",style["TEXT_FG"])
        kwargs.setdefault("font",style["FONT"])
        kwargs.setdefault("insertbackground",style["BTN_ACTIVE_FG"])
        kwargs.setdefault("wrap","word")
        kwargs.setdefault("borderwidth",0)
        kwargs.setdefault("highlightthickness",0)
        return tk.Text(parent,**kwargs)


if __name__=="__main__":
    pass