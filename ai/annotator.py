import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

from src.parse.config import load_config

class DiceAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("Dice Dataset Annotator")
        
        config = load_config(file_path="config/config.yml")

        self.input_dir = config.dataset_path + "/inputs"
        self.output_dir = config.dataset_path + "/targets"

        # Ensure output directories exist
        os.makedirs(self.output_dir, exist_ok=True)

        # GUI elements
        self.listbox = tk.Listbox(root, width=50)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', self.on_image_select)

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.btn_new = tk.Button(root, text="New Annotation", command=self.new_annotation)
        self.btn_new.pack(side=tk.TOP)

        self.btn_view = tk.Button(root, text="View Existing", command=self.view_existing)
        self.btn_view.pack(side=tk.TOP)

        self.btn_save = tk.Button(root, text="Save", command=self.save_annotation)
        self.btn_save.pack(side=tk.TOP)

        self.btn_accept = tk.Button(root, text="Accept", command=self.accept_prediction, state=tk.DISABLED)
        self.btn_accept.pack(side=tk.TOP)

        # Dice scores input
        score_frame = tk.Frame(root)
        score_frame.pack(side=tk.TOP, pady=5)
        tk.Label(score_frame, text="Dice 1:").pack(side=tk.LEFT)
        self.dice1_entry = tk.Entry(score_frame, width=3)
        self.dice1_entry.pack(side=tk.LEFT, padx=2)
        self.dice1_entry.insert(0, "1")
        tk.Label(score_frame, text="Dice 2:").pack(side=tk.LEFT, padx=(10, 0))
        self.dice2_entry = tk.Entry(score_frame, width=3)
        self.dice2_entry.pack(side=tk.LEFT, padx=2)
        self.dice2_entry.insert(0, "1")

        # Text file editor
        text_frame = tk.Frame(root)
        text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Label(text_frame, text="Annotation File:").pack(side=tk.TOP)
        self.text_editor = tk.Text(text_frame, height=8, width=50)
        self.text_editor.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.btn_save_text = tk.Button(text_frame, text="Save File", command=self.save_text_file)
        self.btn_save_text.pack(side=tk.TOP, padx=5, pady=2)

        self.load_images()

        self.current_image_path = None
        self.current_image_rel_path = None  # Relative path (e.g., "11/0001.png")
        self.current_label_path = None  # Path to current annotation file
        self.annotations = []  # list of (x, y, w, h, pips)
        self.drawing = False
        self.start_x = self.start_y = 0
        self.current_rect = None
        self.is_predicted = False  # Track if current image has a predicted annotation
        self.rect_counter = 0  # Counter for alternating between dice1 and dice2

    def load_images(self):
        self.listbox.delete(0, tk.END)  # Clear the listbox
        if os.path.exists(self.input_dir):
            images = []
            # Recursively find images in subfolders
            for root, dirs, files in os.walk(self.input_dir):
                for f in files:
                    if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                        # Get relative path (e.g., "11/0001.png")
                        rel_path = os.path.relpath(os.path.join(root, f), self.input_dir)
                        status = self.is_annotated(rel_path)
                        images.append((rel_path, status))
            
            # Sort: not_annotated first, then predicted, then annotated, then by name
            status_order = {"not_annotated": 0, "predicted": 1, "annotated": 2}
            images.sort(key=lambda x: (status_order[x[1]], x[0]))
            
            for img, status in images:
                if status == "annotated":
                    display_status = "Annotated"
                elif status == "predicted":
                    display_status = "Predicted"
                else:
                    display_status = "Not Annotated"
                self.listbox.insert(tk.END, f"{img} - {display_status}")

    def is_annotated(self, rel_img_path):
        """Check annotation status of an image.
        
        Args:
            rel_img_path: Relative path to image (e.g., "11/0001.png")
            
        Returns:
            "annotated" if manual annotation exists
            "predicted" if only predicted annotation exists
            "not_annotated" otherwise
        """
        base = os.path.splitext(rel_img_path)[0]
        manual_path = os.path.join(self.output_dir, base + ".txt")
        augmented_path = os.path.join(self.output_dir, base + "a.txt")
        
        if os.path.exists(manual_path):
            return "annotated"
        elif os.path.exists(augmented_path):
            return "predicted"
        else:
            return "not_annotated"

    def on_image_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            item = self.listbox.get(selection[0])
            rel_img_path = item.split(" - ")[0]  # e.g., "11/0001.png"
            self.current_image_rel_path = rel_img_path
            self.current_image_path = os.path.join(self.input_dir, rel_img_path)
            
            # Extract folder name and set dice values
            folder_name = os.path.dirname(rel_img_path)  # e.g., "11"
            if folder_name and folder_name.isdigit():
                dice1 = folder_name[0]
                dice2 = folder_name[1] if len(folder_name) > 1 else folder_name[0]
                self.dice1_entry.delete(0, tk.END)
                self.dice2_entry.delete(0, tk.END)
                self.dice1_entry.insert(0, dice1)
                self.dice2_entry.insert(0, dice2)
            
            self.display_image(self.current_image_path)
            self.load_and_draw_annotations(rel_img_path)

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
        self.rect_counter = 0  # Reset counter for new annotation
        # Keep the dice values from the folder (don't reset them)
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
        self.load_and_draw_annotations(self.current_image_rel_path)
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
            self.current_rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline='red')

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
                try:
                    # Alternate between dice1 and dice2 for each rectangle
                    if self.rect_counter % 2 == 0:
                        # Even rectangles (0, 2, 4...) use dice1
                        pips = int(self.dice1_entry.get())
                    else:
                        # Odd rectangles (1, 3, 5...) use dice2
                        pips = int(self.dice2_entry.get())
                    
                    if 1 <= pips <= 6:
                        self.annotations.append((x, y, w, h, pips))
                        self.rect_counter += 1
                        self.draw_annotations()
                        self.canvas.update_idletasks()
                    else:
                        messagebox.showerror("Error", "Each dice value must be between 1 and 6")
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numbers")
            if self.current_rect:
                self.canvas.delete(self.current_rect)
                self.current_rect = None

    def load_and_draw_annotations(self, rel_img_path):
        """Load annotations for an image. rel_img_path can be relative with folders (e.g., "11/0001.png")"""
        base = os.path.splitext(rel_img_path)[0]
        manual_path = os.path.join(self.output_dir, base + ".txt")
        augmented_path = os.path.join(self.output_dir, base + "a.txt")
        
        # Prioritize manual annotations over predicted
        if os.path.exists(manual_path):
            label_path = manual_path
            self.is_predicted = False
        elif os.path.exists(augmented_path):
            label_path = augmented_path
            self.is_predicted = True
        else:
            label_path = None
            self.is_predicted = False
        
        # Store the label path for later use
        self.current_label_path = label_path
        
        # Enable/disable Accept button based on predicted status
        self.btn_accept.config(state=tk.NORMAL if self.is_predicted else tk.DISABLED)
        
        if label_path:
            with open(label_path, 'r') as f:
                content = f.read()
                self.annotations = []
                for line in content.strip().split('\n'):
                    if line:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            x, y, w, h, pips = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                            self.annotations.append((x, y, w, h, pips))
            # Display file contents in text editor
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, content)
            self.draw_annotations()
        else:
            self.annotations = []
            # Clear text editor if no file
            self.text_editor.delete(1.0, tk.END)

    def draw_annotations(self):
        self.canvas.delete("annotation")
        self.canvas.update_idletasks()
        for x, y, w, h, pips in self.annotations:
            self.canvas.create_rectangle(x, y, x+w, y+h, outline='blue', tags="annotation")
            self.canvas.create_text(x + w//2, y - 5, text=str(pips), fill='red', tags="annotation", font=("Arial", 24, "bold"))
        self.canvas.update_idletasks()

    def save_annotation(self):
        if not self.annotations:
            messagebox.showerror("Error", "No annotation to save")
            return
        if not self.current_image_path:
            messagebox.showerror("Error", "No image selected")
            return
        
        # Get relative path from input_dir (e.g., "11/0001.png")
        rel_img_path = os.path.relpath(self.current_image_path, self.input_dir)
        base = os.path.splitext(rel_img_path)[0]
        
        # Create target subfolder if needed (e.g., "targets/11")
        label_dir = os.path.dirname(os.path.join(self.output_dir, base))
        os.makedirs(label_dir, exist_ok=True)
        
        # Save labels as-is (keep individual values from alternating mode)
        label_path = os.path.join(self.output_dir, base + ".txt")
        with open(label_path, 'w') as f:
            for x, y, w, h, pips in self.annotations:
                f.write(f"{x} {y} {w} {h} {pips}\n")
        self.load_images()  # Refresh list

    def accept_prediction(self):
        """Accept a predicted annotation by renaming XXXXa.txt to XXXX.txt"""
        if not self.is_predicted:
            messagebox.showerror("Error", "No predicted annotation to accept")
            return
        if not self.current_image_rel_path:
            messagebox.showerror("Error", "No image selected")
            return
        
        base = os.path.splitext(self.current_image_rel_path)[0]
        augmented_path = os.path.join(self.output_dir, base + "a.txt")
        manual_path = os.path.join(self.output_dir, base + ".txt")
        
        if os.path.exists(augmented_path):
            # Rename predicted annotation to manual annotation
            os.rename(augmented_path, manual_path)
            self.is_predicted = False
            self.btn_accept.config(state=tk.DISABLED)
            self.load_images()  # Refresh list
        else:
            messagebox.showerror("Error", "Predicted annotation file not found")

    def save_text_file(self):
        """Save the contents of the text editor to the current annotation file"""
        if not self.current_label_path:
            messagebox.showerror("Error", "No annotation file loaded")
            return
        
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            with open(self.current_label_path, 'w') as f:
                f.write(content)
                if content:
                    f.write('\n')
            # Reload annotations from file and refresh the view
            self.load_and_draw_annotations(self.current_image_rel_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiceAnnotator(root)
    root.mainloop()