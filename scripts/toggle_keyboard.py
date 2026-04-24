from PIL import Image, ImageOps

import scripts.toast as toast

def get_disabled_icon(icon):
    img = icon.convert("RGBA")
    
    r, g, b, a = img.split()
    
    grayscale = ImageOps.grayscale(img)
    
    disabled_img = Image.merge("RGBA", (grayscale, grayscale, grayscale, a))
    
    return disabled_img

def toggle_phonetic_keyboard(toggle_phonemes, icon, system_tray) -> None:
    toggle_phonemes = not toggle_phonemes
    if (toggle_phonemes):
        toast.show_toast("Phonetic keyboard enabled.")
        system_tray.icon = icon
        return True
    else:
        toast.show_toast("Phonetic keyboard disabled.")
        system_tray.icon = get_disabled_icon(icon)
        return False