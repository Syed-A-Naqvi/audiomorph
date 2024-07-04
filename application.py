import tkinter as tk
from tkinter import ttk

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Input/Output Interface")
        
        # Create input label and entry
        self.input_label = ttk.Label(root, text="Enter some text:")
        self.input_label.grid(column=0, row=0, padx=10, pady=10)
        
        self.input_entry = ttk.Entry(root, width=30)
        self.input_entry.grid(column=1, row=0, padx=10, pady=10)
        
        # Create submit button
        self.submit_button = ttk.Button(root, text="Submit", command=self.display_output)
        self.submit_button.grid(column=2, row=0, padx=10, pady=10)
        
        # Create output label
        self.output_label = ttk.Label(root, text="Output will be displayed here.")
        self.output_label.grid(column=0, row=1, columnspan=3, padx=10, pady=10)
        
    def display_output(self):
        input_text = self.input_entry.get()
        self.output_label.config(text=f"Output: {input_text}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
