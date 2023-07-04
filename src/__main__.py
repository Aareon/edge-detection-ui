import tkinter as tk
from tkinter import filedialog

import cv2
import numpy as np
from PIL import Image, ImageTk


def open_image():
    # Load the image
    image_path = filedialog.askopenfile(
        filetypes=[("Image files", "*.jpg *.jpeg *.bmp")]
    )
    if image_path is None:
        return
    image = Image.open(image_path.name)
    return image


def get_edges(image, t_lower, t_upper):
    # Apply Canny edge detection
    edges = cv2.Canny(image, t_lower, t_upper)
    return edges


def convert_from_cv2_to_image(img: np.ndarray) -> Image:
    # return Image.fromarray(img)
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def convert_from_image_to_cv2(img: Image) -> np.ndarray:
    # return np.asarray(img)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


class App:
    def __init__(self):
        self.root = tk.Tk()

        self.pil_image = None  # Pillow image
        self.tk_image = None  # Tkinter image
        self.image = None  # Selected by user / cvimage

        self.pil_edges = None
        self.edges = None  # Generated using Canny
        self.tk_edges = None

        self.threshold1 = tk.StringVar()
        self.threshold2 = tk.StringVar()

        self.selected_slider = None  # updated every time a slider is clicked
        self.has_updated = False  # set the first time the edges are updated

    def update_image(self):
        image = open_image()
        if image is None:
            return

        self.pil_image = image.resize((200, 200))
        self.image = convert_from_image_to_cv2(self.pil_image)
        self.tk_image = ImageTk.PhotoImage(self.pil_image)
        self.image1.configure(image=self.tk_image)

        if not self.has_updated:
            self.update_edges()
            self.has_updated = True

    def save_edges(self):
        if self.edges is None:
            return
        # fmt: off
        fp = filedialog.asksaveasfile(
                filetypes=[("PNG Image", "*.png")],
                defaultextension="*.png",
        )
        # fmt: on
        if fp is None:
            return
        self.pil_edges.save(fp.name, format="png")

    def update_edges(self, *args):
        if self.image is None:
            return
        cv2_img = get_edges(
            self.image, float(self.threshold1.get()), float(self.threshold2.get())
        )
        self.edges = cv2_img
        self.pil_edges = convert_from_cv2_to_image(self.edges)
        self.tk_edges = ImageTk.PhotoImage(self.pil_edges)

        self.image2.configure(image=self.tk_edges)

    def handle_slider_arrows(self, event: tk.Event):
        if self.selected_slider is None:
            return

        if self.selected_slider == "lower":
            slider = self.t_lower_slider
        else:
            slider = self.t_upper_slider

        curr_val = slider.get()
        if event.keysym == "Left":
            slider.set(curr_val - 1)
        elif event.keysym == "Right":
            slider.set(curr_val + 1)

        if event.type == "3":
            print("updating")
            self.update_edges()

    def handle_slider_clicked(self, name):
        self.selected_slider = name
        self.update_edges()

    def run(self):
        self.root.wm_title("Edge Detector")
        # Create a blank white image for placeholder
        width, height = 200, 200
        white_pil_image = Image.new("RGB", (width, height), "white")
        white_image = ImageTk.PhotoImage(white_pil_image)

        image_frame = tk.Frame(self.root)
        self.image1 = tk.Label(image_frame, image=white_image)
        self.image1.pack(side="left", anchor="nw")

        self.image2 = tk.Label(image_frame, image=white_image)
        self.image2.pack(side="right", anchor="ne")
        image_frame.pack(side="top", expand=True, fill="x", padx=10)

        buttons_frame = tk.Frame(self.root)
        self.open_button = tk.Button(
            buttons_frame, text="Open Image", command=self.update_image
        )
        self.open_button.pack(side="left", anchor="center", padx=75)

        self.save_button = tk.Button(
            buttons_frame, text="Save Edges", command=self.save_edges
        )
        self.save_button.pack(side="right", anchor="center", padx=75)
        buttons_frame.pack(expand=True, fill="x")

        self.t_lower_slider = tk.Scale(
            self.root,
            from_=0,
            to=500,
            orient="horizontal",
            variable=self.threshold1,
            name="t_lower",
        )
        self.t_lower_slider.bind(
            "<ButtonRelease-1>", lambda x: self.handle_slider_clicked("lower")
        )
        self.t_lower_slider.pack(side="top", anchor="center")

        self.t_upper_slider = tk.Scale(
            self.root,
            from_=0,
            to=500,
            orient="horizontal",
            variable=self.threshold2,
            name="t_upper",
        )
        self.t_upper_slider.bind(
            "<ButtonRelease-1>", lambda x: self.handle_slider_clicked("upper")
        )
        self.t_upper_slider.pack(side="top", anchor="center")

        self.update_button = tk.Button(
            self.root, text="Update Edges", command=self.update_edges
        )
        self.update_button.pack(side="bottom", anchor="center", pady=10)

        self.root.bind("<Left>", self.handle_slider_arrows)
        self.root.bind("<KeyRelease>", self.handle_slider_arrows)
        self.root.bind("<Right>", self.handle_slider_arrows)
        self.root.bind("<KeyRelease>", self.handle_slider_arrows)

        self.root.mainloop()


if __name__ == "__main__":
    App().run()
