import libtorrent as lt
import time
import os
import json
import threading
from colorama import Fore, Style, init

# Initialize colorama
init()

# Set the save path for torrent downloads
SAVE_PATH = 'torrentdls'
os.makedirs(SAVE_PATH, exist_ok=True)

MAGNETS_FILE = 'magnets.json'
download_threads = []


def load_magnets():
    """Load magnets from the magnets.json file."""
    if not os.path.exists(MAGNETS_FILE):
        return []
    with open(MAGNETS_FILE, 'r') as f:
        return json.load(f)


def save_magnets(magnets):
    """Save magnets to the magnets.json file."""
    with open(MAGNETS_FILE, 'w') as f:
        json.dump(magnets, f, indent=4)


def download_and_seed(magnet_link, index):
    """
    Download a torrent and automatically start seeding it.
    This runs in a separate thread for each torrent.
    """
    session = lt.session()
    session.listen_on(6881, 6891)

    print(Fore.GREEN + f"[Torrent {index}] Starting download..." + Style.RESET_ALL)
    atp = lt.parse_magnet_uri(magnet_link)
    atp.save_path = SAVE_PATH
    handle = session.add_torrent(atp)

    # Wait until metadata is downloaded
    while handle.status().state == lt.torrent_status.downloading_metadata:
        print(Fore.YELLOW + f"[Torrent {index}] Downloading metadata..." + Style.RESET_ALL)
        time.sleep(1)

    print(Fore.GREEN + f"[Torrent {index}] Metadata retrieved. Starting download..." + Style.RESET_ALL)

    # Download the torrent
    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        print(
            Fore.CYAN +
            f"[Torrent {index}] Downloading: {s.progress * 100:.2f}% "
            f"| D: {s.download_rate / 1024:.2f} kB/s "
            f"| U: {s.upload_rate / 1024:.2f} kB/s "
            f"| D Total: {s.total_done / (1024 * 1024):.2f} MB ",
            end='\r', flush=True
        )
        time.sleep(1)

    print(Fore.GREEN + f"\n[Torrent {index}] Download complete. Seeding now..." + Style.RESET_ALL)

    # Seed the torrent
    while True:
        s = handle.status()
        print(
            Fore.CYAN +
            f"[Torrent {index}] Seeding: "
            f"| U: {s.upload_rate / 1024:.2f} kB/s "
            f"| U Total: {s.total_upload / (1024 * 1024):.2f} MB ",
            end='\r', flush=True
        )
        time.sleep(1)


def manage_magnets():
    """View, add, and delete magnets from magnets.json."""
    while True:
        magnets = load_magnets()
        print(Fore.BLUE + "\nManage Magnets Menu:" + Style.RESET_ALL)
        print("1. View Magnets")
        print("2. Add Magnet")
        print("3. Delete Magnet")
        print("4. Go Back")

        choice = input(Fore.YELLOW + "Enter your choice: " + Style.RESET_ALL)

        if choice == '1':
            if not magnets:
                print(Fore.RED + "No magnets saved yet." + Style.RESET_ALL)
            else:
                print(Fore.CYAN + "Saved magnets:" + Style.RESET_ALL)
                for idx, magnet in enumerate(magnets, start=1):
                    print(f"{idx}. {magnet}")

        elif choice == '2':
            magnet_link = input(Fore.CYAN + "Enter the magnet link to add: " + Style.RESET_ALL).strip()
            if magnet_link:
                if magnet_link not in magnets:
                    magnets.append(magnet_link)
                    save_magnets(magnets)
                    print(Fore.GREEN + "Magnet link added!" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "Magnet link already exists." + Style.RESET_ALL)

        elif choice == '3':
            if not magnets:
                print(Fore.RED + "No magnets saved to delete." + Style.RESET_ALL)
            else:
                print(Fore.CYAN + "Saved magnets:" + Style.RESET_ALL)
                for idx, magnet in enumerate(magnets, start=1):
                    print(f"{idx}. {magnet}")

                choice = input(Fore.YELLOW + "\nEnter the number of the magnet to delete (or press Enter to go back): " + Style.RESET_ALL)
                if choice.strip().isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(magnets):
                        deleted = magnets.pop(idx)
                        save_magnets(magnets)
                        print(Fore.RED + f"Deleted magnet: {deleted}" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)

        elif choice == '4':
            break

        else:
            print(Fore.RED + "Invalid choice! Please try again." + Style.RESET_ALL)


def download_all_magnets():
    """Download and seed all magnets from the magnets.json file."""
    magnets = load_magnets()
    if not magnets:
        print(Fore.RED + "No magnets saved to download." + Style.RESET_ALL)
        return

    for idx, magnet_link in enumerate(magnets, start=1):
        thread = threading.Thread(target=download_and_seed, args=(magnet_link, idx))
        thread.start()
        download_threads.append(thread)

    # Wait for all threads to complete
    for thread in download_threads:
        thread.join()


def main():
    """Main menu."""
    while True:
        print(Fore.BLUE + "\nTorrent Manager Menu:" + Style.RESET_ALL)
        print("1. Download All Torrents (with Seeding)")
        print("2. Manage Magnets")
        print("3. Exit")

        choice = input(Fore.YELLOW + "Enter your choice: " + Style.RESET_ALL)
        if choice == '1':
            download_all_magnets()
        elif choice == '2':
            manage_magnets()
        elif choice == '3':
            print(Fore.GREEN + "Goodbye!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Invalid choice! Please try again." + Style.RESET_ALL)


if __name__ == "__main__":
    main()
