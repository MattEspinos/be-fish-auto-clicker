import tkinter, customtkinter, keyboard, threading, time, sys, random
from tkinter import messagebox
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Listener


class MouseApp:
    def __init__(self, root):
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        self.root = root
        self.root.geometry("450x420")
        self.root.title("Mouse Hold and Clicker")

        self.mouse = MouseController()
        self.keyboard_ctrl = KeyboardController()

        self.mouse_held = {"left": False, "right": False}
        self.clicker_running = False
        self.clicker_thread = None
        self.user_initiated_click = False

        self.in_hold_page = False
        self.in_clicker_page = False

        # Double click delay (seconds)
        self.double_click_delay = 0.06  # 60 ms default

        self.create_welcome_page()

        threading.Thread(target=self.start_keyboard_listener, daemon=True).start()

    # ---------------- UI PAGES ---------------- #

    def create_welcome_page(self):
        self.clear_frame()

        customtkinter.CTkLabel(
            self.root,
            text="Welcome to the Mouse Hold and Clicker App!\n\nSelect an option:",
            font=(None, 20),
            text_color="lightblue"
        ).grid(row=0, column=0, columnspan=2, pady=20)

        customtkinter.CTkButton(
            self.root, text="Hold Mouse", command=self.create_hold_mouse_page
        ).grid(row=1, column=0, padx=10, pady=50)

        customtkinter.CTkButton(
            self.root, text="Mouse Clicker", command=self.create_mouse_clicker_page
        ).grid(row=1, column=1, padx=10, pady=50)

    def create_hold_mouse_page(self):
        self.clear_frame()
        keyboard.unhook_all()

        self.in_hold_page = True
        self.in_clicker_page = False

        self.var_mouse_button = customtkinter.StringVar(value="left")

        customtkinter.CTkButton(
            self.root, text="Back", command=self.create_welcome_page
        ).grid(row=0, column=0, sticky="nw", padx=10)

        customtkinter.CTkLabel(
            self.root, text="Hold Mouse", font=(None, 30)
        ).grid(row=1, column=0, columnspan=2, pady=20)

        customtkinter.CTkRadioButton(
            self.root, text="Left Mouse",
            variable=self.var_mouse_button, value="left"
        ).grid(row=2, column=0)

        customtkinter.CTkRadioButton(
            self.root, text="Right Mouse",
            variable=self.var_mouse_button, value="right"
        ).grid(row=2, column=1)

        self.label_hold_status = customtkinter.CTkLabel(
            self.root, text="Mouse Hold Status: OFF", font=(None, 18)
        )
        self.label_hold_status.grid(row=3, column=0, columnspan=2, pady=15)

        customtkinter.CTkLabel(
            self.root, text="Press '=' to toggle Mouse Hold"
        ).grid(row=4, column=0, columnspan=2)

        keyboard.on_press_key("=", lambda _: self.toggle_mouse_hold())
        keyboard.on_press_key("-", lambda _: self.close_program())

    def create_mouse_clicker_page(self):
        self.clear_frame()
        keyboard.unhook_all()

        self.in_hold_page = False
        self.in_clicker_page = True

        self.var_mouse_button = customtkinter.StringVar(value="left")

        customtkinter.CTkButton(
            self.root, text="Back", command=self.create_welcome_page
        ).grid(row=0, column=0, sticky="nw", padx=10)

        customtkinter.CTkLabel(
            self.root, text="Mouse Clicker", font=(None, 30)
        ).grid(row=1, column=0, columnspan=2, pady=15)

        customtkinter.CTkRadioButton(
            self.root, text="Left Mouse",
            variable=self.var_mouse_button, value="left"
        ).grid(row=2, column=0)

        customtkinter.CTkRadioButton(
            self.root, text="Right Mouse",
            variable=self.var_mouse_button, value="right"
        ).grid(row=2, column=1)

        customtkinter.CTkLabel(
            self.root, text="Interval (seconds):"
        ).grid(row=3, column=0, pady=(10, 0))

        self.combobox_interval = customtkinter.CTkComboBox(
            self.root,
            values=["0.01", "0.1", "0.5", "1", "2", "3", "5", "10", "60", "600"],
            state="readonly"
        )
        self.combobox_interval.set("1")
        self.combobox_interval.grid(row=3, column=1, pady=(10, 0))

        # Double-click delay slider
        customtkinter.CTkLabel(
            self.root, text="Double Click Delay (ms):"
        ).grid(row=4, column=0, pady=(15, 0))

        self.double_click_slider = customtkinter.CTkSlider(
            self.root,
            from_=20,
            to=150,
            number_of_steps=130,
            command=self.update_double_click_delay
        )
        self.double_click_slider.set(60)
        self.double_click_slider.grid(row=4, column=1, pady=(15, 0), sticky="w")

        self.double_click_value_label = customtkinter.CTkLabel(
            self.root, text="60 ms"
        )
        self.double_click_value_label.grid(row=5, column=0, columnspan=2)

        self.label_clicker_status = customtkinter.CTkLabel(
            self.root, text="Mouse Clicker Status: OFF", font=(None, 18)
        )
        self.label_clicker_status.grid(row=6, column=0, columnspan=2, pady=15)

        customtkinter.CTkLabel(
            self.root, text="Press '=' to toggle Mouse Clicker"
        ).grid(row=7, column=0, columnspan=2)

        keyboard.on_press_key("=", lambda _: self.toggle_mouse_clicker())
        keyboard.on_press_key("-", lambda _: self.close_program())

    # ---------------- CORE LOGIC ---------------- #

    def update_double_click_delay(self, value):
        self.double_click_delay = float(value) / 1000
        self.double_click_value_label.configure(text=f"{int(value)} ms")

    def toggle_mouse_clicker(self):
        if self.clicker_running:
            self.clicker_running = False
            self.label_clicker_status.configure(
                text="Mouse Clicker Status: OFF",
                text_color="lightblue"
            )
            return

        if not self.in_clicker_page:
            return

        try:
            interval = float(self.combobox_interval.get())
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid interval value.")
            return

        button = Button.left if self.var_mouse_button.get() == "left" else Button.right

        self.clicker_running = True
        self.clicker_thread = threading.Thread(
            target=self.clicker_loop, args=(button, interval), daemon=True
        )
        self.clicker_thread.start()

        self.label_clicker_status.configure(
            text="Mouse Clicker Status: ON",
            text_color="red"
        )

    def clicker_loop(self, button, interval):
        keys = ["w", "a", "s", "d"]

        while self.clicker_running:
            if not self.mouse_held[self.var_mouse_button.get()] and not self.user_initiated_click:
                # First click
                self.mouse.press(button)
                self.mouse.release(button)

                # Delay between clicks
                time.sleep(self.double_click_delay)

                # Second click
                self.mouse.press(button)
                self.mouse.release(button)

                # Random WASD key
                key = random.choice(keys)
                self.keyboard_ctrl.press(key)
                self.keyboard_ctrl.release(key)

            self.user_initiated_click = False
            time.sleep(interval)

    def toggle_mouse_hold(self):
        if not self.in_hold_page:
            return

        mouse_button = self.var_mouse_button.get()
        btn = Button.left if mouse_button == "left" else Button.right

        if self.mouse_held[mouse_button]:
            self.mouse.release(btn)
            self.mouse_held[mouse_button] = False
            self.label_hold_status.configure(
                text="Mouse Hold Status: OFF",
                text_color="lightblue"
            )
        else:
            self.mouse.press(btn)
            self.mouse_held[mouse_button] = True
            self.user_initiated_click = True
            self.label_hold_status.configure(
                text="Mouse Hold Status: ON",
                text_color="red"
            )

    # ---------------- SYSTEM ---------------- #

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_keyboard_listener(self):
        with Listener(on_press=self.on_key_press) as listener:
            listener.join()

    def on_key_press(self, key):
        try:
            if key.char == "-":
                self.close_program()
        except AttributeError:
            pass

    def close_program(self):
        self.root.destroy()
        sys.exit()


if __name__ == "__main__":
    root = customtkinter.CTk()
    app = MouseApp(root)
    root.mainloop()
