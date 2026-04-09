import os

def build_files_json(
    game_name,
    output_path,
    cardList,
    file_grid_map
):
    card_files = []

    cards_by_file = {}
    for card in cardList.values():
        if card.quantidade <= 0:
            continue
        cards_by_file.setdefault(card.filepath, []).append(card)

    fileData = []

    for filepath, cards in cards_by_file.items():

        if filepath not in file_grid_map:
            continue

        grid_info = file_grid_map[filepath]
        rows, cols = grid_info["grid"]

        for card in cards:
            row, col = card.grid_pos
            index = row * cols + col

            fileData.append({
                "filename": filepath,          
                "card_count": [cols, rows], # COLUNAS primeiro, LINHAS depois    
                "select": [[index, index]],     
                "instances": card.quantidade,   
                "maintain_w_or_h": 1
            })

    card_files.append({
        "name": "cards",
        "rotate": False,
        "bestFit": True,
        "margin_mm": [10, 10],
        "padding_mm": [1, 1],
        "card_dim": [63, 88],
        "fileData": fileData
    })

    return {
        "game": game_name,
        "a3_pix": [3508, 4960],
        "a3_dim": [297, 420],
        "outputPath": output_path,
        "save_as_pdf": True,
        "card_files": card_files
    }
