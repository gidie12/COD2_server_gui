import os

from PIL import Image, ImageTk
import tkinter as tk
from PIL import Image, ImageTk

# Make it possible to show preview of map on hover
class CheckboxWithPreview(tk.Checkbutton):
    def __init__(self, master, text, image_path, var, **kw):
        super().__init__(master, **kw)
        self.master = master
        self.image_path = image_path
        self.config(variable=var, text=text)
        self.bind("<Enter>", self.show_preview)
        self.bind("<Leave>", self.hide_preview)

        self.preview_window = None


    def show_preview(self, event=None):
        self.preview_window = tk.Toplevel()
        self.preview_window.geometry("+{}+{}".format(event.x_root + 20, event.y_root + 20))
        self.preview_window.overrideredirect(True)
        self.preview_window.wm_attributes("-topmost", 1)

        # Load image using PIL
        pil_image = Image.open(self.image_path)

        # Resize image to fit within preview window
        max_width = 200
        max_height = 200
        width, height = pil_image.size
        if width > max_width or height > max_height:
            scale_factor = min(max_width / width, max_height / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            pil_image = pil_image.resize((new_width, new_height), Image.ANTIALIAS)

        # Convert PIL image to Tkinter-compatible format
        tk_image = ImageTk.PhotoImage(pil_image)

        preview_label = tk.Label(self.preview_window, image=tk_image)
        preview_label.image = tk_image
        preview_label.grid(row=0, column=1)

    def hide_preview(self, event=None):
        if self.preview_window is not None:
            self.preview_window.destroy()
            self.preview_window = None




# root = Tk()
#
# CheckboxWithPreview(root, "Checkbox 1", os.path.join(os.getcwd(), 'img/preview_images/villers_bocage.jpg'))
#
# root.mainloop()
