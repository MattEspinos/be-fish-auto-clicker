import tkinter, customtkinter, keyboard, threading, time, sys, random
from tkinter import messagebox
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Listener


class MouseApp:
    def __init__(self, root):
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        self.root = root
        self.root.geometry("500x480")
        self.root.title("Mouse Utility Suite")

        self.root.grid_columnconfigure((0, 1), weight=1)

        self.mouse = MouseController()
        self.keyboard_ctrl = KeyboardController()

        self.mouse_held = {"left": False, "right": False}
        self.clicker_running = False
        self.farm_running = False

        self.double_click_delay = 0.06

        self.in_hold_page = False
        self.in_clicker_page = False
        self.in_farm_page = False

        self.create_welcome_page()

        threading.Thread(target=self.start_keyboard_listener, daemon=True).start()

    # ---------------- MAIN MENU ---------------- #

    def create_welcome_page(self):
        self.clear_frame()
        keyboard.unhook_all()

        customtkinter.CTkLabel(
            self.root,
            text="Welcome!\n\nSelect an option:",
            font=(None, 22),
            text_color="lightblue",
            justify="center",
            anchor="center"
        ).grid(row=0, column=0, columnspan=2, pady=40, sticky="n")

        customtkinter.CTkButton(self.root, text="Hold Mouse",
            command=self.create_hold_mouse_page)\
            .grid(row=1, column=0, columnspan=2, pady=15)

        customtkinter.CTkButton(self.root, text="Mouse Clicker",
            command=self.create_mouse_clicker_page)\
            .grid(row=2, column=0, columnspan=2, pady=15)

        customtkinter.CTkButton(self.root, text="Break Bones AFK Farm",
            command=self.create_farm_page)\
            .grid(row=3, column=0, columnspan=2, pady=15)

    # ---------------- HOLD PAGE ---------------- #

    def create_hold_mouse_page(self):
        self.clear_frame()
        keyboard.unhook_all()

        self.in_hold_page = True
        self.in_clicker_page = False
        self.in_farm_page = False

        self.var_mouse_button = customtkinter.StringVar(value="left")

        customtkinter.CTkButton(self.root, text="Back",
            command=self.create_welcome_page)\
            .grid(row=0, column=0, columnspan=2, pady=10)

        customtkinter.CTkLabel(self.root, text="Hold Mouse",
            font=(None, 28), justify="center", anchor="center")\
            .grid(row=1, column=0, columnspan=2, pady=20)

        customtkinter.CTkRadioButton(self.root, text="Left Mouse",
            variable=self.var_mouse_button, value="left")\
            .grid(row=2, column=0, columnspan=2, pady=5)

        customtkinter.CTkRadioButton(self.root, text="Right Mouse",
            variable=self.var_mouse_button, value="right")\
            .grid(row=3, column=0, columnspan=2, pady=5)

        self.label_hold_status = customtkinter.CTkLabel(
            self.root, text="Mouse Hold Status: OFF",
            font=(None, 18), justify="center", anchor="center")
        self.label_hold_status.grid(row=4, column=0, columnspan=2, pady=20)

        customtkinter.CTkLabel(self.root,
            text="Press '=' to toggle\nPress '-' to close program",
            justify="center", anchor="center")\
            .grid(row=5, column=0, columnspan=2, pady=10)

        keyboard.on_press_key("=", lambda _: self.toggle_mouse_hold())
        keyboard.on_press_key("-", lambda _: self.close_program())

    # ---------------- CLICKER PAGE ---------------- #

    def create_mouse_clicker_page(self):
        self.clear_frame()
        keyboard.unhook_all()

        self.in_hold_page = False
        self.in_clicker_page = True
        self.in_farm_page = False

        self.var_mouse_button = customtkinter.StringVar(value="left")

        customtkinter.CTkButton(self.root, text="Back",
            command=self.create_welcome_page)\
            .grid(row=0, column=0, columnspan=2, pady=10)

        customtkinter.CTkLabel(self.root, text="Mouse Clicker",
            font=(None, 28), justify="center", anchor="center")\
            .grid(row=1, column=0, columnspan=2, pady=15)

        customtkinter.CTkRadioButton(self.root, text="Left Mouse",
            variable=self.var_mouse_button, value="left")\
            .grid(row=2, column=0, columnspan=2, pady=5)

        customtkinter.CTkRadioButton(self.root, text="Right Mouse",
            variable=self.var_mouse_button, value="right")\
            .grid(row=3, column=0, columnspan=2, pady=5)

        customtkinter.CTkLabel(self.root,
            text="Interval (seconds):",
            justify="center", anchor="center")\
            .grid(row=4, column=0, columnspan=2)

        self.combobox_interval = customtkinter.CTkComboBox(
            self.root, values=["0.1","0.5","1","2","3","5","10"], state="readonly")
        self.combobox_interval.set("1")
        self.combobox_interval.grid(row=5, column=0, columnspan=2, pady=5)

        customtkinter.CTkLabel(self.root,
            text="Double Click Delay (ms):",
            justify="center", anchor="center")\
            .grid(row=6, column=0, columnspan=2, pady=10)

        self.double_click_slider = customtkinter.CTkSlider(
            self.root, from_=20, to=150, number_of_steps=130,
            command=self.update_double_click_delay)
        self.double_click_slider.set(60)
        self.double_click_slider.grid(row=7, column=0, columnspan=2, pady=5)

        self.double_click_value_label = customtkinter.CTkLabel(
            self.root, text="60 ms",
            justify="center", anchor="center")
        self.double_click_value_label.grid(row=8, column=0, columnspan=2)

        self.label_clicker_status = customtkinter.CTkLabel(
            self.root, text="Mouse Clicker Status: OFF",
            font=(None,18), justify="center", anchor="center")
        self.label_clicker_status.grid(row=9, column=0, columnspan=2, pady=15)

        customtkinter.CTkLabel(self.root,
            text="Press '=' to toggle\nPress '-' to close program",
            justify="center", anchor="center")\
            .grid(row=10, column=0, columnspan=2)

        keyboard.on_press_key("=", lambda _: self.toggle_mouse_clicker())
        keyboard.on_press_key("-", lambda _: self.close_program())

    # ---------------- AFK FARM PAGE ---------------- #

    def create_farm_page(self):
        self.clear_frame()
        keyboard.unhook_all()

        self.in_hold_page = False
        self.in_clicker_page = False
        self.in_farm_page = True

        customtkinter.CTkButton(self.root, text="Back",
            command=self.create_welcome_page)\
            .grid(row=0, column=0, columnspan=2, pady=10)

        customtkinter.CTkLabel(self.root,
            text="Break Bones AFK Farm",
            font=(None, 28), justify="center", anchor="center")\
            .grid(row=1, column=0, columnspan=2, pady=20)

        self.label_farm_status = customtkinter.CTkLabel(
            self.root, text="AFK Farm Status: OFF",
            font=(None,18), justify="center", anchor="center")
        self.label_farm_status.grid(row=2, column=0, columnspan=2, pady=20)

        customtkinter.CTkLabel(self.root,
            text="Press '=' to toggle farm\nPress '-' to close program",
            justify="center", anchor="center")\
            .grid(row=3, column=0, columnspan=2)

        keyboard.on_press_key("=", lambda _: self.toggle_farm())
        keyboard.on_press_key("-", lambda _: self.close_program())

    # ---------------- LOGIC ---------------- #

    def update_double_click_delay(self, value):
        self.double_click_delay = float(value)/1000
        self.double_click_value_label.configure(text=f"{int(value)} ms")

    def toggle_mouse_clicker(self):
        if not self.in_clicker_page:
            return

        self.clicker_running = not self.clicker_running
        self.label_clicker_status.configure(
            text=f"Mouse Clicker Status: {'ON' if self.clicker_running else 'OFF'}",
            text_color="red" if self.clicker_running else "lightblue"
        )

        if self.clicker_running:
            threading.Thread(target=self.clicker_loop, daemon=True).start()

    def clicker_loop(self):
        interval=float(self.combobox_interval.get())
        button=Button.left if self.var_mouse_button.get()=="left" else Button.right
        keys=["w","a","s","d"]

        while self.clicker_running:
            self.mouse.press(button); self.mouse.release(button)
            time.sleep(self.double_click_delay)
            self.mouse.press(button); self.mouse.release(button)

            key=random.choice(keys)
            self.keyboard_ctrl.press(key); self.keyboard_ctrl.release(key)

            time.sleep(interval)

    def toggle_mouse_hold(self):
        if not self.in_hold_page:
            return

        btn = Button.left if self.var_mouse_button.get()=="left" else Button.right
        key=self.var_mouse_button.get()

        if self.mouse_held[key]:
            self.mouse.release(btn)
            self.mouse_held[key]=False
            self.label_hold_status.configure(text="Mouse Hold Status: OFF", text_color="lightblue")
        else:
            self.mouse.press(btn)
            self.mouse_held[key]=True
            self.label_hold_status.configure(text="Mouse Hold Status: ON", text_color="red")

    def toggle_farm(self):
        if not self.in_farm_page:
            return

        self.farm_running=not self.farm_running
        self.label_farm_status.configure(
            text=f"AFK Farm Status: {'ON' if self.farm_running else 'OFF'}",
            text_color="red" if self.farm_running else "lightblue"
        )

        if self.farm_running:
            threading.Thread(target=self.farm_loop, daemon=True).start()
        else:
            self.keyboard_ctrl.release("w")

    def farm_loop(self):
        self.keyboard_ctrl.press("w")
        while self.farm_running:
            self.keyboard_ctrl.press("e"); self.keyboard_ctrl.release("e")
            for _ in range(100):
                if not self.farm_running: break
                time.sleep(0.1)
        self.keyboard_ctrl.release("w")

    # ---------------- SYSTEM ---------------- #

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_keyboard_listener(self):
        with Listener(on_press=self.on_key_press) as listener:
            listener.join()

    def on_key_press(self,key):
        try:
            if key.char=="-":
                self.close_program()
        except AttributeError:
            pass

    def close_program(self):
        self.clicker_running=False
        self.farm_running=False
        self.root.destroy()
        sys.exit()


if __name__=="__main__":
    root=customtkinter.CTk()
    app=MouseApp(root)
    root.mainloop()
