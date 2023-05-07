import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from paddleocr import PaddleOCR
import cv2
from pyzbar.pyzbar import decode
from difflib import SequenceMatcher

class OCRApp:
    def __init__(self, master):
        self.master = master
        master.title("OCR App")

        self.ocr_loaded_object = PaddleOCR()

        self.file_path = ""
        self.text = ""

        master.rowconfigure(0, minsize=400, weight=1)
        #master.columnconfigure(1, minsize=400, weight=1)

        # Create frame button
        frm_buttons = tk.Frame(master, relief=tk.RAISED, bd=2)
        frm_buttons.grid(row=0, column=0, sticky="ns")

        # Create button for selecting file
        self.file_button = tk.Button(frm_buttons, text="Select File", command=self.select_file)
        self.file_button.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Create button for performing OCR
        self.ocr_button = tk.Button(frm_buttons, text="Submit", command=self.perform_ocr)
        self.ocr_button.grid(row=1, column=0, sticky='ew', padx=5)

        # Create image frame
        frm_image = tk.Frame(master, relief=tk.SUNKEN, bd=2)
        frm_image.grid(row=0, column=1, sticky="ns")

        self.image_label = tk.Label(frm_image)
        self.image_label.grid(row=0, column=1, sticky='nsew')

        # Create result frame
        frm_result = tk.Frame(master)
        frm_result.grid(row=0, column=2, sticky="ns")

        # Create frame for OCR row
        ocr_frm = tk.Frame(frm_result, padx=5, pady=5)
        ocr_frm.grid(row=0, column=0, sticky='w')
        
        ocr_label = tk.Label(ocr_frm, text="OCR Result : ")
        ocr_label.grid(row=0, column=0, sticky='w')
        self.ocr_result = tk.Label(ocr_frm, relief=tk.SUNKEN)
        self.ocr_result.grid(row=0, column=1, sticky='w')

        # Create frame for barcode row
        barcode_frm = tk.Frame(frm_result, padx=5, pady=5)
        barcode_frm.grid(row=1, column=0, sticky='w')
        
        barcode_label = tk.Label(barcode_frm, text="Barcode Result : ")
        barcode_label.grid(row=0, column=0, sticky='w')
        self.barcode_result = tk.Label(barcode_frm, relief=tk.SUNKEN)
        self.barcode_result.grid(row=0, column=1, sticky='w')

        # Create frame for accuracy row
        acc_frm = tk.Frame(frm_result, padx=5, pady=15)
        acc_frm.grid(row=2, column=0, sticky='w')
        
        acc_label = tk.Label(acc_frm, text="Accuracy : ")
        acc_label.grid(row=0, column=0, sticky='w')
        self.acc_result = tk.Label(acc_frm, relief=tk.SUNKEN)
        self.acc_result.grid(row=0, column=1, sticky='w')

        # Create frame for accuracy row
        rev_frm = tk.Frame(frm_result, padx=5, pady=50)
        rev_frm.grid(row=3, column=0, sticky='w')
        
        self.barcode_result_list = []
        self.ocr_result_list = []

        for w in range(17):
            label = tk.Label(rev_frm, relief=tk.SUNKEN, width=2, height=1)
            label.grid(row=1, column=w)
            self.barcode_result_list.append(label)

            entry = tk.Text(rev_frm, width=2, height=1, )
            entry.grid(row=3, column=w)
            self.ocr_result_list.append(entry)



        # Create submit button
        self.submit_button = tk.Button(frm_result, text="Submit Result")
        self.submit_button.grid(row=4, column=0, sticky='ew', padx=50, pady=100)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])

    def perform_ocr(self):
        if self.file_path:
            # Read image from file path
            img = cv2.imread(self.file_path)

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Run OCR on image
            result = self.ocr_loaded_object.ocr(gray)[0]

            # Draw OCR result on image
            draw_ocr(result, img)

            # Set OCR Result
            ocr = "Not Detected"

            if result:
                ocr = result[0][1][0]

                i = 0
                for o in self.ocr_result_list:
                    o.insert(tk.END, ocr[i])
                    o.config(bg='light green')
                    i += 1

            # Write OCR Label            
            self.ocr_result.config(text=result[0][1][0])

            # Read Barcode
            detectedBarcodes = decode(img)

            # Draw barcode on image
            draw_barcode(detectedBarcodes, img)

            # Set barcode result
            barcode = "Not Detected"

            if detectedBarcodes:
                barcode = detectedBarcodes[0].data.decode('utf-8')

                i = 0
                for bar in self.barcode_result_list:
                    bar.config(text=barcode[i])
                    i += 1

            # Write barcode Label            
            self.barcode_result.config(text=barcode)

            # 
            if ocr != "Not Detected" and barcode != "Not Detected":
                # Calculate string math ratio
                acc = SequenceMatcher(None, ocr, barcode).ratio()

                # Write accuracy label
                self.acc_result.config(text=str(acc * 100) + "%")

            # Convert Image to RGB format
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Convert Array Image to PIL Image and resize
            image = Image.fromarray(img).resize(( int(len(img[0])/2), int(len(img)/2) ))

            # Convert PIL Image to PIL PhotoImage
            imgtk = ImageTk.PhotoImage(image)

            # Write and displat image
            self.image_label.image = imgtk
            self.image_label.config(image=imgtk)

        else:
            pass

def draw_ocr(datas, img):
    for data in datas:
        box = data[0]
        
        x0, y0 = int(box[0][0]), int(box[0][1])
        x2, y2 = int(box[2][0]), int(box[2][1])

        cv2.rectangle(img, (x0, y0), (x2, y2), (255, 0, 0), 1)
        cv2.putText(img, data[1][0], (x0, y0 + 25), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)

def draw_barcode(datas, img):
    for data in datas:
        left, top, w, h = data.rect

        cv2.rectangle(img, (left, top), (left + w, top + h), (0, 255, 0), 2)
        cv2.putText(img, data.data.decode('utf-8'), (left, top + 20), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 0, 255), 2)

root = tk.Tk()
app = OCRApp(root)
root.mainloop()
