import csv
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox

TABLE_SIZE = 30  # Number of slots (boxes) in the open-addressing hash table

class Record:
    def __init__(self, phone_number="", username="", address="", deleted=False):
        self.phone_number = phone_number
        self.username = username
        self.address = address
        self.deleted = deleted

    def is_active(self):
        return self.username != "" and not self.deleted

    def __str__(self):
        return f"Username: {self.username}, Phone: {self.phone_number}, Address: {self.address}"

class HashTable:
    def __init__(self, load_samples=True):
        self.table = [Record() for _ in range(TABLE_SIZE)]
        self.count = 0
        if load_samples:
            self.load_sample_data()

    def hash_func(self, key):
        return sum(ord(c) for c in key) % TABLE_SIZE 
    def insert(self, record, by='username'):
        key = record.username if by == 'username' else record.phone_number
        idx = self.hash_func(key)
        probes = 1
        for i in range(TABLE_SIZE):
            pos = (idx + i) % TABLE_SIZE
            if not self.table[pos].is_active():
                self.table[pos] = record
                self.count += 1
                return probes
            probes += 1
        print("Insertion failed: Table full")
        return probes

    def search(self, key, by='username'):
        idx = self.hash_func(key)
        probes = 1
        for i in range(TABLE_SIZE):
            pos = (idx + i) % TABLE_SIZE
            entry = self.table[pos]
            if not entry.is_active() and not entry.deleted:
                return None, probes
            if entry.is_active():
                # username searches are case-insensitive for usability
                if by == 'username' and entry.username.lower() == key.lower():
                    return entry, probes
                if by == 'phone' and entry.phone_number == key:
                    return entry, probes
            probes += 1
        return None, probes

    def search_all(self, key, by='username'):
        """Return a list of all active records matching the key (username, phone or address).
        Username matching is case-insensitive; address searches perform case-insensitive substring match."""
        results = []
        if by == 'username':
            k = key.lower()
            for entry in self.table:
                if entry.is_active() and entry.username.lower() == k:
                    results.append(entry)
        elif by == 'phone':
            for entry in self.table:
                if entry.is_active() and entry.phone_number == key:
                    results.append(entry)
        elif by == 'address':
            k = key.lower()
            for entry in self.table:
                if entry.is_active() and k in entry.address.lower():
                    results.append(entry)
        return results

    def delete(self, key, by='username'):
        idx = self.hash_func(key)
        for i in range(TABLE_SIZE):
            pos = (idx + i) % TABLE_SIZE
            entry = self.table[pos]
            if not entry.is_active() and not entry.deleted:
                return False
            if entry.is_active():
                if (by == 'username' and entry.username == key) or (by == 'phone' and entry.phone_number == key):
                    self.table[pos] = Record(deleted=True)
                    self.count -= 1
                    return True
        return False

    def display(self):
        """Display the raw hash table: index, username, phone, address (empty only)."""
        print("Index\tUsername\tPhone Number\tAddress/Status")
        for idx, entry in enumerate(self.table):
            if entry.is_active():
                print(f"{idx}\t{entry.username}\t{entry.phone_number}\t{entry.address}")
            else:
                # treat deleted and empty equally: blank username and no marker in address
                print(f"{idx}\t\t-\t-")

    def save(self, filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            # write rows: username, phone, address
            for entry in self.table:
                if entry.is_active():
                    writer.writerow([entry.username, entry.phone_number, entry.address])

    def load(self, filename):
        self.table = [Record() for _ in range(TABLE_SIZE)]
        self.count = 0
        try:
            with open(filename, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    # accept 3+ columns: username, phone, address
                    if len(row) >= 3:
                        username = row[0]
                        phone = row[1]
                        address = row[2]
                        record = Record(phone, username, address)
                        self.insert(record, by='username')
        except FileNotFoundError:
            print("File not found.")

    def load_sample_data(self):
        # 15 sample records (kept small by request). Addresses are stored but not shown on main GUI until 'Load Samples' is pressed.
        samples = [
            ("0003093", "aya", "Room 101"),
            ("4550002", "ines", "Room 102"),
            ("9250003", "nicol", "Room 103"),
            ("2750004", "david", "Room 104"),
            ("5750005", "eve", "Room 105"),
            ("9250006", "frank", "Room 106"),
            ("8450007", "grace", "Room 107"),
            ("2950008", "heidi", "Room 108"),
            ("8850009", "ivan", "Room 109"),
            ("5550010", "judy", "Room 110"),
            ("5550011", "alice", "Room 111"),
            ("5550012", "anna", "Room 112"),
            ("5550013", "anem", "Room 113"),
            ("5550014", "boby", "Room 114"),
            ("5550015", "bob", "Room 115"),
        ]
        for phone, user, addr in samples:
            self.insert(Record(phone, user, addr), by='username')

class Directory:
    """A directory that keeps two hash tables synchronized: one hashed by username and one by phone number."""
    def __init__(self):
        # Do not preload sample records until explicitly requested
        self.by_username = HashTable(load_samples=False)
        self.by_phone = HashTable(load_samples=False)
        self.samples_loaded = False

    def load_samples(self):
        """Load the built-in sample dataset into the directory. Returns number of records loaded."""
        if self.samples_loaded:
            return sum(1 for e in self.by_username.table if e.is_active())
        self.by_username.load_sample_data()
        self.by_phone = HashTable(load_samples=False)
        for entry in self.by_username.table:
            if entry.is_active():
                self.by_phone.insert(entry, by='phone')
        self.samples_loaded = True
        return sum(1 for e in self.by_username.table if e.is_active())

    def is_full(self):
        return self.by_username.count >= TABLE_SIZE or self.by_phone.count >= TABLE_SIZE

    def insert(self, record, by='username'):
        if self.is_full():
            return None
        # Ensure properties exist for older records
        p_user = self.by_username.insert(record, by='username')
        p_phone = self.by_phone.insert(record, by='phone')
        return p_user, p_phone

    def search(self, key, by='username'):
        if by == 'username':
            return self.by_username.search(key, by='username')
        else:
            return self.by_phone.search(key, by='phone')

    def delete(self, key, by='username'):
        entry, probes = self.search(key, by=by)
        if not entry:
            return False
        self.by_username.delete(entry.username, by='username')
        self.by_phone.delete(entry.phone_number, by='phone')
        return True

    def delete_record(self, record):
        """Delete a specific record (identified by username & phone)."""
        ok1 = self.by_username.delete(record.username, by='username')
        ok2 = self.by_phone.delete(record.phone_number, by='phone')
        return ok1 or ok2

    def modify_record(self, record, new_username, new_phone, new_address):
        """Modify an existing record atomically. Returns (True, message) on success or (False, reason).
        This checks for duplicate username/phone and rolls back on failure."""
        # check duplicates for username (ignore current record)
        if new_username.lower() != record.username.lower():
            existing = self.by_username.search_all(new_username, by='username')
            if any(e.is_active() for e in existing):
                return False, 'Username already exists'
        # check duplicates for phone (ignore current record)
        if new_phone != record.phone_number:
            existing = self.by_phone.search_all(new_phone, by='phone')
            if any(e.is_active() for e in existing):
                return False, 'Phone number already exists'
        # perform delete then insert, but keep a backup to rollback if needed
        backup = Record(record.phone_number, record.username, record.address)
        self.delete_record(record)
        newrec = Record(new_phone, new_username, new_address)
        probes = self.insert(newrec, by='username')
        if probes is None:
            # rollback
            self.insert(backup, by='username')
            return False, 'Modification failed: table full'
        return True, 'Modified'

    def search_all(self, key, by='username'):
        if by == 'username':
            return self.by_username.search_all(key, by='username')
        elif by == 'phone':
            return self.by_phone.search_all(key, by='phone')
        elif by == 'address':
            # Addresses are stored with records in the username table
            return self.by_username.search_all(key, by='address')
        else:
            return []

    # GUI helper: search by address (case-insensitive substring search)


    def display(self):
        self.by_username.display()

    def save(self, filename):
        self.by_username.save(filename)

    def load(self, filename):
        self.by_username.load(filename)
        self.by_phone = HashTable(load_samples=False)
        for entry in self.by_username.table:
            if entry.is_active():
                self.by_phone.insert(entry, by='phone')


class DirectoryGUI:
    def __init__(self, master):
        self.master = master
        master.title("Phone Directory")
        self.dir = Directory()

        # Top input frame
        frm = tk.Frame(master)
        frm.pack(padx=8, pady=6, fill='x')

        tk.Label(frm, text="Username:").grid(row=0, column=0, sticky='w', padx=(0,4))
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(frm, textvariable=self.username_var)
        self.username_entry.grid(row=0, column=1, sticky='we')

        tk.Label(frm, text="Phone:").grid(row=0, column=2, sticky='w', padx=(10,4))
        self.phone_var = tk.StringVar()
        self.phone_entry = tk.Entry(frm, textvariable=self.phone_var)
        self.phone_entry.grid(row=0, column=3, sticky='we')

        tk.Label(frm, text="Address (search):").grid(row=0, column=4, sticky='w', padx=(10,4))
        self.address_search_var = tk.StringVar()
        tk.Entry(frm, textvariable=self.address_search_var).grid(row=0, column=5, sticky='we')

        frm.grid_columnconfigure(1, weight=1)
        frm.grid_columnconfigure(3, weight=1)
        frm.grid_columnconfigure(5, weight=1)

        # Buttons (Insert opens a modal dialog for Username/Phone/Address)
        btn_frame = ttk.Frame(master)
        btn_frame.pack(fill='x', padx=8, pady=(8,4))

        # refined color palette and fonts
        primary = '#1E88E5'       # main blue
        primary_dark = '#1565C0'  # darker blue for headings/active states
        accent = '#00ACC1'        # teal accent
        bg_light = '#F7F9FC'      # soft app background
        selection_bg = '#E3F2FD'  # gentle selection highlight
        hover_color = '#E1F5FE'   # hover highlight
        # choose a modern system font from a prioritized list (falls back safely)
        available_fonts = set(tkfont.families())
        # include 'Lucida Handwriting' as an available decorative option
        preferred = ['Lucida Handwriting', 'Inter', 'Segoe UI Variable', 'Segoe UI', 'Calibri', 'Helvetica', 'Arial']
        for f in preferred:
            if f in available_fonts:
                base_font = f
                break
        else:
            base_font = 'TkDefaultFont'
        # Use base font size 8 across the UI as requested
        normal_font = (base_font, 8)
        heading_font = (base_font, 8, 'bold')
        button_font = (base_font, 8, 'bold')
        entry_font = (base_font, 8)
        # expose as instance fonts for use throughout the class
        self.normal_font = normal_font
        self.heading_font = heading_font
        self.button_font = button_font
        self.entry_font = entry_font

        # configure ttk styles for a modern look
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Primary.TButton', background=primary, foreground='white', font=button_font, padding=6)
        style.map('Primary.TButton', background=[('active', primary_dark)])
        style.configure('TButton', font=button_font, padding=6)
        style.configure('TLabel', font=normal_font)
        style.configure('TEntry', font=entry_font)

        # Treeview style improvements
        style.configure('Treeview', background=bg_light, fieldbackground=bg_light, foreground='black', rowheight=28, font=normal_font)
        style.configure('Treeview.Heading', background=primary_dark, foreground='white', font=heading_font)
        style.map('Treeview', background=[('selected', selection_bg)], foreground=[('selected', '#0B3B57')])
        # hover tag style (we'll apply tag dynamically)
        self.hover_color = hover_color
        # ensure main window matches the light background initially
        try:
            self.master.configure(bg=bg_light)
        except Exception:
            pass

        # expose palette for dialogs and labels
        self._palette = {'primary': primary, 'accent': accent, 'bg_light': bg_light, 'selection_bg': selection_bg, 'hover': hover_color}
        # apply background color to the top input frame and labels to match the theme
        try:
            frm.configure(bg=self._palette['bg_light'])
            for child in frm.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=self._palette['bg_light'], fg='#0B3B57')
        except Exception:
            pass
        # Note: theme toggle (dark mode) removed; the app uses the light theme only

        # Primary actions — styled
        ttk.Button(btn_frame, text='✚ Insert', style='Primary.TButton', command=self.open_insert_dialog).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='🔎 Username', style='Primary.TButton', command=self.search_by_username).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='📞 Phone', style='Primary.TButton', command=self.search_by_phone).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='🏷️ Address', style='Primary.TButton', command=self.search_by_address).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='📋 Display All', style='Primary.TButton', command=self.display_all).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='✎ Modify', style='Primary.TButton', command=self.modify_selected).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='🗑 Delete', style='Primary.TButton', command=self.delete_selected).pack(side='left', padx=4)
        # Collision table viewer: analyze probing for a key or start index
        ttk.Button(btn_frame, text='🔁 Collision', command=self.open_collision_dialog).pack(side='left', padx=4)
        # make toolbar buttons use hand cursor
        try:
            for child in btn_frame.winfo_children():
                child.configure(cursor='hand2')
        except Exception:
            pass
        # Secondary actions
        ttk.Button(btn_frame, text='💾 Save', command=self.save_file).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='📂 Load', command=self.load_file, style='Primary.TButton').pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Exit', command=master.quit).pack(side='right', padx=4)
        # Table (only Username and Phone are visible in frontend; Address remains in backend only)
        # subtle alternating row color
        light_row = '#EEF7FF'
        # Heading font tweak
        style.configure('Treeview.Heading', font=('TkDefaultFont', 10, 'bold'))
        # selection mapping already configured; ensure text color is consistent
        style.map('Treeview', foreground=[('selected', '#0B3B57')])

        # Split view: left = list, right = detail card
        content_frame = ttk.Frame(master)
        content_frame.pack(fill='both', expand=True, padx=8, pady=6)

        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side='left', fill='both', expand=True)

        right_frame = ttk.Frame(content_frame, width=320, padding=(12,12))
        right_frame.pack(side='right', fill='y', padx=(8,0))

        # Treeview on the left with scrollbar
        self.tree = ttk.Treeview(left_frame, columns=('username','phone'), show='headings', selectmode='extended')
        self.tree.heading('username', text='Username', command=lambda c='username': self._sort_by(c, False))
        self.tree.heading('phone', text='Phone', command=lambda c='phone': self._sort_by(c, False))
        self.tree.column('username', width=300)
        self.tree.column('phone', width=140)
        vsb = ttk.Scrollbar(left_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True, side='left')

        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        # double-click to open modify in detail pane
        self.tree.bind('<Double-1>', self.on_double_click)
        # enable hover highlighting
        self._last_hover = None
        self.tree.bind('<Motion>', self._on_tree_motion)
        self.tree.bind('<Leave>', self._on_tree_leave)
        # Row tag colors for alternating rows
        self.tree.tag_configure('odd', background=self._palette['bg_light'])
        self.tree.tag_configure('even', background=light_row)
        self.tree.tag_configure('hover', background=self.hover_color)
        # briefly highlight newly-inserted rows
        self.tree.tag_configure('recent', background='#FFF9C4')

        # Detail card on the right
        card = ttk.Frame(right_frame, relief='groove', padding=(12,12))
        card.pack(fill='y', expand=True)
        # avatar (initials) canvas
        self.avatar_canvas = tk.Canvas(card, width=64, height=64, bd=0, highlightthickness=0)
        self.avatar_canvas.create_oval(2,2,62,62, fill=self._palette['primary'], outline='')
        self.avatar_text = self.avatar_canvas.create_text(32,34, text='?', fill='white', font=self.heading_font)
        self.avatar_canvas.pack(pady=(0,8))

        ttk.Label(card, text='Name', font=self.normal_font).pack(anchor='w')
        self.detail_name_var = tk.StringVar()
        self.detail_name_e = ttk.Entry(card, textvariable=self.detail_name_var, font=self.entry_font, state='disabled')
        self.detail_name_e.pack(fill='x', pady=(0,6))


        ttk.Label(card, text='Phone', font=self.normal_font).pack(anchor='w')
        self.detail_phone_var = tk.StringVar()
        self.detail_phone_e = ttk.Entry(card, textvariable=self.detail_phone_var, font=self.entry_font, state='disabled')
        self.detail_phone_e.pack(fill='x', pady=(0,6))

        ttk.Label(card, text='Address', font=self.normal_font).pack(anchor='w')
        self.detail_addr_var = tk.StringVar()
        self.detail_addr_e = ttk.Entry(card, textvariable=self.detail_addr_var, font=self.entry_font, state='disabled')
        self.detail_addr_e.pack(fill='x', pady=(0,8))

        # action buttons
        btns = ttk.Frame(card)
        btns.pack(fill='x', pady=(4,0))
        self.edit_btn = ttk.Button(btns, text='Edit', command=lambda: self._set_detail_edit(True), style='Primary.TButton')
        self.edit_btn.pack(side='left', padx=(0,8))
        self.save_btn = ttk.Button(btns, text='Save', command=self._save_detail, state='disabled')
        self.save_btn.pack(side='left', padx=(0,8))
        self.cancel_btn = ttk.Button(btns, text='Cancel', command=self._cancel_detail, state='disabled')
        self.cancel_btn.pack(side='left')

        # quick actions
        quick = ttk.Frame(card)
        quick.pack(fill='x', pady=(8,0))
        ttk.Button(quick, text='Copy Phone', command=self._copy_phone).pack(side='left', padx=(0,6))
        ttk.Button(quick, text='Display Details', command=lambda: self._show_details_external()).pack(side='left', padx=(0,6))

        # detail state
        self._detail_rec = None
        self._detail_edit_mode = False
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set('Ready')
        status = tk.Label(master, textvariable=self.status_var, anchor='w', bg=self._palette['bg_light'], fg='#0B3B57', font=normal_font)
        status.pack(fill='x', padx=8, pady=(0,8))

        self.item_map = {}
        self.showing_address = False  # whether the table currently shows the address column
        # Start with an empty view; do NOT auto-load sample data. User must press 'Display All' to load samples.
        self.populate_table([])
        self.status_var.set("Ready — press 'Display All' to load sample records")

        # keyboard shortcuts
        master.bind_all('<Control-n>', lambda e: self.open_insert_dialog())
        master.bind_all('<Control-f>', lambda e: self.username_entry.focus_set())
        master.bind_all('<Delete>', lambda e: self.delete_selected())
        master.bind_all('<Control-s>', lambda e: self.save_file())
        master.bind_all('<Control-o>', lambda e: self.load_file())
        master.bind_all('<Control-d>', lambda e: self.display_all())
        # accessibility: tooltips and focus order already applied above

        # Tooltips helper
        class _Tip:
            def __init__(self, widget, text):
                self.widget = widget
                self.text = text
                self.tip = None
                widget.bind('<Enter>', self.show)
                widget.bind('<Leave>', self.hide)
            def show(self, _=None):
                if self.tip:
                    return
                x = self.widget.winfo_rootx() + 20
                y = self.widget.winfo_rooty() + 20
                self.tip = tw = tk.Toplevel(self.widget)
                tw.wm_overrideredirect(True)
                tw.wm_geometry(f'+{x}+{y}')
                # subtle tooltip style that matches the light theme
                lbl = tk.Label(tw, text=self.text, bg='#FFF8DC', fg='#0B3B57', relief='solid', bd=1, padx=6, pady=4, font=normal_font)
                lbl.pack()
            def hide(self, _=None):
                if self.tip:
                    self.tip.destroy()
                    self.tip = None

        # tooltips for toolbar buttons (attempt to find them)
        try:
            for child in btn_frame.winfo_children():
                txt = child.cget('text')
                _Tip(child, txt)
        except Exception:
            pass

    def populate_table(self, records=None, show_address=False):
        """Populate the tree. If show_address is True, include the address column.
        When records is None, fetch and sort active username records A→Z.
        Records may be a list of Record objects or a list of dicts describing boxes (for full table view)."""
        # Reconfigure columns if address visibility changed
        if show_address != getattr(self, 'showing_address', False):
            # update columns
            if show_address:
                self.tree['columns'] = ('username', 'phone', 'address')
                self.tree.heading('username', text='Username', command=lambda c='username': self._sort_by(c, False))
                self.tree.heading('phone', text='Phone', command=lambda c='phone': self._sort_by(c, False))
                self.tree.heading('address', text='Address', command=lambda c='address': self._sort_by(c, False))
                self.tree.column('username', width=180)
                self.tree.column('phone', width=120)
                self.tree.column('address', width=220)
            else:
                self.tree['columns'] = ('username', 'phone')
                self.tree.heading('username', text='Username', command=lambda c='username': self._sort_by(c, False))
                self.tree.heading('phone', text='Phone', command=lambda c='phone': self._sort_by(c, False))
                self.tree.column('username', width=200)
                self.tree.column('phone', width=120)
            self.showing_address = show_address

        self.tree.delete(*self.tree.get_children())
        self.item_map.clear()
        # Prepare records (hide address from frontend unless requested)
        if records is None:
            records = [e for e in self.dir.by_username.table if e.is_active()]
            records = sorted(records, key=lambda r: (r.username.lower(), r.phone_number))

        # Insert rows; support Record objects or dicts representing boxes
        for i, rec in enumerate(records):
            tag = 'even' if i % 2 else 'odd'
            # If rec is a dict (full-box view), extract display values and keep reference
            if isinstance(rec, dict):
                uname = rec.get('username')
                phone = rec.get('phone')
                addr = rec.get('address')
                ref = rec.get('record')
                if show_address:
                    iid = self.tree.insert('', 'end', values=(uname, phone, addr), tags=(tag,))
                else:
                    iid = self.tree.insert('', 'end', values=(uname, phone), tags=(tag,))
                self.item_map[iid] = ref
            else:
                # assume Record
                if show_address:
                    iid = self.tree.insert('', 'end', values=(rec.username, rec.phone_number, rec.address), tags=(tag,))
                else:
                    iid = self.tree.insert('', 'end', values=(rec.username, rec.phone_number), tags=(tag,))
                self.item_map[iid] = rec

        # Reset top entry text color to default (black) after repopulating
        try:
            self.username_entry.config(fg='black')
            self.phone_entry.config(fg='black')
        except Exception:
            pass
        self.status_var.set(f"{len(records)} row(s) shown")

    # Treeview helpers: hover and column-sort
    def _on_tree_motion(self, event):
        cur = self.tree.identify_row(event.y)
        if cur == self._last_hover:
            return
        # remove old hover
        if self._last_hover:
            try:
                self.tree.item(self._last_hover, tags=self.tree.item(self._last_hover, 'tags'))
            except Exception:
                pass
        # apply hover tag to current
        if cur:
            tags = list(self.tree.item(cur, 'tags'))
            if 'hover' not in tags:
                tags.append('hover')
            self.tree.item(cur, tags=tags)
        self._last_hover = cur

    def _on_tree_leave(self, event):
        if self._last_hover:
            try:
                tags = list(self.tree.item(self._last_hover, 'tags'))
                if 'hover' in tags:
                    tags.remove('hover')
                self.tree.item(self._last_hover, tags=tags)
            except Exception:
                pass
            self._last_hover = None

    def _sort_by(self, col, descending):
        # get data to sort from visible column values
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            data.sort(key=lambda t: (t[0] is None, t[0].lower()), reverse=descending)
        except Exception:
            data.sort(reverse=descending)
        # rearrange items in sorted order
        for index, (_, k) in enumerate(data):
            self.tree.move(k, '', index)
        # reverse sort next time
        self.tree.heading(col, command=lambda c=col: self._sort_by(c, not descending))

    def insert_record(self):
        # Kept for compatibility; prefer using the modal insert dialog instead.
        self.open_insert_dialog()

    def open_insert_dialog(self):
        dlg = tk.Toplevel(self.master)
        dlg.title('Insert New Record')
        dlg.transient(self.master)
        dlg.grab_set()

        ttk.Label(dlg, text='Username:').grid(row=0, column=0, sticky='w', padx=8, pady=6)
        uname_var = tk.StringVar()
        uname_e = ttk.Entry(dlg, textvariable=uname_var)
        uname_e.grid(row=0, column=1, padx=8, pady=6)
        try:
            uname_e.configure(font=self.entry_font)
        except Exception:
            pass

        ttk.Label(dlg, text='Phone:').grid(row=1, column=0, sticky='w', padx=8, pady=6)
        phone_var = tk.StringVar()
        phone_e = ttk.Entry(dlg, textvariable=phone_var)
        phone_e.grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(dlg, text='Address (backend only):').grid(row=2, column=0, sticky='w', padx=8, pady=6)
        addr_var = tk.StringVar()
        addr_e = ttk.Entry(dlg, textvariable=addr_var)
        addr_e.grid(row=2, column=1, padx=8, pady=6)

        # inline error label
        error_var = tk.StringVar()
        err_lbl = ttk.Label(dlg, textvariable=error_var, foreground='red')
        err_lbl.grid(row=3, column=0, columnspan=2, padx=8, pady=(0,4))



        # make the dialog visually match the main theme
        dlg.configure(bg=self._palette.get('bg_light', 'white'))

        # placeholders: insert hint text and remove on focus
        uname_hint = 'e.g., alice'
        phone_hint = 'e.g., 555-1234'
        addr_hint = 'e.g., Room 203'
        uname_e.insert(0, uname_hint)
        phone_e.insert(0, phone_hint)
        addr_e.insert(0, addr_hint)
        def _clear_hint(e, hint):
            if e.get() == hint:
                e.delete(0, 'end')
        def _restore_hint(e, hint):
            if not e.get():
                e.insert(0, hint)
        uname_e.bind('<FocusIn>', lambda ev: _clear_hint(uname_e, uname_hint))
        uname_e.bind('<FocusOut>', lambda ev: _restore_hint(uname_e, uname_hint))
        phone_e.bind('<FocusIn>', lambda ev: _clear_hint(phone_e, phone_hint))
        phone_e.bind('<FocusOut>', lambda ev: _restore_hint(phone_e, phone_hint))
        addr_e.bind('<FocusIn>', lambda ev: _clear_hint(addr_e, addr_hint))
        addr_e.bind('<FocusOut>', lambda ev: _restore_hint(addr_e, addr_hint))

        def on_confirm():
            username = uname_var.get().strip()
            phone = phone_var.get().strip()
            addr = addr_var.get().strip()
            # validate
            if not username or username == uname_hint:
                error_var.set('Username is required')
                uname_e.focus_set()
                return
            if not phone or phone == phone_hint:
                error_var.set('Phone is required')
                phone_e.focus_set()
                return
            # basic phone validation (digits and basic punctuation)
            if not any(ch.isdigit() for ch in phone):
                error_var.set('Phone must contain digits')
                phone_e.focus_set()
                return
            rec = Record(phone, username, addr)
            probes = self.dir.insert(rec, by='username')
            if probes is None:
                messagebox.showerror('Insert failed', 'Directory is full or insertion failed.')
                dlg.destroy()
                return
            p_user, p_phone = probes
            # Refresh view so new record appears immediately
            self.status_var.set(f'Inserted {username} (probes u={p_user}, p={p_phone}).')
            # If currently showing the full table (Address visible), refresh full view, otherwise show active records
            if getattr(self, 'showing_address', False):
                self.display_all()
            else:
                self.populate_table()
            # Try to find and select the newly-inserted record, and flash it briefly
            try:
                entry, _ = self.dir.search(username, by='username')
                if entry:
                    for iid, ref in self.item_map.items():
                        if ref and ref.username == entry.username and ref.phone_number == entry.phone_number:
                            self.tree.selection_set(iid)
                            self.tree.see(iid)
                            # add 'recent' tag to highlight
                            tags = list(self.tree.item(iid, 'tags'))
                            if 'recent' not in tags:
                                tags.append('recent')
                                self.tree.item(iid, tags=tags)
                                def _remove_recent(iid=iid):
                                    try:
                                        t = list(self.tree.item(iid, 'tags'))
                                        if 'recent' in t:
                                            t.remove('recent')
                                            self.tree.item(iid, tags=t)
                                    except Exception:
                                        pass
                                self.master.after(1500, _remove_recent)
                            self.populate_detail_pane(entry)
                            break
            except Exception:
                pass
            dlg.destroy()
            # If insertion required probing (collision), automatically show the collision table for inspection
            try:
                if p_user and p_user > 1:
                    # show username-based collision table
                    self.show_collision_table(username, 'username')
                elif p_phone and p_phone > 1:
                    # fallback: show phone-based collision table
                    self.show_collision_table(phone, 'phone')
            except Exception:
                # don't let visualization errors interrupt flow
                pass

        btn_frame = ttk.Frame(dlg)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(0,8))
        ttk.Button(btn_frame, text='Confirm', command=on_confirm, style='Primary.TButton').pack(side='left', padx=8)
        ttk.Button(btn_frame, text='Cancel', command=dlg.destroy).pack(side='right', padx=8)

        uname_e.focus_set()
        self.master.wait_window(dlg)

    def open_modify_dialog(self, record):
        dlg = tk.Toplevel(self.master)
        dlg.title('Modify Record')
        dlg.transient(self.master)
        dlg.grab_set()

        ttk.Label(dlg, text='Username:').grid(row=0, column=0, sticky='w', padx=8, pady=6)
        uname_var = tk.StringVar(value=record.username)
        uname_e = ttk.Entry(dlg, textvariable=uname_var)
        uname_e.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(dlg, text='Phone:').grid(row=1, column=0, sticky='w', padx=8, pady=6)
        phone_var = tk.StringVar(value=record.phone_number)
        phone_e = ttk.Entry(dlg, textvariable=phone_var)
        phone_e.grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(dlg, text='Address:').grid(row=2, column=0, sticky='w', padx=8, pady=6)
        addr_var = tk.StringVar(value=record.address)
        addr_e = ttk.Entry(dlg, textvariable=addr_var)
        addr_e.grid(row=2, column=1, padx=8, pady=6)



        error_var = tk.StringVar()
        err_lbl = ttk.Label(dlg, textvariable=error_var, foreground='red')
        err_lbl.grid(row=4, column=0, columnspan=2, padx=8, pady=(0,4))

        dlg.configure(bg=self._palette.get('bg_light', 'white'))

        def on_confirm():
            new_uname = uname_var.get().strip()
            new_phone = phone_var.get().strip()
            new_addr = addr_var.get().strip()
            if not new_uname:
                error_var.set('Username is required')
                uname_e.focus_set()
                return
            if not new_phone or not any(ch.isdigit() for ch in new_phone):
                error_var.set('Phone number is required and must contain digits')
                phone_e.focus_set()
                return
            ok, msg = self.dir.modify_record(record, new_uname, new_phone, new_addr)
            if not ok:
                messagebox.showerror('Modify failed', msg)
                return
            messagebox.showinfo('Modified', f'Record modified: {new_uname}')
            dlg.destroy()
            # refresh view
            self.display_all()

        btn_frame = ttk.Frame(dlg)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(0,8))
        ttk.Button(btn_frame, text='Confirm', command=on_confirm, style='Primary.TButton').pack(side='left', padx=8)
        ttk.Button(btn_frame, text='Cancel', command=dlg.destroy).pack(side='right', padx=8)

        uname_e.focus_set()
        self.master.wait_window(dlg)

    def search_by_username(self):
        key = self.username_var.get().strip()
        if not key:
            messagebox.showwarning("Input required", "Enter a username to search.")
            return
        # Use search to get probe count for exact lookup, and search_all to get any matches to display
        entry, probes = self.dir.search(key, by='username')
        recs = self.dir.search_all(key, by='username')
        self.populate_table(recs)
        if not recs:
            self.status_var.set(f"No matching records found (probes: {probes})")
        else:
            self.status_var.set(f"Found {len(recs)} record(s) for username '{key}' — search length: {probes} probe(s)")

    def search_by_phone(self):
        key = self.phone_var.get().strip()
        if not key:
            messagebox.showwarning("Input required", "Enter a phone number to search.")
            return
        # Use search to get probe count for exact lookup, and search_all to build the result list
        entry, probes = self.dir.search(key, by='phone')
        recs = self.dir.search_all(key, by='phone')
        self.populate_table(recs)
        if not recs:
            self.status_var.set(f"No matching records found (probes: {probes})")
        else:
            self.status_var.set(f"Found {len(recs)} record(s) for phone '{key}' — search length: {probes} probe(s)")

    def search_by_address(self):
        key = self.address_search_var.get().strip()
        if not key:
            messagebox.showwarning("Input required", "Enter an address (or part) to search.")
            return
        recs = self.dir.search_all(key, by='address')
        self.populate_table(recs)
        if not recs:
            self.status_var.set('No matching records found')
        else:
            self.status_var.set(f"Found {len(recs)} record(s) with address matching '{key}'")

    # Detail pane helpers
    def populate_detail_pane(self, rec):
        """Fill the right-hand detail card with record data. rec may be None.
        Detail pane is for viewing and inline modification."""
        self._detail_rec = rec
        if not rec:
            self.detail_name_var.set('')
            self.detail_phone_var.set('')
            self.detail_addr_var.set('')
            self._update_avatar('?')
            self._set_detail_edit(False)
            return
        self.detail_name_var.set(rec.username)
        self.detail_phone_var.set(rec.phone_number)
        self.detail_addr_var.set(rec.address)
        # set avatar initials
        initials = ''.join([p[0].upper() for p in rec.username.split() if p])[:2] or '?'
        self._update_avatar(initials, bg=self._color_for_name(rec.username))
        self._set_detail_edit(False)

    def _update_avatar(self, text, bg=None):
        """Update the avatar canvas with initials text and optional background color."""
        try:
            # draw colored circle as background
            if bg:
                try:
                    # remove any previous circle (create new with tag)
                    self.avatar_canvas.delete('back')
                except Exception:
                    pass
                self.avatar_canvas.create_oval(2,2,62,62, fill=bg, outline='', tags='back')
            # update initials text
            self.avatar_canvas.itemconfigure(self.avatar_text, text=text)
        except Exception:
            pass

    def _color_for_name(self, name: str) -> str:
        """Deterministically pick a color for a name."""
        colors = ['#F44336','#E91E63','#9C27B0','#3F51B5','#2196F3','#03A9F4','#009688','#4CAF50','#FF9800','#795548']
        h = sum(ord(c) for c in (name or ''))
        return colors[h % len(colors)]



    def _set_detail_edit(self, enable: bool):
        self._detail_edit_mode = enable
        state = 'normal' if enable else 'disabled'
        try:
            self.detail_name_e.configure(state=state)
            self.detail_phone_e.configure(state=state)
            self.detail_addr_e.configure(state=state)
        except Exception:
            pass
        self.save_btn.configure(state='normal' if enable else 'disabled')
        self.cancel_btn.configure(state='normal' if enable else 'disabled')
        self.edit_btn.configure(state='disabled' if enable else 'normal')

    def _save_detail(self):
        if not self._detail_rec:
            messagebox.showwarning('No record', 'No record selected to save.')
            return
        new_uname = self.detail_name_var.get().strip()
        new_phone = self.detail_phone_var.get().strip()
        new_addr = self.detail_addr_var.get().strip()
        if not new_uname:
            messagebox.showwarning('Input', 'Name required')
            return
        if not any(ch.isdigit() for ch in new_phone):
            messagebox.showwarning('Input', 'Phone must contain digits')
            return
        ok, msg = self.dir.modify_record(self._detail_rec, new_uname, new_phone, new_addr)
        if not ok:
            messagebox.showerror('Modify failed', msg)
            return
        messagebox.showinfo('Modified', 'Record updated')
        self._set_detail_edit(False)
        # refresh table and reselect updated record
        self.display_all()
        # re-find the record by username
        entry, _ = self.dir.search(new_uname, by='username')
        if entry:
            # select the row
            for iid, ref in self.item_map.items():
                if ref and ref.username == entry.username and ref.phone_number == entry.phone_number:
                    self.tree.selection_set(iid)
                    self.tree.see(iid)
                    self.populate_detail_pane(entry)
                    break

    def _cancel_detail(self):
        # revert fields
        if self._detail_rec:
            self.populate_detail_pane(self._detail_rec)
        else:
            self.populate_detail_pane(None)
        self._set_detail_edit(False)

    def _copy_phone(self):
        if not self._detail_rec:
            return
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(self._detail_rec.phone_number)
            self.status_var.set('Phone copied to clipboard')
        except Exception:
            pass

    def _show_details_external(self):
        if not self._detail_rec:
            return
        messagebox.showinfo('Details', f"{self._detail_rec}\n\n(Use Edit to modify this contact)")
    def display_all(self):
        # Ensure built-in samples are loaded first (only once) so Display All shows them by default
        loaded_msg = ''
        if not self.dir.samples_loaded:
            count_loaded = self.dir.load_samples()
            loaded_msg = f"Loaded {count_loaded} sample record(s). " if count_loaded else ''
        # Build a full list of boxes (size TABLE_SIZE) including empty and deleted slots
        boxes = []
        for idx, entry in enumerate(self.dir.by_username.table):
            if entry.is_active():
                boxes.append({'username': entry.username, 'phone': entry.phone_number, 'address': entry.address, 'record': entry, 'index': idx, 'deleted': False})
            elif entry.deleted:
                # deleted slots: treat as empty (no visual marker)
                boxes.append({'username': '', 'phone': '-', 'address': '-', 'record': None, 'index': idx, 'deleted': True})
            else:
                # for empty slots show an empty username string
                boxes.append({'username': '', 'phone': '-', 'address': '-', 'record': None, 'index': idx, 'deleted': False})
        # Sort boxes by username for display, but keep empties/deleted grouped at the end to reflect empties visually
        active_boxes = [b for b in boxes if b['record'] is not None]
        empty_deleted = [b for b in boxes if b['record'] is None]
        active_sorted = sorted(active_boxes, key=lambda r: (r['username'].lower(), r['phone']))
        records_sorted = active_sorted + empty_deleted
        # show address column for the full display
        self.populate_table(records_sorted, show_address=True)
        count = len(active_sorted)
        empty_slots = sum(1 for b in boxes if b['record'] is None)
        free = empty_slots
        self.status_var.set(f"{loaded_msg}Showing {count} active record(s) + {empty_slots} empty — {TABLE_SIZE} boxes ({free} free)")

    def delete_selected(self):
        sels = self.tree.selection()
        if not sels:
            messagebox.showwarning("Select", "Select one or more rows to delete.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(sels)} selected record(s)?"):
            return
        deleted = 0
        for iid in sels:
            rec = self.item_map.get(iid)
            if rec:
                ok = self.dir.delete_record(rec)
                if ok:
                    deleted += 1
        self.display_all()
        self.status_var.set(f"Deleted {deleted} record(s)")

    def open_collision_dialog(self):
        """Show the collision probe visualization for the selected or entered key."""
        sels = self.tree.selection()
        if sels:
            rec = self.item_map.get(sels[0])
            if rec:
                try:
                    self.show_collision_table(rec.username, 'username')
                except Exception:
                    pass
                return
        # Without a selected row, use the current search key for the probe view.
        username_key = self.username_var.get().strip()
        phone_key = self.phone_var.get().strip()
        if username_key:
            self.show_collision_table(username_key, 'username')
        elif phone_key:
            self.show_collision_table(phone_key, 'phone')
        else:
            messagebox.showwarning('Select or search', 'Select a contact or enter a username or phone number first.')

    def show_collision_table(self, key, mode='username'):
        """Visualize probe sequences and insertion point for the given key or start index.
        mode: 'username'|'phone'|'index'"""
        # determine start index
        if mode == 'index':
            try:
                start_index = int(key)
            except ValueError:
                messagebox.showerror('Invalid index', 'Start index must be an integer between 0 and TABLE_SIZE-1')
                return
            if not (0 <= start_index < TABLE_SIZE):
                messagebox.showerror('Invalid index', f'Index must be between 0 and {TABLE_SIZE-1}')
                return
            probe_key = ''
            by = 'username'
        elif mode == 'phone':
            start_index = self.dir.by_phone.hash_func(key)
            probe_key = key
            by = 'phone'
        else:
            start_index = self.dir.by_username.hash_func(key)
            probe_key = key
            by = 'username'

        table = self.dir.by_username.table
        # compute search probe sequence (stops when finds key or empty non-deleted slot)
        search_seq = []
        found_search = False
        for i in range(TABLE_SIZE):
            pos = (start_index + i) % TABLE_SIZE
            search_seq.append(pos)
            entry = table[pos]
            if entry.is_active():
                if by == 'username' and entry.username.lower() == probe_key.lower():
                    found_search = True
                    break
                if by == 'phone' and entry.phone_number == probe_key:
                    found_search = True
                    break
            else:
                if not entry.deleted:
                    # reached a truly empty slot - search stops
                    break
        # compute insertion probe sequence (stops at first non-active slot)
        insert_seq = []
        insert_index = None
        for i in range(TABLE_SIZE):
            pos = (start_index + i) % TABLE_SIZE
            insert_seq.append(pos)
            if not table[pos].is_active():
                insert_index = pos
                break

        # Build and display the table
        win = tk.Toplevel(self.master)
        win.title(f'Collision table starting at {start_index}')
        win.transient(self.master)

        cols = ('index','username','phone','status','probed_search','probed_insert')
        tv = ttk.Treeview(win, columns=cols, show='headings')
        for c in cols:
            tv.heading(c, text=c.title())
            tv.column(c, width=120)
        tv.pack(fill='both', expand=True, padx=8, pady=8)

        # tags
        tv.tag_configure('probed_search', background=self._palette['selection_bg'])
        tv.tag_configure('probed_insert', background=self._palette['accent'])
        tv.tag_configure('insert_here', background=self._palette['primary'])

        for idx, entry in enumerate(table):
            if entry.is_active():
                status = 'Active'
                uname = entry.username
                phone = entry.phone_number
            elif entry.deleted:
                status = 'Deleted'
                uname = ''
                phone = '-'
            else:
                status = 'Empty'
                uname = ''
                phone = '-'
            ps = 'Yes' if idx in search_seq else ''
            pi = 'Yes' if idx in insert_seq else ''
            values = (idx, uname, phone, status, ps, pi)
            tags = []
            if idx in search_seq:
                tags.append('probed_search')
            if idx in insert_seq:
                tags.append('probed_insert')
            if insert_index == idx:
                tags.append('insert_here')
            tv.insert('', 'end', values=values, tags=tags)

        info = tk.Label(win, text=f'Search found: {found_search}. Insert at: {insert_index if insert_index is not None else "(table full)"}', anchor='w')
        info.pack(fill='x', padx=8, pady=(0,8))

        ttk.Button(win, text='Close', command=win.destroy).pack(pady=(0,8))
        win.grab_set()
        self.master.wait_window(win)

    def show_backend_table(self):
        """Display the raw hash table (backend view) showing index, username, phone, and status in index order."""
        table = self.dir.by_username.table
        win = tk.Toplevel(self.master)
        win.title('Hash Table (backend view)')
        win.transient(self.master)

        cols = ('index','username','phone','status')
        tv = ttk.Treeview(win, columns=cols, show='headings')
        for c in cols:
            tv.heading(c, text=c.title())
            tv.column(c, width=120)
        tv.pack(fill='both', expand=True, padx=8, pady=8)

        # tags for clarity
        tv.tag_configure('deleted', background='#F5F5F5')
        tv.tag_configure('empty', background='#FFFFFF')

        for idx, entry in enumerate(table):
            if entry.is_active():
                status = 'Active'
                uname = entry.username
                phone = entry.phone_number
                tags = []
            elif entry.deleted:
                status = 'Deleted'
                uname = ''
                phone = '-'
                tags = ['deleted']
            else:
                status = 'Empty'
                uname = ''
                phone = '-'
                tags = ['empty']
            tv.insert('', 'end', values=(idx, uname, phone, status), tags=tags)

        ttk.Button(win, text='Close', command=win.destroy).pack(pady=(0,8))
        win.grab_set()
        self.master.wait_window(win)

    def save_file(self):
        fname = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv'), ('All files','*.*')])
        if not fname:
            return
        # Write from the username table a CSV with columns: username,phone,address
        try:
            with open(fname, 'w', newline='') as f:
                writer = csv.writer(f)
                for entry in self.dir.by_username.table:
                    if entry.is_active():
                        writer.writerow([entry.username, entry.phone_number, entry.address])
            self.status_var.set(f"Saved to {fname}")
            messagebox.showinfo("Saved", f"Directory saved to {fname}")
        except Exception as e:
            messagebox.showerror('Save failed', str(e))

    def load_file(self):
        fname = filedialog.askopenfilename(filetypes=[('CSV files','*.csv'), ('All files','*.*')])
        if not fname:
            return
        try:
            # load into username table then rebuild phone index
            self.dir.by_username.load(fname)
            self.dir.by_phone = HashTable(load_samples=False)
            for entry in self.dir.by_username.table:
                if entry.is_active():
                    self.dir.by_phone.insert(entry, by='phone')
            self.display_all()
            self.status_var.set(f"Loaded from {fname}")
            messagebox.showinfo("Loaded", f"Directory loaded from {fname}")
        except Exception as e:
            messagebox.showerror('Load failed', str(e))

    def load_samples_button(self):
        count = self.dir.load_samples()
        self.display_all()
        if count:
            self.status_var.set(f"Loaded {count} sample record(s)")
        else:
            self.status_var.set("Sample data already loaded")

    def on_select(self, event):
        sels = self.tree.selection()
        if not sels:
            return
        iid = sels[0]
        rec = self.item_map.get(iid)
        if rec:
            self.username_var.set(rec.username)
            self.phone_var.set(rec.phone_number)
            # make entry text red when selected
            try:
                self.username_entry.config(fg='red')
                self.phone_entry.config(fg='red')
            except Exception:
                pass
            if getattr(self, 'showing_address', False):
                # include address in status when displayAll is showing addresses
                self.status_var.set(f"Selected: {rec.username} | {rec.phone_number} | {rec.address}")
            else:
                self.status_var.set(f"Selected: {rec.username} | {rec.phone_number}")
            self.populate_detail_pane(rec)

    def on_double_click(self, event):
        rowid = self.tree.identify_row(event.y)
        if not rowid:
            return
        rec = self.item_map.get(rowid)
        if rec:
            # focus detail pane and enable editing
            self.populate_detail_pane(rec)
            self._set_detail_edit(True)

    def modify_selected(self):
        sels = self.tree.selection()
        if not sels:
            messagebox.showwarning('Select', 'Select a row to modify.')
            return
        iid = sels[0]
        rec = self.item_map.get(iid)
        if not rec:
            messagebox.showwarning('Select', 'Selected row is not editable.')
            return
        # populate detail pane and enable edit
        self.populate_detail_pane(rec)
        self._set_detail_edit(True)

def menu():
    print("""
    1. Insert record
    2. Search by username
    3. Search by phone number
    4. Delete by username
    5. Delete by phone number
    6. Display all records
    7. Save table to file
    8. Load table from file
    9. Exit
    10. Search by address
    """)

def get_record():
    username = input("Enter username: ").strip()
    phone = input("Enter phone number: ").strip()
    addr = input("Enter address: ").strip()
    return Record(phone, username, addr)

def main():
    dir = Directory()
    while True:
        menu()
        choice = input("Select option: ")
        if choice == "1":
            if dir.is_full():
                print("Cannot insert: Hash table full.")
                continue
            record = get_record()
            by = input("Insert by [username/phone] (default=username): ").strip() or "username"
            probes = dir.insert(record, by=by)
            if probes is None:
                print("Insertion failed: Table full or error.")
            else:
                p_user, p_phone = probes
                print(f"Inserted. Probe lengths: username={p_user}, phone={p_phone}")
        elif choice == "2":
            key = input("Username to search: ").strip()
            entry, probes = dir.search(key, by='username')
            if entry:
                print("Found:", entry)
            else:
                print("Not found.")
            print(f"Probe length: {probes}")
        elif choice == "3":
            key = input("Phone number to search: ").strip()
            entry, probes = dir.search(key, by='phone')
            if entry:
                print("Found:", entry)
            else:
                print("Not found.")
            print(f"Probe length: {probes}")
        elif choice == "4":
            key = input("Username to delete: ").strip()
            if dir.delete(key, by='username'):
                print("Deleted.")
            else:
                print("Not found.")
        elif choice == "5":
            key = input("Phone number to delete: ").strip()
            if dir.delete(key, by='phone'):
                print("Deleted.")
            else:
                print("Not found.")
        elif choice == "6":
            dir.display()
        elif choice == "7":
            filename = input("Filename to save: ").strip()
            dir.save(filename)
            print("Saved.")
        elif choice == "8":
            filename = input("Filename to load: ").strip()
            dir.load(filename)
            print("Loaded.")
        elif choice == "9":
            print("Exiting.")
            break
        elif choice == "10":
            key = input("Address to search (substring): ").strip()
            results = dir.search_all(key, by='address')
            if results:
                print(f"Found {len(results)} record(s):")
                for rec in results:
                    print("  ", rec)
            else:
                print("Not found.")
        else:
            print("Invalid option.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DirectoryGUI(root)
    root.mainloop()