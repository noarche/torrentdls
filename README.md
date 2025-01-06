# torrentdls

Download and seed torrent in terminal. 

Very simple script quickly written. Might update with more features later but this gets the job done. 

![Screenshot 2025-01-06 052743](https://github.com/user-attachments/assets/bd3d83af-0bc7-4417-b330-075a6222a261)

### Install libtorrent 
`sudo apt install python3-libtorrent`

### Downloading

Run the script and enter magnet link. Files are saved in a directory `./torrentdls` that is created in the root dir of the script. 

### Seeding

The script automatically starts seeding after downloading. If you enter the magnet link to a torrent you have already downloaded it will check the files and start seeding as normal. 


