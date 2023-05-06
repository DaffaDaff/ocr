import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from paddleocr import PaddleOCR
import cv2
import re


class OCRApp:
    def __init__(self, master):
        self.master = master
        master.title("OCR App")

        self.ocr_loaded_object = PaddleOCR()

        self.file_path = ""
        self.text = ""

        # create label for displaying selected file path
        self.path_label = tk.Label(master, text="No file selected")
        self.path_label.pack()

        # create button for selecting file
        self.file_button = tk.Button(master, text="Select File", command=self.select_file)
        self.file_button.pack()

        # create button for performing OCR
        self.ocr_button = tk.Button(master, text="Perform OCR", command=self.perform_ocr)
        self.ocr_button.pack()

        self.label = tk.Label(master, width=600, height=600)
        self.label.pack()

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        self.path_label.config(text=self.file_path)

    def perform_ocr(self):
        if self.file_path:
            img = cv2.imread(self.file_path)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            result = self.ocr_loaded_object.ocr(gray)[0]

            draw_box(result, img)
            
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            imgtk = ImageTk.PhotoImage(Image.fromarray(img).resize((600, 600)))
            self.label.image = imgtk
            self.label.config(image=imgtk)
        else:
            self.path_label.config(text="No file selected")

def draw_box(datas, img):
    hImg, wImg, _ = img.shape

    for data in datas:
        box = data[0]
        
        x0, y0 = int(box[0][0]), int(box[0][1])
        x2, y2 = int(box[2][0]), int(box[2][1])

        cv2.rectangle(img, (x0, y0), (x2, y2), (255, 0, 0), 1)
        cv2.putText(img, data[1][0], (x0 + 25, y0 + 25), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)

def post_process_box(box_text):

    # adds space before capital letters
    capital_corrected = re.sub(r'(\w)([A-Z])', r'\1 \2', str(box_text))
    
    # adds white-space after white-space
    punctuation_corrected = re.sub(r'([.:,!;?])([^\s])', r'\1 \2', str(capital_corrected))
    return punctuation_corrected

root = tk.Tk()
app = OCRApp(root)
root.mainloop()
