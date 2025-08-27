import os
import shutil
import json
import sys

def analyze_files(root_dir, dest_dir, extensions, lookup_file="lookup.json"):
    """
    Analizuje pliki do backupu i zapisuje lookup table w JSON.
    """
    root_dir = os.path.abspath(root_dir)
    dest_dir = os.path.abspath(dest_dir)

    lookup_table = []
    total_size = 0
    total_files = 0

    for current_path, dirs, files in os.walk(root_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                src_path = os.path.join(current_path, file)
                rel_path = os.path.relpath(current_path, root_dir)
                dest_path = os.path.join(dest_dir, rel_path, file)

                try:
                    size = os.path.getsize(src_path)
                except OSError:
                    size = 0

                lookup_table.append({
                    "src": src_path,
                    "dest": dest_path,
                    "size": size
                })

                total_files += 1
                total_size += size

    # Podsumowanie
    size_mb = total_size / (1024 * 1024)
    size_gb = total_size / (1024 * 1024 * 1024)

    print(f"\n[ANALIZA ZAKOŃCZONA]")
    print(f"Znaleziono plików: {total_files}")
    print(f"Łączny rozmiar: {total_size} B  ({size_mb:.2f} MB / {size_gb:.2f} GB)")

    # Zapis lookup table do JSON
    with open(lookup_file, "w", encoding="utf-8") as f:
        json.dump(lookup_table, f, indent=4, ensure_ascii=False)

    print(f"[INFO] Lookup table zapisano do: {lookup_file}")
    return lookup_table


def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█'):
    """
    Wyświetla progress bar w konsoli.
    """
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()


def copy_files_from_lookup(lookup_file):
    """
    Kopiuje pliki na podstawie lookup table w JSON + progress bar.
    """
    with open(lookup_file, "r", encoding="utf-8") as f:
        lookup_table = json.load(f)

    total_files = len(lookup_table)
    total_size = sum(entry["size"] for entry in lookup_table)

    copied_files = 0
    copied_size = 0

    for entry in lookup_table:
        src = entry["src"]
        dest = entry["dest"]
        size = entry["size"]

        dest_dir = os.path.dirname(dest)
        os.makedirs(dest_dir, exist_ok=True)

        try:
            shutil.copy2(src, dest)
        except Exception as e:
            print(f"\n[ERROR] {src} -> {dest}: {e}")

        copied_files += 1
        copied_size += size

        # Progres wg plików i wg rozmiaru
        print_progress_bar(
            copied_files,
            total_files,
            prefix=f"Pliki {copied_files}/{total_files}",
            suffix=f"Rozmiar {copied_size/(1024*1024):.2f} MB / {total_size/(1024*1024):.2f} MB",
            length=40
        )


if __name__ == "__main__":
    # 🔧 KONFIGURACJA
    src = "H:/"   # katalog źródłowy
    dst = "G:/backup/HP"          # katalog docelowy
    lookup_file = "lookup.json" # plik JSON do zapisu/odczytu

    extensions = [
        ".txt", ".pdf", ".doc", ".docx", ".odt", ".rtf", ".tex",
        ".xls", ".xlsx", ".ods", ".csv",
        ".ppt", ".pptx", ".odp",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic",
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
        ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".mpeg",
        ".zip", ".rar", ".7z", #".tar", ".gz", ".bz2",
        #".py", ".c", ".cpp", ".java", ".js", ".html", ".css", ".json", ".xml"
    ]

    # 🔹 Najpierw analiza
    analyze_files(src, dst, extensions, lookup_file)

    # 🔹 Pytanie do użytkownika
    res = input("\nCzy chcesz teraz wykonać kopię plików? (t/n): ").strip().lower()
    if res == "t":
        copy_files_from_lookup(lookup_file)
        print("\n[KOPIOWANIE ZAKOŃCZONE]")
    else:
        print("\n[KOPIOWANIE POMINIĘTE]")
