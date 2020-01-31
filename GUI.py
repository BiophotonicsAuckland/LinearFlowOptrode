import tkinter as tk
import tkinter.filedialog as tkFileDialog

class View:

    def __init__(self, root):
        # Creating GUI
        self.root = root
        self.root.title("Linear Flow Fluorescence")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.geometry("380x400+150+100")
        self.root.grid_columnconfigure(0, weight=1)

        # Setting variables
        self.directory = tk.StringVar(value="")
        self.filename = tk.StringVar(value="")      # Filename of output data
        self.is_suff = tk.IntVar(value=0)           # 0 or 1 depending on whether or not to add a suffix to filename
        self.int_time = tk.StringVar(value="50")    # Integration time of spectrometer (ms)
        self.rec_time = tk.StringVar(value="90")    # Recording duration of spectrometer (s)
        self.min_len = tk.StringVar(value="450")    # Minimum wavelength to record (nm)
        self.max_len = tk.StringVar(value="650")    # Maximum wavelength to record (nm)

        self.error_msg = tk.StringVar(value=" ")    # Variable that stores the error message displayed on GUI
        wait_var = tk.IntVar(value=0)          # Variable used to keep GUI waiting for user input during tests

        self.root.help_window = None

        small_entry = 6
        large_entry = 19

        # Title frame
        frame1 = tk.Frame(self.root)
        frame1.grid(row=0, column=0)

        title = tk.Label(frame1, text="LINEAR FLOW OPTRODE", font=("Times", 13))
        title.grid(row=0, column=1, padx=10, pady=10)

        # Parameter frame
        frame2 = tk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        frame2.grid(row=1, column=0, padx=8, pady=4, sticky=tk.W+tk.E)
        rowdir = 1
        rowfn = 2   # Filename row
        rowsu = 3   # Filename suffix row
        rowrd = 4   # Recording duration row
        rowit = 5   # Integration time row
        rowwr = 6   # Wavelength range row
  
        fnlbl = tk.Label(frame2, text="Directory", font=(None, 11))
        fnlbl.grid(row=rowdir, column=1, padx=6, pady=(6,0), sticky=tk.W)
        fntxt = tk.Entry(frame2, textvariable=self.directory, width=large_entry+8)
        fntxt.grid(row=rowdir, column=2, pady=(6,0), columnspan=3, sticky=tk.W)
        dir_browse = tk.Button(frame2, text="Browse",command=lambda: self.get_dir(self.directory))
        dir_browse.grid(row=rowdir,column=4, padx=6, pady=(6,0), sticky=tk.E)
        
        fnlbl = tk.Label(frame2, text="Filename", font=(None, 11))
        fnlbl.grid(row=rowfn, column=1, padx=6, pady=(6,0), sticky=tk.W)
        fntxt = tk.Entry(frame2, textvariable=self.filename, width=large_entry+8)
        fntxt.grid(row=rowfn, column=2, padx=6, pady=(6,0), columnspan=3)

        sulbl = tk.Label(frame2, text="Add Date Time Suffix", font=(None, 11))
        sulbl.grid(row=rowsu, column=1, padx=9, pady=6, sticky=tk.E)
        fntxt = tk.Checkbutton(frame2, variable=self.is_suff)
        fntxt.grid(row=rowsu, column=2, padx=0, pady=6, sticky=tk.W)

        rdlbl = tk.Label(frame2, text="Recording duration (s)", font=(None, 11))
        rdlbl.grid(row=rowrd, column=1, padx=6, pady=6, sticky=tk.E)
        rdtxt = tk.Entry(frame2, textvariable=self.rec_time, width=large_entry)
        rdtxt.grid(row=rowrd, column=2, padx=6, pady=6, columnspan=3)

        itlbl = tk.Label(frame2, text="Integration time (ms)", font=(None, 11))
        itlbl.grid(row=rowit, column=1, padx=6, pady=6, sticky=tk.E)
        ittxt = tk.Entry(frame2, textvariable=self.int_time, width=large_entry)
        ittxt.grid(row=rowit, column=2, padx=6, pady=6, columnspan=3)

        wrlbl = tk.Label(frame2, text="Wavelength range (nm)", font=(None, 11))
        wrlbl.grid(row=rowwr, column=1, padx=6, pady=6, sticky=tk.E)
        wrtxt = tk.Entry(frame2, textvariable=self.min_len, width=small_entry)
        wrtxt.grid(row=rowwr, column=2, padx=6, pady=6, sticky=tk.W)
        wrlbl = tk.Label(frame2, text="to", font=(None, 11))
        wrlbl.grid(row=rowwr, column=3, padx=0, pady=6)
        wrtxt = tk.Entry(frame2, textvariable=self.max_len, width=small_entry)
        wrtxt.grid(row=rowwr, column=4, padx=6, pady=6, sticky=tk.E)

        # tk.Frame for checkbox frames
        framech = tk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
    
        # Error message
        erlbl = tk.Message(framech, width=360, textvariable=self.error_msg, font=(None, 11))
        erlbl.grid(row=2, column=1, columnspan=3)

        # tk.Button frames
        frame6 = tk.Frame(self.root)
        frame6.grid(row=3, column=0)

        self.but_setup = tk.Button(frame6, text="Setup Test")
        self.but_setup.grid(row=1, column=1, padx=10, pady=10)
        self.but_start = tk.Button(frame6, text="Start Test", state=tk.DISABLED)
        self.but_start.grid(row=1, column=2, padx=10, pady=10)

        but_help = tk.Button(frame6, text="Help", command=self.help)
        but_help.grid(row=4, column=1, padx=10, pady=10)

    def help(self):
        '''
        Creates a help window if none exists.
        '''
        if self.root.help_window == None or self.root.help_window.winfo_exists() == 0:
            self.root.help_window = tk.Toplevel(self.root)
            self.root.help_window.geometry("260x350+450+150")
            self.root.help_window.wm_title("Help")

            w = 250

            tk.Message(self.root.help_window, width=w, font=(None, 13), text="Help:")																												.grid(row=1, column=1, sticky=tk.W)
            tk.Message(self.root.help_window, width=w, font=(None, 11), text="Press begin to setup test, then press start to begin data collection.")												.grid(row=2, column=1, sticky=tk.W)
            tk.Message(self.root.help_window, width=w, font=(None, 11), text="Press align to open live read of data to help calibrate setup.")														.grid(row=3, column=1, sticky=tk.W)
            tk.Message(self.root.help_window, width=w, font=(None, 11), text="After data collection is complete, press re-run to run test with same parameters, or change to change parameters.")	.grid(row=4, column=1, sticky=tk.W)
            tk.Message(self.root.help_window, width=w, font=(None, 11), text="Checking extension checkbox adds a time tag to end of filename.")														.grid(row=5, column=1, sticky=tk.W)
            tk.Message(self.root.help_window, width=w, font=(None, 11), text="Checking blit checkbox makes the alignment animations run more smoothly but means axis values will be incorrect.")	.grid(row=6, column=1, sticky=tk.W)

        else:
            self.root.help_window.focus_set()
            
    def toggle_ui(self, disable=True):
        '''
        Disables non-button UI. Functions recursively.
        '''
        
        for w in self.root.winfo_children():
            if w.winfo_class() == "TEntry" or w.winfo_class() == "tk.Checkbutton":
                if disable == True:
                    w.config(state=tk.DISABLED)
                else:
                    w.config(state=tk.NORMAL)
            else:
                self.disable_ui(disable)
                
    def get_dir(self, sv):
        """Takes a string var object, and opens a file select dialog, changes text entry to chosen file"""
        directory = tkFileDialog.askdirectory()
        #print(filename)
        if directory:
            sv.set(directory)