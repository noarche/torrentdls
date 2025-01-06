import libtorrent as lt
import time
import os
from colorama import Fore, Style, init

# Initialize colorama
init()

def main():
    # Directory for torrent downloads
    download_dir = 'torrentdls'
    os.makedirs(download_dir, exist_ok=True)
    
    # User input for magnet link
    print(Fore.CYAN + "Enter the magnet link for the torrent:" + Style.RESET_ALL)
    magnet_link = input(Fore.YELLOW + "Magnet Link: " + Style.RESET_ALL).strip()

    # Libtorrent session setup
    session = lt.session()
    session.listen_on(6881, 6891)
    params = {
        'save_path': download_dir,
        'storage_mode': lt.storage_mode_t.storage_mode_sparse
    }

    # Add torrent to session using `add_torrent_params`
    print(Fore.GREEN + "Adding torrent..." + Style.RESET_ALL)
    atp = lt.parse_magnet_uri(magnet_link)
    atp.save_path = download_dir
    handle = session.add_torrent(atp)
    print(Fore.GREEN + "Torrent added! Downloading..." + Style.RESET_ALL)

    # Wait until metadata is downloaded
    print(Fore.YELLOW + "Downloading metadata..." + Style.RESET_ALL)
    while handle.status().state == lt.torrent_status.downloading_metadata:
        time.sleep(1)

    print(Fore.GREEN + "Metadata retrieved. Starting download..." + Style.RESET_ALL)

    # Display download/upload stats
    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        print(
            Fore.CYAN + f"\rDownloading: {s.progress * 100:.2f}% "
            f"| D: {s.download_rate / 1024:.2f} kB/s "
            f"| U: {s.upload_rate / 1024:.2f} kB/s "
            f"| D Total: {s.total_done / (1024 * 1024):.2f} MB "
            f"| U Total: {s.total_upload / (1024 * 1024):.2f} MB "
            f"| Ratio: {s.total_upload / s.total_done if s.total_done > 0 else 0:.2f}",
            end='', flush=True
        )
        time.sleep(1)

    print(Fore.GREEN + "\nDownload complete! Seeding now..." + Style.RESET_ALL)

    # Keep seeding until manually stopped
    try:
        while True:
            s = handle.status()
            print(
                Fore.CYAN + f"\rSeeding: "
                f"| U: {s.upload_rate / 1024:.2f} kB/s "
                f"| U Total: {s.total_upload / (1024 * 1024):.2f} MB "
                f"| Ratio: {s.total_upload / s.total_done if s.total_done > 0 else 0:.2f}",
                end='', flush=True
            )
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "\nSeeding stopped by user." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
