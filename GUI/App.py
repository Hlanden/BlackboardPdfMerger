import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from pathlib import Path
import PDF_downloader as pdf
import threading
import browser_cookie3


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('Blackboard to PDF')

        self.master.bind("<Return>", lambda x: self.start_pdf_thread())
        self.pdfThread = None
        self.create_widgets()


    def create_widgets(self):
        self.labelHowToHeader = tk.Label(text='How to use the app:', font=('', 12, 'bold'))
        self.labelHowTo = tk.Label(text='\t1. Log into Blackboard with Firefox\n'
                                        '\t2. Find the folder containg the PDFs you want to combine\n'
                                        '\t3. Select the output-fodler where the combined PDF will be saved\n'
                                        '\t4. Select the name of the output-pdf\n'
                                        '\t5. Generate combined PDF', justify=tk.LEFT)
        self.stringVarBrowser = tk.StringVar()
        self.labelBrowser = tk.Label(self.master, text='Select browser:')
        self.rbFirefox = tk.Radiobutton(self.master, text='Firefox', variable=self.stringVarBrowser, value=0)
        self.rbChrome = tk.Radiobutton(self.master, text='Chrome', variable=self.stringVarBrowser, value=1)
        self.stringVarBrowser.set(0)

        self.labelBdLink = tk.Label(self.master, text='Link to Blackboard-folder:')
        self.entryBbLink = tk.Entry(self.master, width=50)

        self.stringVarOutputFolder = tk.StringVar()
        self.labelOutputFolder = tk.Label(self.master, text='Select output-folder:')
        self.entryOutputFolder = tk.Entry(self.master, textvariable=self.stringVarOutputFolder)
        self.buttonBrowseRemFolder = tk.Button(self.master, text='Browse...',
                                               command=lambda: self.browse_output_folder(self.stringVarOutputFolder))

        self.labelOutputName = tk.Label(self.master, text='Select name for the the merged PDF')
        self.entryOutputName = tk.Entry(self.master)

        self.buttonGeneratePdf = tk.Button(self.master, text='Generate Combined PDF', font=('', 12, 'bold'),
                                           command=self.start_pdf_thread, fg='Green')

        """-----------------------------------------GRID-----------------------------------------------------------"""
        self.labelHowToHeader.grid(row=1, column=1)
        self.labelHowTo.grid(row=2, column=1, pady=10)

        #self.labelBrowser.grid(row=3, column=1)
        #self.rbFirefox.grid(row=4, column=1,sticky='W')
        #self.rbChrome.grid(row=4, column=1, sticky='E')

        self.labelBdLink.grid(row=5, column=1, pady=10)
        self.entryBbLink.grid(row=6, column=1)

        self.labelOutputFolder.grid(row=7, column=1)
        self.entryOutputFolder.grid(row=8, column=1, sticky='W')
        self.buttonBrowseRemFolder.grid(row=8, column=1, sticky='E')

        self.labelOutputName.grid(row=9, column=1, pady=10)
        self.entryOutputName.grid(row=10, column=1)

        self.buttonGeneratePdf.grid(row=15, column=1, pady=10)

    def browse_output_folder(self, stringVar):
        foldername = str(Path(filedialog.askdirectory()))
        stringVar.set(foldername)

    def start_pdf_thread(self):
        if self.pdfThread is None or not self.pdfThread.is_alive():
            self.pdfThread = threading.Thread(target=self.generate_pdf, args=(),
                                              daemon=True)
            self.pdfThread.start()
        else:
            messagebox.showinfo('Merging operation still processing',
                                'Please wait until the current merging process is done!')


    def generate_pdf(self):
        bbLink = self.entryBbLink.get()
        outputFolder = self.entryOutputFolder.get()
        outputName = self.entryOutputName.get()
        browser = self.stringVarBrowser.get()

        if not bbLink:
            messagebox.showerror('No Blackboard link provided', 'Please enter Blackboard link')
            return
        if not outputFolder:
            messagebox.showerror('No output folder selected', 'Please select output-folder')
            return
        if not outputName:
            messagebox.showerror('No output name provided', 'Please enter output name')
            return

        if browser == '0':
            cookiejar = browser_cookie3.firefox(domain_name='ntnu.blackboard.com')
        elif browser == '1':
            cookiejar = browser_cookie3.chrome(domain_name='ntnu.blackboard.com')
        try:
            if pdf.generate_pdf(bbLink, outputFolder, outputName, cookiejar):
                messagebox.showinfo('Success', 'Successfully created PDF!')
            else:
                messagebox.showerror('Did not find any pdf-links', 'Error occured. Magit statke sure you are logged into BB\n'
                                                                   'in Firefox.')
        except Exception as e:
            messagebox.showerror('Exception', 'Exception occured:\n {}'.format(e))
            raise e




if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    app.mainloop()