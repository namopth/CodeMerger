import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import platform

# --- Configuration (NERV-inspired Theme - Enhanced) ---
BG_COLOR = "#1a1a1a"
FG_COLOR = "#E0E0E0"
ACCENT_COLOR_RED = "#FF3B30"
ACCENT_COLOR_ORANGE = "#FF9500"
TEXT_AREA_BG = "#000000"
TEXT_AREA_FG = "#33FF33"
# PREVIEW_AREA_BG = "#101010" # Canvas background will be BG_COLOR
CHECKBOX_FRAME_BG = "#1f1f1f" # Slightly different bg for the frame inside canvas
PREVIEW_AREA_FG = "#C0C0C0" # Color for checkbox text
BUTTON_BG = ACCENT_COLOR_RED
BUTTON_FG = "#FFFFFF"
BUTTON_ACTIVE_BG = "#D00000"
ENTRY_BG = "#2c2c2e"
ENTRY_FG = FG_COLOR
SEPARATOR_COLOR = "#444444"
BORDER_COLOR = ACCENT_COLOR_ORANGE
CHECKBOX_SELECT_COLOR = ACCENT_COLOR_ORANGE # Color for the checkmark itself

FONT_FAMILY_MAIN = "SF Pro Display" if platform.system() == "Darwin" else ("Segoe UI" if platform.system() == "Windows" else "Helvetica")
FONT_FAMILY_CODE = "SF Mono" if platform.system() == "Darwin" else ("Consolas" if platform.system() == "Windows" else "Monaco")
FONT_SIZE_NORMAL = 11
FONT_SIZE_LABEL = 12
FONT_SIZE_CODE = 10
FONT_SIZE_CHECKBOX = 10 # Font size for checkbox labels

# --- Application Class ---
class CodeMergerApp:
    def __init__(self, root):
        """Initialize the application window and widgets."""
        self.root = root
        self.root.title("CodeMerger")
        self.root.geometry("850x800")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(700, 600)

        # Store the state of each file checkbox {full_path: BooleanVar}
        self.file_checkbox_vars = {}
        # Store the actual full paths found by the last preview
        self.last_previewed_files = []

        # --- Style Configuration ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # General widget styling
        self.style.configure('.', background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL))
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('Checkbox.TFrame', background=CHECKBOX_FRAME_BG) # Style for frame inside canvas

        # Label styling
        self.style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL))
        self.style.configure('Header.TLabel', font=(FONT_FAMILY_MAIN, FONT_SIZE_LABEL, 'bold'), foreground=ACCENT_COLOR_ORANGE)
        self.style.configure('Checkbox.TLabel', background=CHECKBOX_FRAME_BG, foreground=PREVIEW_AREA_FG, font=(FONT_FAMILY_CODE, FONT_SIZE_CHECKBOX))

        # Entry styling
        self.style.configure('TEntry', fieldbackground=ENTRY_BG, foreground=ENTRY_FG, insertcolor=FG_COLOR, borderwidth=1, relief=tk.FLAT)
        self.style.map('TEntry', bordercolor=[('focus', BORDER_COLOR)], relief=[('focus', tk.SOLID)])

        # Button styling
        self.style.configure('TButton', background=BUTTON_BG, foreground=BUTTON_FG, font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL, 'bold'), borderwidth=0, relief=tk.RAISED, padding=(10, 5))
        self.style.map('TButton', background=[('active', BUTTON_ACTIVE_BG), ('disabled', '#555555'), ('!disabled', BUTTON_BG)], foreground=[('disabled', '#999999'), ('!disabled', BUTTON_FG)])

        # Separator styling
        self.style.configure('TSeparator', background=SEPARATOR_COLOR)

        # Checkbox styling (configure Checkbutton itself)
        self.style.configure('TCheckbutton',
                             background=CHECKBOX_FRAME_BG, # Background of the checkbox area
                             foreground=PREVIEW_AREA_FG,    # Text color
                             font=(FONT_FAMILY_CODE, FONT_SIZE_CHECKBOX),
                             indicatorcolor=BG_COLOR, # Border of the box
                             selectcolor=CHECKBOX_SELECT_COLOR # Color of the checkmark when selected
                             )
        self.style.map('TCheckbutton',
                       indicatorcolor=[('selected', BG_COLOR), ('!selected', BG_COLOR)], # Keep box border consistent
                       selectcolor=[('selected', CHECKBOX_SELECT_COLOR), ('!selected', CHECKBOX_FRAME_BG)], # Checkmark color / box fill color when not selected
                       foreground=[('disabled', '#777777'), ('active', FG_COLOR)] # Text color states
                       )
        # --- Main Frame ---
        main_frame = ttk.Frame(root, padding="15 15 15 15")
        main_frame.pack(expand=True, fill=tk.BOTH)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1) # Preview area row
        main_frame.rowconfigure(7, weight=2) # Output area row

        # --- Input Section ---
        input_section_frame = ttk.Frame(main_frame)
        input_section_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        input_section_frame.columnconfigure(1, weight=1)
        ttk.Label(input_section_frame, text="Configuration", style='Header.TLabel').grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))
        # Folder Selection
        ttk.Label(input_section_frame, text="Target Directory:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.folder_path_var = tk.StringVar()
        self.folder_entry = ttk.Entry(input_section_frame, textvariable=self.folder_path_var, width=60)
        self.folder_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button = ttk.Button(input_section_frame, text="Browse...", command=self.browse_folder, width=10)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5)
        # Extension Input
        ttk.Label(input_section_frame, text="File Extension:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.extension_var = tk.StringVar(value=".py")
        self.extension_entry = ttk.Entry(input_section_frame, textvariable=self.extension_var, width=15)
        self.extension_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        # Exclude Folders Input
        ttk.Label(input_section_frame, text="Exclude Folders:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(input_section_frame, text="(comma-separated)", font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL - 2)).grid(row=4, column=0, padx=5, pady=(0,5), sticky="nw")
        self.exclude_folders_var = tk.StringVar(value="venv, .git, __pycache__, node_modules, build, dist")
        self.exclude_folders_entry = ttk.Entry(input_section_frame, textvariable=self.exclude_folders_var, width=60)
        self.exclude_folders_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew", rowspan=2)

        # --- Separator ---
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=1, column=0, sticky="ew", pady=10)

        # --- Action Frame ---
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, pady=5)
        self.preview_button = ttk.Button(action_frame, text="Preview Files", command=self.preview_files)
        self.preview_button.pack(side=tk.LEFT, padx=10)
        self.combine_button = ttk.Button(action_frame, text="Combine Files", command=self.combine_files)
        self.combine_button.pack(side=tk.LEFT, padx=10)

        # --- Separator ---
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=3, column=0, sticky="ew", pady=10)

        # --- Preview Area (Scrollable Checkbox List) ---
        preview_section_frame = ttk.Frame(main_frame)
        preview_section_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 5))
        preview_section_frame.columnconfigure(0, weight=1)
        preview_section_frame.rowconfigure(1, weight=1)

        ttk.Label(preview_section_frame, text="Files to be Included:", style='Header.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Create a Canvas and a Scrollbar
        self.preview_canvas = tk.Canvas(preview_section_frame, bg=BG_COLOR, highlightthickness=1, highlightbackground=SEPARATOR_COLOR) # Use canvas bg, add border
        self.preview_scrollbar = ttk.Scrollbar(preview_section_frame, orient="vertical", command=self.preview_canvas.yview)
        self.preview_canvas.configure(yscrollcommand=self.preview_scrollbar.set)

        self.preview_canvas.grid(row=1, column=0, sticky="nsew")
        self.preview_scrollbar.grid(row=1, column=1, sticky="ns")

        # Create a Frame INSIDE the Canvas
        self.checkbox_frame = ttk.Frame(self.preview_canvas, style='Checkbox.TFrame') # Use specific style
        self.canvas_frame_id = self.preview_canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")

        # Bind events for scrolling and resizing
        self.checkbox_frame.bind("<Configure>", self.on_frame_configure)
        self.preview_canvas.bind("<Configure>", self.on_canvas_configure)
        # Mouse wheel scrolling (platform specific)
        if platform.system() == "Windows":
            self.preview_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        elif platform.system() == "Darwin": # macOS
             self.preview_canvas.bind_all("<MouseWheel>", self.on_mousewheel) # Tkinter handles this similarly now
             self.preview_canvas.bind_all("<Button-4>", self.on_mousewheel) # Older binding might be needed
             self.preview_canvas.bind_all("<Button-5>", self.on_mousewheel)
        else: # Linux
            self.preview_canvas.bind("<Button-4>", self.on_mousewheel)
            self.preview_canvas.bind("<Button-5>", self.on_mousewheel)


        # --- Separator ---
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=5, column=0, sticky="ew", pady=10)

        # --- Output Area ---
        output_section_frame = ttk.Frame(main_frame)
        output_section_frame.grid(row=6, column=0, sticky="ew", pady=(0, 5))
        output_section_frame.columnconfigure(0, weight=1)
        ttk.Label(output_section_frame, text="Combined Output:", style='Header.TLabel').grid(row=0, column=0, sticky="w")
        output_actions_frame = ttk.Frame(output_section_frame)
        output_actions_frame.grid(row=0, column=1, sticky="e")
        self.copy_button = ttk.Button(output_actions_frame, text="Copy Output", command=self.copy_output, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))
        self.save_button = ttk.Button(output_actions_frame, text="Save Output", command=self.save_output, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=0)
        output_text_frame = ttk.Frame(main_frame, relief=tk.SOLID, borderwidth=1, style='Output.TFrame')
        output_text_frame.grid(row=7, column=0, sticky="nsew", pady=5)
        output_text_frame.columnconfigure(0, weight=1)
        output_text_frame.rowconfigure(0, weight=1)
        self.style.configure('Output.TFrame', background=TEXT_AREA_BG)
        self.output_text = scrolledtext.ScrolledText(
            output_text_frame, wrap=tk.WORD, width=80, height=15, bg=TEXT_AREA_BG, fg=TEXT_AREA_FG,
            font=(FONT_FAMILY_CODE, FONT_SIZE_CODE), relief=tk.FLAT, bd=0, insertbackground=ACCENT_COLOR_ORANGE
        )
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        self.output_text.configure(state=tk.DISABLED)

        # --- Status Bar ---
        status_bar = ttk.Label(root, text="Status: Idle", relief=tk.FLAT, anchor=tk.W, padding=(5, 3), foreground=ACCENT_COLOR_ORANGE, background="#000000", font=(FONT_FAMILY_CODE, FONT_SIZE_NORMAL - 1))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar(value="Status: Idle")
        status_bar.configure(textvariable=self.status_var)

    # --- Canvas/Frame/Scrolling Event Handlers ---
    def on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Set the inner frame width to the canvas width"""
        canvas_width = event.width
        self.preview_canvas.itemconfig(self.canvas_frame_id, width=canvas_width)

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if platform.system() == 'Darwin': # macOS specific delta
             delta = event.delta
        elif platform.system() == 'Windows':
             delta = -1 * int(event.delta / 120) # Windows delta is different
        else: # Linux Button-4 / Button-5
            if event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            else:
                delta = 0

        # Check if cursor is over the canvas before scrolling
        widget_under_cursor = self.root.winfo_containing(event.x_root, event.y_root)
        if widget_under_cursor == self.preview_canvas or widget_under_cursor.master == self.checkbox_frame:
             self.preview_canvas.yview_scroll(delta, "units")


    # --- Core Logic Methods ---

    def browse_folder(self):
        """Open a dialog to select a directory."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(folder_selected)
            self.clear_results()
            self.status_var.set(f"Status: Directory selected. Ready for Preview or Combine.")

    def clear_results(self):
        """Clears the preview and output areas and resets buttons and data."""
        # Clear checkboxes from the frame
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        self.file_checkbox_vars.clear() # Clear the stored variable states
        self.last_previewed_files = [] # Clear the list of files

        # Reset scroll region after clearing
        self.on_frame_configure()
        self.preview_canvas.yview_moveto(0) # Scroll back to top

        # Clear output text
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.configure(state=tk.DISABLED)

        # Disable Save and Copy buttons
        self.save_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        # Don't reset status here, let the calling function set it

    def get_excluded_folders(self):
        """Parses the excluded folders string into a set."""
        exclude_str = self.exclude_folders_var.get().strip()
        if not exclude_str: return set()
        return {folder.strip() for folder in exclude_str.split(',') if folder.strip()}

    def find_files(self):
        """Finds files, respecting exclusions. Returns list of full paths or None."""
        folder_path = self.folder_path_var.get()
        extension = self.extension_var.get().strip()
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Error", "Please select a valid target directory.")
            self.status_var.set("Status: Error - Invalid directory")
            return None
        if not extension or not extension.startswith('.'):
            messagebox.showerror("Error", "Please enter a valid file extension (e.g., .py).")
            self.status_var.set("Status: Error - Invalid extension format")
            return None

        excluded_folders = self.get_excluded_folders()
        found_files = []
        self.status_var.set(f"Status: Searching for '{extension}' files...")
        self.root.update_idletasks()
        try:
            for root_dir, dirs, files in os.walk(folder_path, topdown=True):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in excluded_folders]
                for file in files:
                    if file.endswith(extension):
                        try:
                            file_path = os.path.join(root_dir, file)
                            if os.path.commonpath([folder_path]) == os.path.commonpath([folder_path, file_path]):
                                found_files.append(file_path)
                        except Exception as e: print(f"Warning: Skipping {os.path.join(root_dir, file)} due to path issue: {e}")
            return found_files
        except Exception as e:
            messagebox.showerror("Error", f"Error during file search:\n{str(e)}")
            self.status_var.set(f"Status: Error - File search failed: {str(e)}")
            return None

    def preview_files(self):
        """Finds files and populates the checkbox list."""
        self.clear_results() # Clear previous results first
        folder_path = self.folder_path_var.get()
        if not folder_path:
             messagebox.showerror("Error", "Please select a target directory first.")
             self.status_var.set("Status: Select a directory.")
             return

        self.last_previewed_files = self.find_files() # Get the list of full paths

        if self.last_previewed_files is None: return # Error occurred

        if not self.last_previewed_files:
            # Display message inside the checkbox frame if no files found
            no_files_label = ttk.Label(self.checkbox_frame, text="No matching files found.", style='Checkbox.TLabel')
            no_files_label.pack(pady=10, padx=10)
            self.status_var.set("Status: Preview complete. No matching files found.")
        else:
            # --- Populate Checkbox List ---
            self.file_checkbox_vars.clear() # Clear previous vars
            try:
                for full_path in self.last_previewed_files:
                    var = tk.BooleanVar(value=True) # Default to checked
                    self.file_checkbox_vars[full_path] = var
                    relative_path = os.path.relpath(full_path, folder_path)
                    cb = ttk.Checkbutton(self.checkbox_frame, text=relative_path, variable=var, style='TCheckbutton')
                    cb.pack(anchor='w', padx=5, pady=2, fill='x') # Fill horizontally
                self.status_var.set(f"Status: Preview complete. Found {len(self.last_previewed_files)} file(s). Ready to combine.")
            except ValueError as e:
                 messagebox.showerror("Error", f"Could not determine relative paths:\n{e}\nCheckboxes will show full paths.")
                 self.status_var.set(f"Status: Preview complete (full paths). Found {len(self.last_previewed_files)} file(s).")
                 # Fallback to full paths in checkboxes if relpath fails
                 self.file_checkbox_vars.clear()
                 for full_path in self.last_previewed_files:
                     var = tk.BooleanVar(value=True)
                     self.file_checkbox_vars[full_path] = var
                     cb = ttk.Checkbutton(self.checkbox_frame, text=full_path, variable=var, style='TCheckbutton')
                     cb.pack(anchor='w', padx=5, pady=2, fill='x')

        # Update scroll region after adding widgets
        self.on_frame_configure()
        self.preview_canvas.yview_moveto(0) # Scroll to top

        # Keep Save/Copy disabled after only previewing
        self.save_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)


    def combine_files(self):
        """Combines the content of CHECKED files from the preview list."""
        folder_path = self.folder_path_var.get() # Needed for relpath fallback

        # --- Get list of files to combine based on checkbox state ---
        files_to_combine = [
            fp for fp, var in self.file_checkbox_vars.items() if var.get()
        ]

        # Clear only the output area, keep the preview checkboxes as they are
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.configure(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)


        if not self.file_checkbox_vars:
             self.status_var.set("Status: Please preview files before combining.")
             messagebox.showinfo("Info", "Run 'Preview Files' first to select files.")
             return
        if not files_to_combine:
             self.status_var.set(f"Status: No files selected to combine.")
             messagebox.showinfo("Info", f"No files are checked in the list above.")
             return

        self.status_var.set(f"Status: Combining {len(files_to_combine)} selected file(s)...")
        self.root.update_idletasks()

        combined_content = []
        files_processed_count = 0
        errors_encountered = 0

        try:
            # --- Read and Combine File Content ---
            for file_path in files_to_combine: # Iterate through the CHECKED files
                try:
                    relative_path = os.path.relpath(file_path, folder_path)
                except ValueError:
                    relative_path = file_path # Fallback

                self.status_var.set(f"Status: Processing {relative_path}...")
                self.root.update_idletasks()

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    combined_content.append(f"--- File: {relative_path} ---")
                    combined_content.append(content.strip())
                    combined_content.append(f"--- End File: {relative_path} ---\n")
                    files_processed_count += 1
                except Exception as e:
                    errors_encountered += 1
                    error_msg = f"--- Error reading file: {relative_path} ---\nError: {str(e)}\n--- End Error ---\n"
                    combined_content.append(error_msg)
                    print(f"Warning: Could not read file {file_path}: {e}")

            final_output = "\n".join(combined_content)

            # --- Update Output Text Area ---
            self.output_text.configure(state=tk.NORMAL)
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert('1.0', final_output)
            self.output_text.configure(state=tk.DISABLED)

            # --- Update Button States and Status ---
            if files_processed_count > 0:
                self.save_button.config(state=tk.NORMAL)
                self.copy_button.config(state=tk.NORMAL)
                status_msg = f"Status: Combined {files_processed_count} selected file(s)."
                if errors_encountered > 0: status_msg += f" Encountered {errors_encountered} read error(s)."
                self.status_var.set(status_msg)
            else:
                # This case means files were selected but all failed to read
                self.save_button.config(state=tk.DISABLED)
                self.copy_button.config(state=tk.DISABLED)
                self.status_var.set(f"Status: Combine complete. No selected files processed successfully (Errors: {errors_encountered}).")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error during combining:\n{str(e)}")
            self.status_var.set(f"Status: Error - Combining failed: {str(e)}")
            self.save_button.config(state=tk.DISABLED)
            self.copy_button.config(state=tk.DISABLED)


    def copy_output(self):
        """Copies the content of the output text area to the clipboard."""
        content = self.output_text.get('1.0', tk.END).strip()
        if content:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self.status_var.set("Status: Output copied to clipboard.")
            except tk.TclError:
                 messagebox.showwarning("Clipboard Error", "Could not access the clipboard.")
                 self.status_var.set("Status: Error - Failed to copy to clipboard.")
        else:
            self.status_var.set("Status: Nothing to copy.")


    def save_output(self):
        """Save the content of the output text area to a file."""
        content_to_save = self.output_text.get('1.0', tk.END).strip()
        if not content_to_save:
             messagebox.showwarning("Warning", "There is no output content to save.")
             self.status_var.set("Status: Nothing to save.")
             return

        initial_filename = f"codemerger_output_{self.extension_var.get().strip('.')}.txt"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=initial_filename, title="Save Combined Code As"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f: f.write(content_to_save)
                self.status_var.set(f"Status: Output saved successfully to {file_path}")
                messagebox.showinfo("Success", f"Output saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
                self.status_var.set(f"Status: Error - Failed to save file: {str(e)}")

# --- Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CodeMergerApp(root)
    root.mainloop()
