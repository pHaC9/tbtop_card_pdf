from PIL import Image
import json

import resize
import resize_a3
import crop_cards
import composite
import pdf_finish


def generate_from_json(json_path, progress_cb=None):
    with open(json_path) as f:
        data = json.load(f)

    card_files = data['card_files']
    pdf_pages = []

    total_steps = 0
    for group in card_files:
        for cdata in group['fileData']:
            instances = int(cdata.get("instances", 1))
            total_steps += instances
        total_steps += 1 

    current_step = 0

    def step(message):
        nonlocal current_step
        current_step += 1
        if progress_cb:
            progress_cb(
                phase="working",
                current=current_step,
                total=total_steps,
                message=message
            )

    for group in card_files:
        cards = []

        if progress_cb:
            progress_cb(
                phase="group",
                current=current_step,
                total=total_steps,
                message=f"Grupo: {group['name']}"
            )

        for cdata in group['fileData']:
            im = Image.open(cdata['filename'])
            
            print(f'Tamanho original: {im.size}')

            im = resize.resize(
                im,
                cdata['card_count'],
                group['card_dim'],
                cdata['maintain_w_or_h']
            )

            im = resize_a3.resize_a3(
                im,
                cdata['card_count'],
                group['card_dim'],
                data['a3_dim'],
                data['a3_pix']
            )
            
            print("esperado por carta:",
                im.size[0] / cdata['card_count'][0],
                im.size[1] / cdata['card_count'][1])

            cropped_cards = crop_cards.crop_cards(
                im,
                cdata['card_count'],
                group['card_dim'],
                data['a3_dim'],
                data['a3_pix']
            )

            selected_cards = []
            if 'select' in cdata:
                for start_ix, end_ix in cdata['select']:
                    selected_cards.extend(
                        cropped_cards[start_ix:end_ix + 1]
                    )
            else:
                selected_cards.extend(cropped_cards)

            instances = int(cdata.get('instances', 1))
            for i in range(instances):
                cards.extend(selected_cards)
                step(f"Preparando cartas ({current_step}/{total_steps})")

        images = composite.composite(
            cards,
            group['card_dim'],
            data['a3_dim'],
            data['a3_pix'],
            group['margin_mm'],
            group['padding_mm'],
            group['rotate'],
            group['bestFit']
        )

        pdf_pages.extend(images)
        step("Compondo página A3")

    if data['save_as_pdf']:
        step("Gerando PDF...")
        pdf_filename = data['outputPath'] + data['game'] + ".pdf"
        pdf_finish.save_images_as_pdf(pdf_pages, pdf_filename)

    if progress_cb:
        progress_cb(
            phase="done",
            current=total_steps,
            total=total_steps,
            message="PDF gerado com sucesso!"
        )


if __name__ == "__main__":
    generate_from_json("data/files_generated.json")