import os

# Aranacak kök klasör
root_dir = "core"

# İçeriği gösterilmeyecek klasörler
ignore_contents = {
    "cache", "media",  "ckeditor", "__pycache__", "migrations"
}

# Dosya yollarını topla
def list_files(base, prefix=""):
    paths = []
    try:
        for item in os.listdir(base):
            full_path = os.path.join(base, item)
            relative_path = os.path.join(prefix, item)

            if os.path.isdir(full_path):
                if item in ignore_contents:
                    paths.append(relative_path + "/")  # sadece klasör ismini yaz
                    continue
                # klasör içeriğini gez
                paths.extend(list_files(full_path, relative_path))
            else:
                # dosya yolu
                paths.append(relative_path)
    except PermissionError:
        pass
    return paths

# çalıştır ve dışa yaz
if __name__ == "__main__":
    result = list_files(root_dir)
    with open("sade_dosya_listesi.txt", "w", encoding="utf-8") as f:
        for line in result:
            f.write(line + "\n")
    print(f"{len(result)} dosya yolu yazıldı -> sade_dosya_listesi.txt")
