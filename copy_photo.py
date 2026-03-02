#!/usr/bin/env python3
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import threading

class PhotoCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Копирај слики од едно место на друго.")
        self.root.geometry("600x500")

        self.source_folder = tk.StringVar()
        self.numbers_file = tk.StringVar()
        self.dest_folder = tk.StringVar()
        
        default_dest = Path.home() / "Desktop" / "selected_photos"
        self.dest_folder.set(str(default_dest))
        
        self.create_widgets()
        
    def create_widgets(self):
        
        tk.Label(self.root, text="Source Folder (with photos):").pack(pady=(10,0))
        frame1 = tk.Frame(self.root)
        frame1.pack(fill=tk.X, padx=10)
        tk.Entry(frame1, textvariable=self.source_folder, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(frame1, text="Browse...", command=self.browse_source).pack(side=tk.RIGHT, padx=5)
        
        
        tk.Label(self.root, text="Text File with Numbers (one per line):").pack(pady=(10,0))
        frame2 = tk.Frame(self.root)
        frame2.pack(fill=tk.X, padx=10)
        tk.Entry(frame2, textvariable=self.numbers_file, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(frame2, text="Browse...", command=self.browse_numbers).pack(side=tk.RIGHT, padx=5)
        
        
        tk.Label(self.root, text="Destination Folder (leave as default for desktop):").pack(pady=(10,0))
        frame3 = tk.Frame(self.root)
        frame3.pack(fill=tk.X, padx=10)
        tk.Entry(frame3, textvariable=self.dest_folder, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(frame3, text="Browse...", command=self.browse_dest).pack(side=tk.RIGHT, padx=5)
        
        
        tk.Button(self.root, text="Copy Photos", command=self.start_copy, bg="lightblue", height=2).pack(pady=20)
        
        
        tk.Label(self.root, text="Log:").pack()
        self.log_area = scrolledtext.ScrolledText(self.root, height=12, state='normal')
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        
    def browse_source(self):
        folder = filedialog.askdirectory(title="Select folder with photos")
        if folder:
            self.source_folder.set(folder)
            
    def browse_numbers(self):
        filetypes = (("Text files", "*.txt"), ("All files", "*.*"))
        filename = filedialog.askopenfilename(title="Select numbers file", filetypes=filetypes)
        if filename:
            self.numbers_file.set(filename)
            
    def browse_dest(self):
        folder = filedialog.askdirectory(title="Select destination folder")
        if folder:
            self.dest_folder.set(folder)
    
    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.root.update()
    
    def start_copy(self):
        
        source = self.source_folder.get().strip()
        numfile = self.numbers_file.get().strip()
        dest = self.dest_folder.get().strip()
        
        if not source:
            messagebox.showerror("Error", "Please select a source folder.")
            return
        if not numfile:
            messagebox.showerror("Error", "Please select a numbers text file.")
            return
        if not dest:
            dest = str(Path.home() / "Desktop" / "selected_photos")
            self.dest_folder.set(dest)
        
        
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] == "Copy Photos":
                widget.config(state=tk.DISABLED)
        
        
        thread = threading.Thread(target=self.copy_photos, args=(source, numfile, dest))
        thread.daemon = True
        thread.start()
    
    def copy_photos(self, source, numfile, dest):
        try:
# 
            with open(numfile, 'r') as f:
                lines = f.readlines()
            numbers = [line.strip() for line in lines if line.strip()]
            
            if not numbers:
                self.log("No numbers found in the file.")
                return
            
            self.log(f"Loaded {len(numbers)} numbers: {', '.join(numbers[:10])}{'...' if len(numbers)>10 else ''}")
            
            Path(dest).mkdir(parents=True, exist_ok=True)
            
            copied = 0
            for filename in os.listdir(source):
                source_path = Path(source) / filename
                if source_path.is_file():
                    for num in numbers:
                        if num in filename:
                            dest_path = Path(dest) / filename
                            try:
                                shutil.copy2(source_path, dest_path)
                                self.log(f"Copied: {filename}")
                                copied += 1
                                break  
                            except Exception as e:
                                self.log(f"Error copying {filename}: {e}")
            
            self.log(f"\nDone! {copied} photo(s) copied to:\n{dest}")
            messagebox.showinfo("Complete", f"Copied {copied} photo(s) to:\n{dest}")
        except Exception as e:
            self.log(f"An error occurred: {e}")
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Button) and widget['text'] == "Copy Photos":
                    widget.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoCopyApp(root)
    root.mainloop()