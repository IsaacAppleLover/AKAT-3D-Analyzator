import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def main():
    # Aktuelles Datum und Uhrzeit abrufen
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Pfad zum neuen Ordner erstellen
    directory = os.path.join("02_Utils", "Images", "captured", timestamp)
    os.makedirs(directory, exist_ok=True)

    # Zwei Zufallsbilder erstellen, beschriften und speichern
    image_left = create_and_save_random_image(directory, "links", "links")
    image_right = create_and_save_random_image(directory, "rechts", "rechts")

    # Kombiniertes Bild erstellen und speichern
    combined_image = combine_images(image_left, image_right)
    combined_image_path = os.path.join(directory, "kombiniert.png")
    combined_image.save(combined_image_path)

    # Nachricht ausgeben
    print(f"Ordner '{directory}' wurde erstellt und Bilder wurden gespeichert. Kombiniertes Bild ist unter '{combined_image_path}' gespeichert.")

def create_and_save_random_image(directory, name, text):
    # Bildgröße definieren
    width, height = 100, 100

    # Zufallsbilddaten generieren
    image_data = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)

    # Bild erstellen
    image = Image.fromarray(image_data, 'RGB')

    # Text auf das Bild schreiben
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    text_width, text_height = draw.textsize(text, font=font)
    text_position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(text_position, text, fill="white", font=font)

    # Bildpfad erstellen
    image_path = os.path.join(directory, f"{name}.png")

    # Bild speichern
    image.save(image_path)

    return image

def combine_images(image_left, image_right):
    # Höhe und Breite der einzelnen Bilder
    width_left, height_left = image_left.size
    width_right, height_right = image_right.size

    # Neue Bildgröße für das kombinierte Bild
    combined_width = width_left + width_right
    combined_height = max(height_left, height_right)

    # Neues leeres Bild mit kombinierter Breite und maximaler Höhe
    combined_image = Image.new("RGB", (combined_width, combined_height))

    # Bilder einfügen
    combined_image.paste(image_left, (0, 0))
    combined_image.paste(image_right, (width_left, 0))

    return combined_image

if __name__ == "__main__":
    main()
