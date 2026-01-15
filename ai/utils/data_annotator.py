import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os


class DiceAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("Dice Dataset Annotator")

        self.input_dir = "data/inputs"
        self.target_dir = "data/targets"

        # Ensure output directories exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.target_dir, exist_ok=True)

        # GUI elements
        self.listbox = tk.Listbox(root, width=50)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind("<<ListboxSelect>>", self.on_image_select)

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.btn_new = tk.Button(
            root, text="New Annotation", command=self.new_annotation
        )
        self.btn_new.pack(side=tk.TOP)

        self.btn_view = tk.Button(
            root, text="View Existing", command=self.view_existing
        )
        self.btn_view.pack(side=tk.TOP)

        self.btn_save = tk.Button(root, text="Save", command=self.save_annotation)
        self.btn_save.pack(side=tk.TOP)

        self.load_images()

        self.current_image_path = None
        self.annotations = []  # list of (x, y, w, h, pips)
        self.drawing = False
        self.start_x = self.start_y = 0
        self.current_rect = None

    def load_images(self):
        self.listbox.delete(0, tk.END)  # Clear the listbox
        if os.path.exists(self.input_dir):
            images = []
            for f in os.listdir(self.input_dir):
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    is_annotated = self.is_annotated(f)
                    images.append((f, is_annotated))

            # Sort: not annotated first, then annotated, then by name
            images.sort(key=lambda x: (x[1], x[0]))  # x[1] is bool, False < True

            for img, is_annotated in images:
                status = "Annotated" if is_annotated else "Not Annotated"
                self.listbox.insert(tk.END, f"{img} - {status}")

    def is_annotated(self, img_name):
        base = os.path.splitext(img_name)[0]
        return os.path.exists(os.path.join(self.target_dir, base + ".txt"))

    def on_image_select(self, _):
        selection = self.listbox.curselection()
        if selection:
            item = self.listbox.get(selection[0])
            img_name = item.split(" - ")[0]
            self.current_image_path = os.path.join(self.input_dir, img_name)
            self.display_image(self.current_image_path)
            self.load_and_draw_annotations(img_name)

    def display_image(self, path):
        self.canvas.delete(tk.ALL)  # Clear all canvas items
        self.canvas.update_idletasks()
        self.image = Image.open(path)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.update_idletasks()

    def new_annotation(self):
        if not self.current_image_path:
            messagebox.showerror("Error", "Select an image first")
            return
        self.annotations = []
        self.drawing = False
        self.current_rect = None
        self.display_image(self.current_image_path)
        self.canvas.update_idletasks()
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down_rect)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag_rect)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up_rect)

    def view_existing(self):
        if not self.current_image_path:
            messagebox.showerror("Error", "Select an image first")
            return
        # Load original image
        self.display_image(self.current_image_path)
        # Load and draw annotations
        img_name = os.path.basename(self.current_image_path)
        self.load_and_draw_annotations(img_name)
        # No binding for editing

    def on_mouse_down_rect(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.drawing = True

    def on_mouse_drag_rect(self, event):
        if self.drawing:
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            if self.current_rect:
                self.canvas.delete(self.current_rect)
            x1 = int(min(self.start_x, cur_x))
            y1 = int(min(self.start_y, cur_y))
            x2 = int(max(self.start_x, cur_x))
            y2 = int(max(self.start_y, cur_y))
            self.current_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline="red"
            )

    def on_mouse_up_rect(self, event):
        if self.drawing:
            self.drawing = False
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            x = int(min(self.start_x, cur_x))
            y = int(min(self.start_y, cur_y))
            w = int(abs(cur_x - self.start_x))
            h = int(abs(cur_y - self.start_y))
            if w > 0 and h > 0:
                pips = simpledialog.askinteger("Pips", "Enter dice value (1-6):")
                if pips and 1 <= pips <= 6:
                    self.annotations.append((x, y, w, h, pips))
                    self.draw_annotations()
                    self.canvas.update_idletasks()
            if self.current_rect:
                self.canvas.delete(self.current_rect)
                self.current_rect = None

    def load_and_draw_annotations(self, img_name):
        if self.is_annotated(img_name):
            base = os.path.splitext(img_name)[0]
            label_path = os.path.join(self.target_dir, base + ".txt")
            with open(label_path, "r") as f:
                self.annotations = []
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        x, y, w, h, pips = (
                            int(parts[0]),
                            int(parts[1]),
                            int(parts[2]),
                            int(parts[3]),
                            int(parts[4]),
                        )
                        self.annotations.append((x, y, w, h, pips))
            self.draw_annotations()
        else:
            self.annotations = []

    def draw_annotations(self):
        self.canvas.delete("annotation")
        self.canvas.update_idletasks()
        for x, y, w, h, pips in self.annotations:
            self.canvas.create_rectangle(
                x, y, x + w, y + h, outline="blue", tags="annotation"
            )
            self.canvas.create_text(
                x + w // 2,
                y - 5,
                text=str(pips),
                fill="red",
                tags="annotation",
                font=("Arial", 24, "bold"),
            )
        self.canvas.update_idletasks()

    def save_annotation(self):
        if not self.annotations:
            messagebox.showerror("Error", "No annotation to save")
            return
        base = os.path.splitext(os.path.basename(self.current_image_path))[0]  # type: ignore
        label_path = os.path.join(self.target_dir, base + ".txt")
        with open(label_path, "w") as f:
            for x, y, w, h, pips in self.annotations:
                f.write(f"{x} {y} {w} {h} {pips}\n")
        self.load_images()


if __name__ == "__main__":
    root = tk.Tk()
    app = DiceAnnotator(root)
    root.mainloop()
