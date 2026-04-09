import os
import tkinter
from tkinter import filedialog, IntVar, ttk
from ttkbootstrap import Combobox, Treeview
from models import Card, FileInfo
from PIL import Image, ImageTk
from jsonBuilder import build_files_json
import json
import script

card_previews = {}
cardList = {}

file_grid_map = {}  
next_card_id = 0

def ImportImageFile(combobox: Combobox, fileList: dict[str, FileInfo], image_label, selectedFileVar, selectedFileLabel):
    tkinter.Tk().withdraw() 

    filepath = filedialog.askopenfilename()

    if filepath in fileList:
        return

    filename = os.path.basename(filepath)
    fileList[filepath] = FileInfo(
        filepath=filepath,
        filename=filename
    )
    combobox['values'] = (*combobox['values'], filename)
    combobox.set(filename)

    Update_Selected_File_Label(combobox, fileList, selectedFileVar, selectedFileLabel)
    UpdateImagePreview(image_label, fileList, filename)  
      
def RemoveImageFile(combobox: Combobox, fileList: dict[str, FileInfo], image_label, selectedFileVar, selectedFileLabel, tree):
    current = combobox.get()
    if not current:
        return

    values = list(combobox["values"])
    if current not in values:
        return

    index = values.index(current)

    # Descobrir filepath
    filepath_to_remove = None
    for path, info in fileList.items():
        if info.filename == current:
            filepath_to_remove = path
            Remove_Cards_From_File(tree, filepath_to_remove)
            break

    if filepath_to_remove is None:
        return

    # Remover do dict e do combobox
    del fileList[filepath_to_remove]
    values.remove(current)
    combobox["values"] = values

    # Decidir o próximo item
    if values:
        new_index = min(index, len(values) - 1)
        next_filename = values[new_index]
        combobox.set(next_filename)
        
        Update_Selected_File_Label(combobox, fileList, selectedFileVar, selectedFileLabel)

        UpdateImagePreview(image_label, fileList, next_filename)
    else:
        combobox.set("")
        Update_Selected_File_Label(combobox, fileList, selectedFileVar, selectedFileLabel)

        ClearImagePreview(image_label)

def Update_Selected_File_Label(
    combobox,
    fileList,
    selectedFileVar,
    label
):
    if not fileList:
        selectedFileVar.set("Nenhum arquivo selecionado.")
        label.config(bootstyle="warning")
    else:
        selectedFileVar.set(combobox.get())
        label.config(bootstyle="info")

def AddCardsToList(
    combobox,
    row_var,
    col_var,
    tree,
    fileList,
    progress_bar,
    progress_var,
    progress_label_var,
    root,
    controls_to_disable
):
    filename = combobox.get()
    if not filename:
        return

    rows = row_var.get()
    cols = col_var.get()
    if rows <= 0 or cols <= 0:
        return

    filepath = next(
        (p for p, i in fileList.items() if i.filename == filename),
        None
    )
    if not filepath:
        return

    if filepath in file_grid_map:
        old_rows, old_cols = file_grid_map[filepath]

        if (rows, cols) == (old_rows, old_cols):
            return

        Remove_Cards_From_File(tree, filepath)

    Disable_Controls(controls_to_disable)

    cards = Extract_Cards_From_Grid(filepath, rows, cols)

    progress_bar.configure(bootstyle="INFO")
    progress_bar["maximum"] = len(cards)
    progress_var.set(0)
    progress_label_var.set(f"Processando carta 0 / {len(cards)}")

    file_grid_map[filepath] = {
    "grid": (rows, cols),
    "cards": []
    }   


    Insert_Cards_Step_By_Step(
        root,
        tree,
        cards,
        filepath,
        progress_bar,
        progress_var,
        progress_label_var,
        controls_to_disable,
        index=0
    )

def Insert_Cards_Step_By_Step(
    root,
    tree,
    cards,
    filepath,
    progress_bar,
    progress_var,
    progress_label_var,
    controls_to_disable,
    index
):
    global next_card_id

    total = len(cards)

    if index >= total:
        progress_label_var.set("Concluído.")
        progress_bar.configure(bootstyle="SUCCESS")
        Enable_Controls(controls_to_disable)
        return

    carta = cards[index]

    item_id = f"card_{next_card_id}"
    next_card_id += 1

    preview = Create_Card_Preview(carta.filepath, carta.bbox)
    card_previews[item_id] = preview
    cardList[item_id] = carta
    file_grid_map[filepath]["cards"].append(item_id)



    tree.insert(
        "",
        "end",
        iid=item_id,
        image=preview,
        values=(
            f"[{carta.grid_pos[0]}, {carta.grid_pos[1]}]",
            os.path.basename(filepath),
            carta.quantidade
        )
    )

    progress_var.set(index + 1)
    progress_label_var.set(
        f"Processando carta {index + 1} / {total}"
    )

    root.after(
        2,
        Insert_Cards_Step_By_Step,
        root,
        tree,
        cards,
        filepath,
        progress_bar,
        progress_var,
        progress_label_var,
        controls_to_disable,
        index + 1
    )

def Remove_Cards_From_File(tree, filepath):
    if filepath not in file_grid_map:
        return

    item_ids = file_grid_map[filepath]["cards"]

    for item_id in item_ids:
        tree.delete(item_id)
        cardList.pop(item_id, None)
        card_previews.pop(item_id, None)

    file_grid_map.pop(filepath, None)

def Add_Cards_To_Table(tree, cards):
    start_index = max(cardList.keys(), default=-1) + 1

    for offset, carta in enumerate(cards):
        item_id = start_index + offset
        preview = Create_Card_Preview(carta.filepath, carta.bbox)

        cardList[item_id] = carta
        card_previews[item_id] = preview

        tree.insert(
            "",
            "end",
            iid=item_id,
            image=preview,
            values=(
                f"[{carta.grid_pos[0]}, {carta.grid_pos[1]}]",
                os.path.basename(carta.filepath),
                carta.quantidade
            )
        )

def Create_Card_Preview(
    filepath: str,
    bbox: tuple[int, int, int, int],
    max_size: int = 130
):
    image = Image.open(filepath)
    x, y, w, h = bbox

    cropped = image.crop((x, y, x + w, y + h))

    scale = min(max_size / w, max_size / h)
    resized = cropped.resize(
        (int(w * scale), int(h * scale)),
        Image.LANCZOS
    )

    return ImageTk.PhotoImage(resized)

def UpdateImagePreview(
    image_label,
    fileList: dict[str, FileInfo],
    filename: str,
    max_size: int = 550
):
    if not filename:
        return

    # Encontrar o filepath pelo filename
    filepath = None
    for path, info in fileList.items():
        if info.filename == filename:
            filepath = path
            break

    if filepath is None:
        return

    pil_image = Image.open(filepath)

    # Redimensionar mantendo aspect ratio
    img_w, img_h = pil_image.size
    scale = min(max_size / img_w, max_size / img_h)
    new_size = (int(img_w * scale), int(img_h * scale))
    preview = pil_image.resize(new_size, Image.LANCZOS)

    tk_image = ImageTk.PhotoImage(preview)

    # Atualizar label
    image_label.config(image=tk_image)
    image_label.image = tk_image

def ClearImagePreview(image_label):
    image_label.config(
        image="",
        text="Nenhum arquivo selecionado.",
        anchor="center",
        font=("Roboto", 12, "italic"),
        bootstyle="warning"
    )
    image_label.image = None

def Set_CardAmount_Entry(tree, row_id, initial=0):
    bbox = tree.bbox(row_id, column="qty")
    if not bbox:
        return

    x, y, w, h = bbox

    var = IntVar(value=initial)
    entry = ttk.Entry(tree, textvariable=var, width=5, justify="center")
    entry.place(x=x, y=y, width=w, height=h)

    return var

def Extract_Cards_From_Grid(filepath, rows, cols):
    image = Image.open(filepath)
    img_w, img_h = image.size

    card_w = img_w // cols
    card_h = img_h // rows

    cards = []

    for r in range(rows):
        for c in range(cols):
            cards.append(
                Card(
                    grid_pos=(r, c),
                    filepath=filepath,
                    bbox=(c * card_w, r * card_h, card_w, card_h),
                    quantidade=0,
                    grid_shape=(rows, cols)
                )
            )

    return cards

def Populate_Card_List(
    tree: Treeview,
    cards: list[Card]
):
    tree.delete(*tree.get_children())
    cardList.clear()
    card_previews.clear()

    for idx, carta in enumerate(cards):
        preview = Create_Card_Preview(carta.filepath, carta.bbox)
        card_previews[idx] = preview
        cardList[idx] = carta

        tree.insert(
            "",
            "end",
            iid=idx,
            image=preview,
            values=(
                f"[{carta.grid_pos[0]}, {carta.grid_pos[1]}]",
                os.path.basename(carta.filepath),
                carta.quantidade
            )
        )

def Update_Card_Copies(item_id, value):
    if item_id not in cardList:
        return

    cardList[item_id].quantidade = value

def Disable_Controls(controls):
    for w in controls:
        w.configure(state="disabled")

def Enable_Controls(controls):
    for w in controls:
        w.configure(state="normal")

def GeneratePDF(
    root,
    progress_bar,
    progress_var,
    progress_label_var,
    controls_to_disable
):
    Disable_Controls(controls_to_disable)

    progress_bar.configure(bootstyle="INFO")
    progress_var.set(0)
    progress_label_var.set("Gerando PDF com as cartas escolhidas...")

    data = build_files_json(
        game_name="pdfexportado",
        output_path="data/exported/",
        cardList=cardList,
        file_grid_map=file_grid_map
    )

    json_path = "data/files.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    progress_cb = PDF_Progress_Callback(
        root,
        progress_bar,
        progress_var,
        progress_label_var
    )

    script.generate_from_json(json_path, progress_cb)

    Enable_Controls(controls_to_disable)

def PDF_Progress_Callback(
    root,
    progress_bar,
    progress_var,
    progress_label_var
):
    def callback(phase, current, total, message):
        progress_bar["maximum"] = max(total, 1)
        progress_var.set(current)
        progress_label_var.set(message)

        if phase == "done":
            progress_bar.configure(bootstyle="SUCCESS")
            progress_var.set(total)

        root.update_idletasks()

    return callback
