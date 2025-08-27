import os
import sys
import time
import shutil
import random

def get_free_space_bytes(path):
    """Zwraca wolną przestrzeń na dysku (w bajtach) — działa na Windows i Linux"""
    total, used, free = shutil.disk_usage(path)
    return free

def generate_payload(byte_value, size):
    """Generuje bufor danych: losowy lub o stałej wartości"""
    if byte_value is None:
        return os.urandom(size)
    return bytes([byte_value]) * size

def format_time(seconds):
    """Formatuje czas w sekundach jako hh:mm:ss"""
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def write_file_with_progress(file_path, size_bytes, byte_value):
    """Zapisuje plik z paskiem postępu i ETA, zwraca liczbę zapisanych bajtów"""
    chunk_size = 1 * 1024 * 1024  # 1 MB
    total_chunks = size_bytes // chunk_size

    with open(file_path, 'wb') as f:
        start_time = time.time()
        for i in range(total_chunks):
            payload = generate_payload(byte_value, chunk_size)
            f.write(payload)

            # Local progress bar
            percent = (i + 1) / total_chunks
            bar_length = 30
            filled = int(bar_length * percent)
            bar = '█' * filled + '-' * (bar_length - filled)

            elapsed = time.time() - start_time
            speed = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (total_chunks - i - 1) / speed if speed > 0 else 0

            sys.stdout.write(f"\r📄 LOCAL : [{bar}] {percent * 100:5.1f}% | ETA: {format_time(remaining)} ")
            sys.stdout.flush()

    print()  # nowa linia po zakończeniu lokalnego paska
    return size_bytes

def create_fill_files(target_dir, pattern_name, byte_value):
    """Tworzy pliki nadpisujące cały dysk i pokazuje postęp globalny + lokalny"""
    file_index = 0
    file_sizes = [
        1024 * 1024 * 1024,  # 1 GB
        512 * 1024 * 1024,
        256 * 1024 * 1024,
        128 * 1024 * 1024,
        64 * 1024 * 1024,
        32 * 1024 * 1024,
        16 * 1024 * 1024,
        8 * 1024 * 1024,
        4 * 1024 * 1024,
        2 * 1024 * 1024,
        1 * 1024 * 1024       # minimalny: 1 MB
    ]

    created_files = []

    total_space = get_free_space_bytes(target_dir)
    written_total = 0
    global_start = time.time()

    print(f"\n🔁 Rozpoczynam przebieg: {pattern_name}")

    try:
        for size in file_sizes:
            while get_free_space_bytes(target_dir) > size + 10 * 1024 * 1024:
                file_path = os.path.join(target_dir, f"{pattern_name}_{file_index:04d}.bin")
                print(f"\n[+] Tworzenie: {file_path} ({size // (1024*1024)} MB)")

                try:
                    written = write_file_with_progress(file_path, size, byte_value)
                    written_total += written
                    created_files.append(file_path)
                    file_index += 1

                    # GLOBAL progress bar
                    percent = written_total / total_space if total_space > 0 else 1.0
                    bar_length = 40
                    filled = int(bar_length * percent)
                    bar = '█' * filled + '-' * (bar_length - filled)
                    elapsed = time.time() - global_start
                    speed = written_total / elapsed if elapsed > 0 else 0
                    remaining = (total_space - written_total) / speed if speed > 0 else 0

                    sys.stdout.write(f"\r🌍 GLOBAL: [{bar}] {percent*100:5.1f}% | ETA: {format_time(remaining)} ")
                    sys.stdout.flush()

                except Exception as e:
                    print(f"\n⚠️  Błąd zapisu: {e}")
                    break
    except KeyboardInterrupt:
        print("\n⛔ Przerwano przez użytkownika.")

    print("\n🧹 Usuwanie plików z tego przebiegu...")
    for fpath in created_files:
        try:
            os.remove(fpath)
            print(f"[-] Usunięto: {fpath}")
        except Exception as e:
            print(f"❌ Błąd przy usuwaniu {fpath}: {e}")

def main():
    print("=== BEZPIECZNE NADPISYWANIE WOLNEJ PRZESTRZENI DYSKOWEJ ===\n")
    target_dir = input("📁 Podaj folder docelowy (na dysku, który chcesz wyczyścić): ").strip()

    if not os.path.exists(target_dir):
        print("❌ Ścieżka nie istnieje.")
        return

    if not os.path.isdir(target_dir):
        print("❌ To nie jest katalog.")
        return

    print(f"\n🔐 Rozpoczynam nadpisywanie wolnej przestrzeni w: {target_dir}")

    # Wzorce przebiegów
    patterns = [
        ("pass1_AA", 0xAA),
        ("pass2_55", 0x55),
        ("pass3_rand", None)
    ]

    for pattern_name, byte_value in patterns:
        create_fill_files(target_dir, pattern_name, byte_value)

    print("\n✅ GOTOWE! Wolna przestrzeń została nadpisana trzema przebiegami.")
    print("💡 Rekomendacja: uruchom ponownie system, by zwolnić wszystkie buffery i cache.")

if __name__ == "__main__":
    main()
