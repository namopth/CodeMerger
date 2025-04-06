import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import platform  # To check OS for potential font differences

# --- Configuration (NERV-inspired Theme - Enhanced) ---
BG_COLOR = "#1a1a1a"  # Dark background
FG_COLOR = "#E0E0E0"  # Slightly brighter grey text
ACCENT_COLOR_RED = "#FF3B30"  # Brighter NERV Red (iOS style red)
ACCENT_COLOR_ORANGE = "#FF9500" # Brighter NERV Orange (iOS style orange)
TEXT_AREA_BG = "#000000" # Black text area
TEXT_AREA_FG = "#33FF33" # Brighter Green terminal-like text
PREVIEW_AREA_BG = "#101010" # Slightly lighter black for preview
PREVIEW_AREA_FG = "#C0C0C0" # Slightly brighter grey for preview text
BUTTON_BG = ACCENT_COLOR_RED
BUTTON_FG = "#FFFFFF" # White button text
BUTTON_ACTIVE_BG = "#D00000" # Darker red on click
ENTRY_BG = "#2c2c2e" # Darker grey for entry background (iOS dark style)
ENTRY_FG = FG_COLOR
SEPARATOR_COLOR = "#444444" # Dark grey for separators
BORDER_COLOR = ACCENT_COLOR_ORANGE # Use orange for focused borders

# Use slightly more modern/clean fonts if available
FONT_FAMILY_MAIN = "SF Pro Display" if platform.system() == "Darwin" else ("Segoe UI" if platform.system() == "Windows" else "Helvetica")
FONT_FAMILY_CODE = "SF Mono" if platform.system() == "Darwin" else ("Consolas" if platform.system() == "Windows" else "Monaco")
FONT_SIZE_NORMAL = 11 # Slightly larger base font
FONT_SIZE_LABEL = 12 # Larger for labels/headers
FONT_SIZE_CODE = 10

# --- Application Class ---
class CodeMergerApp:
    def __init__(self, root):
        """Initialize the application window and widgets."""
        self.root = root
        self.root.title("CodeMerger") # Renamed Program
        self.root.geometry("850x800") # Adjusted size
        self.root.configure(bg=BG_COLOR)
        # Set minimum size
        self.root.minsize(700, 600)

        self.found_files_list = [] # Store list of files found by preview/combine

        # --- Style Configuration ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # General widget styling
        self.style.configure('.',
                             background=BG_COLOR,
                             foreground=FG_COLOR,
                             font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL))
        self.style.configure('TFrame', background=BG_COLOR)

        # Label styling (bolder for section headers)
        self.style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL))
        self.style.configure('Header.TLabel', font=(FONT_FAMILY_MAIN, FONT_SIZE_LABEL, 'bold'), foreground=ACCENT_COLOR_ORANGE)

        # Entry styling
        self.style.configure('TEntry',
                             fieldbackground=ENTRY_BG,
                             foreground=ENTRY_FG,
                             insertcolor=FG_COLOR, # Cursor color
                             borderwidth=1,
                             relief=tk.FLAT) # Flat look initially
        self.style.map('TEntry',
                       bordercolor=[('focus', BORDER_COLOR)], # Orange border on focus
                       relief=[('focus', tk.SOLID)]) # Solid border on focus

        # Button styling
        self.style.configure('TButton',
                             background=BUTTON_BG,
                             foreground=BUTTON_FG,
                             font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL, 'bold'),
                             borderwidth=0, # Flat buttons
                             relief=tk.RAISED, # Gives slight depth effect
                             padding=(10, 5)) # More horizontal padding
        self.style.map('TButton',
                       background=[('active', BUTTON_ACTIVE_BG), ('disabled', '#555555'), ('!disabled', BUTTON_BG)],
                       foreground=[('disabled', '#999999'), ('!disabled', BUTTON_FG)])

        # Separator styling
        self.style.configure('TSeparator', background=SEPARATOR_COLOR)

        # --- Main Frame ---
        main_frame = ttk.Frame(root, padding="15 15 15 15") # Increased padding
        main_frame.pack(expand=True, fill=tk.BOTH)
        main_frame.columnconfigure(0, weight=1)
        # Adjusted row weights for better spacing with separators
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
        self.extension_entry = ttk.Entry(input_section_frame, textvariable=self.extension_var, width=15) # Wider entry
        self.extension_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Exclude Folders Input
        ttk.Label(input_section_frame, text="Exclude Folders:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(input_section_frame, text="(comma-separated)", font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL - 2)).grid(row=4, column=0, padx=5, pady=(0,5), sticky="nw") # Hint below label
        self.exclude_folders_var = tk.StringVar(value="venv, .git, __pycache__, node_modules, build, dist") # Added more defaults
        self.exclude_folders_entry = ttk.Entry(input_section_frame, textvariable=self.exclude_folders_var, width=60)
        self.exclude_folders_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew", rowspan=2) # Span 2 rows

        # --- Separator ---
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=1, column=0, sticky="ew", pady=10)

        # --- Action Frame ---
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, pady=5) # Centered by default grid behavior

        # Preview Button
        self.preview_button = ttk.Button(action_frame, text="Preview Files", command=self.preview_files)
        self.preview_button.pack(side=tk.LEFT, padx=10)

        # Combine Button
        self.combine_button = ttk.Button(action_frame, text="Combine Files", command=self.combine_files)
        self.combine_button.pack(side=tk.LEFT, padx=10)

        # --- Separator ---
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=3, column=0, sticky="ew", pady=10)

        # --- Preview Area ---
        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 5))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)

        ttk.Label(preview_frame, text="Files to be Included:", style='Header.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.preview_text = scrolledtext.ScrolledText(
            preview_frame, wrap=tk.NONE, width=80, height=8, # Slightly reduced height
            bg=PREVIEW_AREA_BG, fg=PREVIEW_AREA_FG,
            font=(FONT_FAMILY_CODE, FONT_SIZE_CODE),
            relief=tk.SOLID, bd=1, # Added border
            insertbackground=ACCENT_COLOR_ORANGE
        )
        self.preview_text.grid(row=1, column=0, sticky="nsew")
        self.preview_text.configure(state=tk.DISABLED)

        # --- Separator ---
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=5, column=0, sticky="ew", pady=10)

        # --- Output Area ---
        output_section_frame = ttk.Frame(main_frame)
        output_section_frame.grid(row=6, column=0, sticky="ew", pady=(0, 5))
        output_section_frame.columnconfigure(0, weight=1) # Allow label/buttons to space out

        ttk.Label(output_section_frame, text="Combined Output:", style='Header.TLabel').grid(row=0, column=0, sticky="w")

        # Frame for Save/Copy buttons
        output_actions_frame = ttk.Frame(output_section_frame)
        output_actions_frame.grid(row=0, column=1, sticky="e")

        # Copy Button (New)
        self.copy_button = ttk.Button(output_actions_frame, text="Copy Output", command=self.copy_output, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))

        # Save Button
        self.save_button = ttk.Button(output_actions_frame, text="Save Output", command=self.save_output, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=0)


        # Output Text Area Frame (allows adding border easily)
        output_text_frame = ttk.Frame(main_frame, relief=tk.SOLID, borderwidth=1, style='Output.TFrame')
        output_text_frame.grid(row=7, column=0, sticky="nsew", pady=5)
        output_text_frame.columnconfigure(0, weight=1)
        output_text_frame.rowconfigure(0, weight=1)
        self.style.configure('Output.TFrame', background=TEXT_AREA_BG) # Match text bg

        self.output_text = scrolledtext.ScrolledText(
            output_text_frame, wrap=tk.WORD, width=80, height=15,
            bg=TEXT_AREA_BG, fg=TEXT_AREA_FG,
            font=(FONT_FAMILY_CODE, FONT_SIZE_CODE),
            relief=tk.FLAT, bd=0, # No border on text widget itself
            insertbackground=ACCENT_COLOR_ORANGE
        )
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=1, pady=1) # Padding inside frame border
        self.output_text.configure(state=tk.DISABLED)

        # --- Status Bar ---
        status_bar = ttk.Label(root, text="Status: Idle", relief=tk.FLAT, anchor=tk.W, padding=(5, 3), foreground=ACCENT_COLOR_ORANGE, background="#000000", font=(FONT_FAMILY_CODE, FONT_SIZE_NORMAL - 1))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar(value="Status: Idle")
        status_bar.configure(textvariable=self.status_var) # Link variable after creation

    # --- Methods (browse_folder, get_excluded_folders, find_files, preview_files are mostly unchanged) ---

    def browse_folder(self):
        """Open a dialog to select a directory."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(folder_selected)
            self.clear_results()
            self.status_var.set(f"Status: Directory selected. Ready for Preview or Combine.")

    def clear_results(self):
        """Clears the preview and output areas and resets buttons."""
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.configure(state=tk.DISABLED)

        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.configure(state=tk.DISABLED)

        # Disable Save and Copy buttons
        self.save_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED) # Disable copy button too
        self.found_files_list = []
        # Don't reset status here, let the calling function set it

    def get_excluded_folders(self):
        """Parses the excluded folders string into a set."""
        exclude_str = self.exclude_folders_var.get().strip()
        if not exclude_str:
            return set()
        return {folder.strip() for folder in exclude_str.split(',') if folder.strip()}

    def find_files(self):
        """
        Finds files matching the extension in the target directory, respecting exclusions.
        Returns a list of full file paths or None if validation fails.
        """
        folder_path = self.folder_path_var.get()
        extension = self.extension_var.get().strip()

        # --- Input Validation ---
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Error", "Please select a valid target directory.")
            self.status_var.set("Status: Error - Invalid directory")
            return None
        if not extension or not extension.startswith('.'):
            messagebox.showerror("Error", "Please enter a valid file extension starting with '.' (e.g., .py).")
            self.status_var.set("Status: Error - Invalid extension format")
            return None

        excluded_folders = self.get_excluded_folders()
        found_files = []
        search_status = f"Status: Searching for '{extension}' files..."
        self.status_var.set(search_status)
        self.root.update_idletasks()

        try:
            # --- File Traversal and Filtering ---
            for root_dir, dirs, files in os.walk(folder_path, topdown=True):
                # Filter directories to exclude
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in excluded_folders]

                # Process files in allowed directories
                for file in files:
                    if file.endswith(extension):
                        try:
                            file_path = os.path.join(root_dir, file)
                            # Basic check to ensure it's not pointing outside the root somehow (security)
                            if os.path.commonpath([folder_path]) == os.path.commonpath([folder_path, file_path]):
                                found_files.append(file_path)
                        except Exception:
                            # Ignore files causing path errors, log if needed
                            print(f"Warning: Skipping file due to path issue: {os.path.join(root_dir, file)}")


            return found_files

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during file search:\n{str(e)}")
            self.status_var.set(f"Status: Error - File search failed: {str(e)}")
            return None

    def preview_files(self):
        """Finds files based on current settings and displays them in the preview area."""
        self.clear_results() # Clear previous results first
        folder_path = self.folder_path_var.get()
        if not folder_path: # Basic check, find_files does more thorough validation
             messagebox.showerror("Error", "Please select a target directory first.")
             self.status_var.set("Status: Select a directory.")
             return

        self.found_files_list = self.find_files()

        if self.found_files_list is None: # Error occurred during find_files
             # Status already set by find_files
             return

        # --- Update Preview Text Area ---
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete('1.0', tk.END)
        if not self.found_files_list:
            self.preview_text.insert('1.0', "No matching files found with current settings.")
            self.status_var.set("Status: Preview complete. No matching files found.")
        else:
            try:
                relative_paths = [os.path.relpath(f, folder_path) for f in self.found_files_list]
                self.preview_text.insert('1.0', "\n".join(relative_paths))
                self.status_var.set(f"Status: Preview complete. Found {len(self.found_files_list)} file(s). Ready to combine.")
            except ValueError as e:
                 # Handle cases where relpath fails (e.g., different drives on Windows)
                 messagebox.showerror("Error", f"Could not determine relative paths:\n{e}\nDisplaying full paths instead.")
                 self.preview_text.insert('1.0', "\n".join(self.found_files_list)) # Fallback to full paths
                 self.status_var.set(f"Status: Preview complete (full paths). Found {len(self.found_files_list)} file(s).")

        self.preview_text.configure(state=tk.DISABLED)
        # Keep Save/Copy disabled after only previewing
        self.save_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)


    def combine_files(self):
        """Combines the content of files found by find_files."""
        self.clear_results() # Clear previous output first
        folder_path = self.folder_path_var.get()
        self.found_files_list = self.find_files() # Run search again

        if self.found_files_list is None or not folder_path:
            self.status_var.set("Status: Combine failed. Check settings.")
            return
        if not self.found_files_list:
             self.status_var.set(f"Status: No matching files found to combine.")
             messagebox.showinfo("Info", f"No files found with the current settings to combine.")
             # Update preview area to show "No files" message
             self.preview_text.configure(state=tk.NORMAL)
             self.preview_text.delete('1.0', tk.END)
             self.preview_text.insert('1.0', "No matching files found.")
             self.preview_text.configure(state=tk.DISABLED)
             return

        self.status_var.set(f"Status: Combining {len(self.found_files_list)} file(s)...")
        self.root.update_idletasks()

        combined_content = []
        files_processed_count = 0
        errors_encountered = 0

        try:
            # --- Read and Combine File Content ---
            for file_path in self.found_files_list:
                try:
                    relative_path = os.path.relpath(file_path, folder_path)
                except ValueError:
                    relative_path = file_path # Fallback to full path if relpath fails

                self.status_var.set(f"Status: Processing {relative_path}...")
                self.root.update_idletasks()

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    combined_content.append(f"--- File: {relative_path} ---")
                    combined_content.append(content.strip()) # Remove leading/trailing whitespace from content
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

            # --- Update Preview Area (Consistency) ---
            self.preview_text.configure(state=tk.NORMAL)
            self.preview_text.delete('1.0', tk.END)
            try:
                relative_paths = [os.path.relpath(f, folder_path) for f in self.found_files_list]
                self.preview_text.insert('1.0', "\n".join(relative_paths))
            except ValueError:
                 self.preview_text.insert('1.0', "\n".join(self.found_files_list)) # Fallback
            self.preview_text.configure(state=tk.DISABLED)

            # --- Update Button States and Status ---
            if files_processed_count > 0:
                self.save_button.config(state=tk.NORMAL)
                self.copy_button.config(state=tk.NORMAL) # Enable copy button
                status_msg = f"Status: Combined {files_processed_count} file(s)."
                if errors_encountered > 0:
                    status_msg += f" Encountered {errors_encountered} read error(s)."
                self.status_var.set(status_msg)
            else:
                self.save_button.config(state=tk.DISABLED)
                self.copy_button.config(state=tk.DISABLED)
                self.status_var.set(f"Status: Combine complete. No files were successfully processed (Errors: {errors_encountered}).")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during combining:\n{str(e)}")
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
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=initial_filename,
            title="Save Combined Code As"
        )

        if file_path:
            try:
                # No need to remove trailing newline now due to .strip() earlier
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content_to_save)
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
