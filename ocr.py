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
        
        self.is_running = False

        self.vid = cv2.VideoCapture(0)

        width= master.winfo_screenwidth()
        height= master.winfo_screenheight()

        master.geometry("%dx%d" % (width, height))

        self.ocr_loaded_object = PaddleOCR(use_gpu=True)

        master.rowconfigure(0, minsize=height, weight=1)

        # Create frame button
        frm_buttons = tk.Frame(master, relief=tk.RAISED, bd=2)
        frm_buttons.grid(row=0, column=0, sticky="ns")

        ## Create button to Start OCR
        self.start_button = tk.Button(frm_buttons, text="Start", command=self.start)
        self.start_button.grid(row=0, column=0, sticky='ew', padx=10,pady=10)

        ## Create button to Stop OCR
        self.stop_button = tk.Button(frm_buttons, text="Stop", command=self.stop)
        self.stop_button.grid(row=1, column=0, sticky='ew')

        # Create image frame
        frm_image = tk.Frame(master, relief=tk.SUNKEN, bd=2)
        frm_image.grid(row=0, column=1, sticky="ns")
        frm_image.columnconfigure(0, minsize=800, weight=1)

        ## Create image label
        self.image_label = tk.Label(frm_image)
        self.image_label.grid(row=0, column=0, sticky='ns')
        
        # Create result frame
        frm_result = tk.Frame(master)
        frm_result.grid(row=0, column=2, sticky="ne")

        ## Create frame for OCR row
        ocr_frm = tk.Frame(frm_result, padx=5, pady=5)
        ocr_frm.grid(row=0, column=0, sticky='w')
        
        ocr_label = tk.Label(ocr_frm, text="OCR Result : ")
        ocr_label.grid(row=0, column=0, sticky='w')
        self.ocr_result = tk.Label(ocr_frm, relief=tk.SUNKEN)
        self.ocr_result.grid(row=0, column=1, sticky='w')

        ## Create frame for barcode row
        barcode_frm = tk.Frame(frm_result, padx=5, pady=5)
        barcode_frm.grid(row=1, column=0, sticky='w')
        
        barcode_label = tk.Label(barcode_frm, text="Barcode Result : ")
        barcode_label.grid(row=0, column=0, sticky='w')
        self.barcode_result = tk.Label(barcode_frm, relief=tk.SUNKEN)
        self.barcode_result.grid(row=0, column=1, sticky='w')

        ## Create frame for accuracy row
        acc_frm = tk.Frame(frm_result, padx=5, pady=15)
        acc_frm.grid(row=2, column=0, sticky='w')
        
        acc_label = tk.Label(acc_frm, text="Accuracy : ")
        acc_label.grid(row=0, column=0, sticky='w')
        self.acc_result = tk.Label(acc_frm, relief=tk.SUNKEN)
        self.acc_result.grid(row=0, column=1, sticky='w')

        ## Create frame for revision row
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

        barcode_rev_label = tk.Label(rev_frm, text="Barcode")
        barcode_rev_label.grid(row=0, column=0, columnspan=17)

        ocr_rev_label = tk.Label(rev_frm, text="OCR Revision")
        ocr_rev_label.grid(row=2, column=0, columnspan=17)

        ## Create submit button
        self.submit_button = tk.Button(frm_result, text="Submit Result")
        self.submit_button.grid(row=4, column=0, sticky='ew', padx=50, pady=100)

        master.after(1000, self.run)

    def run(self):
        if not self.is_running:
            self.master.after(0, self.run)
            return
        
        ret, frame = self.vid.read()

        # Set barcode result
        barcode = "Not Detected"
        # Set OCR Result
        ocr = "Not Detected"

        # Read Barcode
        detectedBarcodes = decode(frame)

        # Run OCR on image
        result = self.ocr_loaded_object.ocr(frame)[0]

        # Draw barcode on image
        draw_barcode(detectedBarcodes, frame)

        # Draw OCR result on image
        draw_ocr(result, frame)

        acc = 0.0
        for b in detectedBarcodes:
            bar = b.data.decode('utf-8')
            
            for c in result:
                cr = c[1][0]
                
                rat = SequenceMatcher(None, cr, bar).ratio()

                if rat > 0.7:
                    barcode = bar
                    ocr = cr
                    print(cr)
                    acc = rat
                    break
            else:
                continue
            break

        # Convert Image to RGB format
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert Array Image to PIL Image and resize
        image = Image.fromarray(img).resize(( int(800), int(len(img) * 800 / len(img[0])) ))

        # Convert PIL Image to PIL PhotoImage
        imgtk = ImageTk.PhotoImage(image)

        # Write and display image
        self.image_label.image = imgtk
        self.image_label.config(image=imgtk)

        self.master.update()

        # Write barcode Label            
        self.barcode_result.config(text=barcode)
        # Write OCR Label            
        self.ocr_result.config(text=ocr)

        # 
        if acc > 0.7:
            # Write accuracy label
            self.acc_result.config(text=str(acc * 100) + "%")

            j = 0
            for bar in self.barcode_result_list:
                if j >= len(barcode):
                    bar.config(text=' ')

                bar.config(text=barcode[j])
                j += 1

            for o in self.ocr_result_list:
                o.delete('0.end', 'end')
            
            opcodes = SequenceMatcher(None, ocr, barcode).get_opcodes()

            for op in opcodes:
                if op[0] == 'equal':
                    for i in range(op[3], op[4]):
                        if len(ocr) <= i or len(self.ocr_result_list) <= i:
                            break
                        
                        self.ocr_result_list[i].insert(tk.END, ocr[i])
                        self.ocr_result_list[i].config(bg='light green')
                
                elif op[0] == 'replace' or op[0] == 'delete':
                    for i in range(op[3], op[4]):
                        if len(ocr) <= i or len(self.ocr_result_list) <= i:
                            break

                        self.ocr_result_list[i].insert(tk.END, ocr[i] if len(ocr) > i else ' ')
                        self.ocr_result_list[i].config(bg='red')
                
                elif op[0] == 'insert':
                    for i in range(op[3], op[4]):
                        self.ocr_result_list[i].insert(tk.END, ocr[i] if len(ocr) > i else ' ')
                        self.ocr_result_list[i].config(bg='red')
            
            self.master.update()
            self.is_running = False
        
        self.master.after(0, self.run)

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

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
