import os
import subprocess


def emf_to_png(emf_path: str, output_dir="extracted_images") -> str:
    """
    Конвертирует EMF в PNG с помощью ImageMagick (magick).
    Возвращает путь к PNG-файлу.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    png_path = os.path.join(
        output_dir,
        os.path.splitext(os.path.basename(emf_path))[0] + ".png"
    )

    # Вызов ImageMagick
    subprocess.run(["magick", emf_path, png_path], check=True)

    return png_path
