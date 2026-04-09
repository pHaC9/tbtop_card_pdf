import sys
from tkinter import *
import ttkbootstrap as ttk
import guiFunctions
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from dataclasses import dataclass
from models import FileInfo, Card


root = ttk.Window(title="Tabletop Simulator Card Game Sheet Generator", themename="darkly", resizable=(False, False))

def only_digits(new_value: str) -> bool:
    return new_value.isdigit() or new_value == ""
vcmd_only_digits = root.register(only_digits)

def close_program():
    root.destroy()
    sys.exit() 
root.protocol("WM_DELETE_WINDOW", close_program)
    

cardList = {}
fileList: dict[str, FileInfo] = {}

is_editing = False

'''------------------------------------------------------------------------------------------------------------------------------'''
'''---------------------------------------------------------WIDGETS--------------------------------------------------------------'''
'''------------------------------------------------------------------------------------------------------------------------------'''


'''------------------------------------------------------------------------------------------------------------------------------'''
'''------------------------------------------------------------------------------------------------------------------------------'''
'''                                                   IMAGENS DE ENTRADA                                                         '''
'''------------------------------------------------------------------------------------------------------------------------------'''
'''------------------------------------------------------------------------------------------------------------------------------'''
# Image Inputs Frame
frame_ImgInput = ttk.Labelframe(root, borderwidth=20, text="Imagens de Entrada", bootstyle=INFO)
frame_ImgInput.grid(row=0, column=0, padx=60, pady=40, sticky=EW)

# Painel para display dos nomes dos arquivos
innerFrame_ImgInput = Frame(frame_ImgInput)
innerFrame_ImgInput.pack()

comboBox_ImgInput = ttk.Combobox(frame_ImgInput, bootstyle=PRIMARY, validate=NONE, state='readonly')
comboBox_ImgInput.pack(fill=X)
comboBox_ImgInput.bind(
    "<<ComboboxSelected>>",
    lambda _:
        guiFunctions.UpdateImagePreview(
            image_label,
            fileList,
            comboBox_ImgInput.get()
        )
)

# Botões para adicionar/remover arquivos da lista
button_LoadImage = Button(frame_ImgInput, text= "Importar", 
                          command= lambda: guiFunctions.ImportImageFile(comboBox_ImgInput, fileList, image_label, selectedFileVar, label_selectedFile2))
button_RemoveImage = Button(frame_ImgInput, text="Remover", 
                            command= lambda: guiFunctions.RemoveImageFile(comboBox_ImgInput, fileList, image_label, selectedFileVar, label_selectedFile2, tree))
button_RemoveImage.pack(side = RIGHT, pady=(20,0), padx=(20,0))
button_LoadImage.pack(side = RIGHT, pady=(20,0))


'''------------------------------------------------------------------------------------------------------------------------------'''
'''------------------------------------------------------------------------------------------------------------------------------'''
'''                                           CONFIGURAÇÃO DE LINHAS E COLUNAS                                                   '''
'''------------------------------------------------------------------------------------------------------------------------------'''
'''------------------------------------------------------------------------------------------------------------------------------'''
# Inputs para configurar o número de linhas e colunas na imagem
frame_RowsColumsConfig = ttk.Labelframe(root, borderwidth=20, text="Definição de Linhas/Colunas", bootstyle=INFO)
frame_RowsColumsConfig.grid(row=1, column=0, padx=60, pady=(0, 20), ipadx=40, sticky=EW)

frame_fileLabel = Frame(frame_RowsColumsConfig)
frame_fileLabel.pack(anchor=W, pady=(0, 20))

selectedFileVar = StringVar(value="Nenhum arquivo selecionado.")

label_selectedFile1 = ttk.Label(frame_fileLabel, text="Arquivo:")
label_selectedFile2 = ttk.Label(
    frame_fileLabel,
    textvariable=selectedFileVar,
    bootstyle="warning"
)

label_selectedFile1.pack(side=LEFT, anchor=NW)
label_selectedFile2.pack(side=LEFT, anchor=NW)

comboBox_ImgInput.bind(
    "<<ComboboxSelected>>",
    lambda e: guiFunctions.Update_Selected_File_Label(
        comboBox_ImgInput,
        fileList,
        selectedFileVar,
        label_selectedFile2
    ),
    add="+"
)

innerFrame_RowsColumnsConfig = Frame(frame_RowsColumsConfig)
innerFrame_RowsColumnsConfig.pack(anchor=NW)

rowAmount = IntVar()
columnAmount = IntVar()
label_rows = Label(innerFrame_RowsColumnsConfig, text="Linhas:")
entry_rows = Entry(
    innerFrame_RowsColumnsConfig,
    textvariable=rowAmount,
    width=5,
    validate="key",
    validatecommand=(vcmd_only_digits, "%P")
)
label_colunas = Label(innerFrame_RowsColumnsConfig, text="Colunas:")
entry_colunas = Entry(
    innerFrame_RowsColumnsConfig,
    textvariable=columnAmount,
    width=5,
    validate="key",
    validatecommand=(vcmd_only_digits, "%P")
)


label_rows.pack(side=LEFT)
entry_rows.pack(side=LEFT, padx=(10, 0))
label_colunas.pack(side=LEFT, padx=(20, 0))
entry_colunas.pack(side=LEFT, padx=(10, 0))

# Botão para carregar as cartas presentes na imagem ("AddCardsToList()")
button_LoadCards = Button(
    frame_RowsColumsConfig,
    text="Carregar Cartas",
    command=lambda:
        guiFunctions.AddCardsToList(
            comboBox_ImgInput,
            rowAmount,
            columnAmount,
            tree,
            fileList,
            progress_bar,
            progress_var,
            progress_label_var,
            root,
            controls_to_disable=[
                button_LoadCards,
                button_LoadImage,
                button_RemoveImage,
                button_CreatePDF,
                comboBox_ImgInput
            ]
        )
)

button_LoadCards.pack(side = BOTTOM, pady=(20,0))

progress_var = IntVar(value=0)

progress_bar = ttk.Progressbar(
    frame_RowsColumsConfig,
    variable=progress_var,
    bootstyle=INFO,
    length=250,
    mode="determinate"
)

progress_label_var = StringVar(value="")
progress_label = ttk.Label(
    frame_RowsColumsConfig,
    textvariable=progress_label_var,
)

progress_bar.pack(pady=(20, 0))
progress_label.pack()




'''------------------------------------------------------------------------------------------------------------------------------'''
'''------------------------------------------------------------------------------------------------------------------------------'''
'''                                          PREVIEW DA IMAGEM E LISTA DE CARTAS                                                 '''
'''------------------------------------------------------------------------------------------------------------------------------'''
'''------------------------------------------------------------------------------------------------------------------------------'''
# CardList Frame
frame_CardList = Frame(root)
frame_CardList.grid(row=0, column=1, pady=40, padx=(0, 60), ipadx=40, rowspan=2)
notebook_CardList = ttk.Notebook(frame_CardList, bootstyle=DEFAULT)

msg_noFileFound = "Nenhum arquivo selecionado."

# Possui duas tabs:
# TAB1: Preview da imagem selecionada
frame_ImagePreviewTab = ttk.Frame(notebook_CardList, padding=10, bootstyle=SECONDARY, height=570, width=570)
frame_ImagePreviewTab.pack_propagate(False)
notebook_CardList.add(frame_ImagePreviewTab, text='Preview da Imagem')


image_label = ttk.Label(frame_ImagePreviewTab, background="#444444")
image_label.pack(expand=True)

guiFunctions.ClearImagePreview(image_label)

# TAB2: Mostra as cartas encontradas e a quantidade default de cópias para incluir
frame_CardListTab = ttk.Frame(notebook_CardList)
notebook_CardList.add(frame_CardListTab, text='Lista de Cartas')
notebook_CardList.pack(fill=BOTH, expand=True)

frame_CardListTab.pack_propagate(False)
frame_CardListTab.config(width=600, height=600)

last_selected_item = None


def Show_Copies_Entry(event=None):
    global last_selected_item, is_editing

    if not is_editing:
        return

    selected = tree.selection()
    if not selected:
        copies_entry.place_forget()
        last_selected_item = None
        return

    item = selected[0]
    last_selected_item = item

    bbox = tree.bbox(item, column="copies")
    if not bbox:
        copies_entry.place_forget()
        return

    x, y, w, h = bbox

    copies_entry.place(
        x=x + w // 2 - 15,
        y=y + h // 2 - 10,
        width=30
    )

    current_value = tree.set(item, "copies")
    copies_entry.delete(0, "end")
    copies_entry.insert(0, current_value)
    copies_entry.focus()
    copies_entry.select_range(0, END)

def Save_Copies_Value(event=None):
    selected = tree.selection()
    if not selected:
        return

    item = selected[0]
    value = copies_entry.get()

    if not value.isdigit():
        value = "0"

    tree.set(item, "copies", value)
    copies_entry.place_forget()

    guiFunctions.Update_Card_Copies(item, int(value))

def Start_Edit(event=None):
    global is_editing
    is_editing = True
    Show_Copies_Entry()

def Commit_Copies_Entry(event=None, move_next=True):
    global last_selected_item, is_editing

    if not last_selected_item:
        return

    value = copies_entry.get()
    if value == "":
        value = "0"

    tree.set(last_selected_item, "copies", value)
    guiFunctions.Update_Card_Copies(last_selected_item, int(value))

    if not move_next:
        copies_entry.place_forget()
        is_editing = False
        return

    children = tree.get_children()
    try:
        current_index = children.index(last_selected_item)
        next_item = children[current_index + 1]
    except (ValueError, IndexError):
        copies_entry.place_forget()
        is_editing = False
        return

    tree.selection_set(next_item)
    tree.focus(next_item)
    last_selected_item = next_item

    Show_Copies_Entry()

def On_Tree_Click(event):
    Commit_Copies_Entry(move_next=False)

def On_Scroll(event=None):
    copies_entry.place_forget()

style = ttk.Style()
style.configure(
    "Card.Treeview",
    rowheight=140   # ajuste conforme o preview
)

columns = ("gridpos", "filename", "copies")

frame_tree_container = Frame(frame_CardListTab)

tree = ttk.Treeview(
    frame_tree_container,
    columns=columns,
    show="tree headings",
    style="Card.Treeview",
    bootstyle=INFO
)

copies_entry = ttk.Entry(
    frame_CardListTab,
    width=100,
    validate="key",
    validatecommand=(vcmd_only_digits, "%P"),
    justify="center"
)
copies_entry.place_forget()

tree.heading("#0", text="Preview", anchor="center")
tree.column("#0", width=150, anchor=CENTER, stretch=False)
tree.heading("gridpos", text="Posição")
tree.heading("filename", text="Arquivo")
tree.heading("copies", text="Cópias")

tree.column("gridpos", width=80, anchor="center")
tree.column("filename", width=80, anchor="center")
tree.column("copies", width=60, anchor="center")

tree.bind("<<TreeviewSelect>>", lambda e: None)
tree.bind("<Double-1>", Start_Edit)             
tree.bind("<Button-1>", On_Tree_Click, add="+")
tree.bind("<Configure>", Show_Copies_Entry)
tree.bind("<MouseWheel>", Show_Copies_Entry)
tree.bind("<MouseWheel>", On_Scroll)

copies_entry.bind("<Return>", lambda e: Commit_Copies_Entry(move_next=True))
copies_entry.bind("<FocusOut>", lambda e: Commit_Copies_Entry(move_next=False))


frame_tree_container.pack(fill=BOTH, expand=True)


scrollbar_y = ttk.Scrollbar(
    frame_tree_container,
    orient=VERTICAL,
    command=tree.yview
)

tree.configure(yscrollcommand=scrollbar_y.set)

scrollbar_y.pack(side=RIGHT, fill=Y)
scrollbar_y.config(command=lambda *args: (tree.yview(*args), On_Scroll()))
tree.pack(side=LEFT, fill=BOTH, expand=True)

def _on_mousewheel(event):
    tree.yview_scroll(int(-1*(event.delta/240)), "units")

tree.bind_all("<MouseWheel>", _on_mousewheel)


# Botão para iniciar a geração do pdf
button_CreatePDF = Button(
    frame_CardList,
    text="Finalizar",
    command=lambda: guiFunctions.GeneratePDF(
        root,
        progress_bar,
        progress_var,
        progress_label_var,
        controls_to_disable=[
                button_LoadCards,
                button_LoadImage,
                button_RemoveImage,
                button_CreatePDF,
                comboBox_ImgInput
        ]
    )
)
button_CreatePDF.pack(side=RIGHT, pady=(20, 0))

button_CreatePDF.pack(side = RIGHT, pady=(20,0))

'''RUN STATEMENT'''
root.mainloop()