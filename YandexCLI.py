import argparse
import requests
import urllib.parse
from urllib.parse import unquote
import time
import os


class YandexDiskDownloader:
    def __init__(self, link, download_location):
        self.link = link
        self.download_location = download_location

    def download(self):
      url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
      response = requests.get(url)
      download_url = response.json()["href"]
      file_name = unquote(download_url.split("filename=")[1].split("&")[0])
      save_path = os.path.join(self.download_location, file_name)

      total_size = int(response.headers.get('content-length', 0))  # Get file size from headers (if available)
      downloaded = 0
      start_time = time.time()

      with open(save_path, "wb") as file:
         download_response = requests.get(download_url, stream=True)
         for chunk in download_response.iter_content(chunk_size=1024):
            if chunk:
               downloaded += len(chunk)
               file.write(chunk)
               file.flush()

               # Calculate and print transfer speed 
               elapsed = time.time() - start_time
               speed = downloaded / elapsed if elapsed > 0 else 0  # Avoid division by zero
               speed_unit = "KB/s"
               if speed > 1024:
                  speed /= 1024
                  speed_unit = "MB/s"
               if speed > 1024:
                  speed /= 1024
                  speed_unit = "GB/s"

               # Print progress with estimated download time (if total size unknown)
               if not total_size:  # If content-length not available
                  print(f"{speed:.2f} {speed_unit} - {downloaded / 1024**2:.2f} MB downloaded")
               else:
                  remaining = total_size - downloaded
                  remaining_unit = "KB"
                  if remaining > 1024**2:
                     remaining /= 1024**2
                     remaining_unit = "MB"
                  if remaining > 1024**3:
                     remaining /= 1024**3
                     remaining_unit = "GB"

                  # Estimate remaining time (consider potential fluctuations)
                  estimated_time = remaining / speed if speed > 0 else None
                  time_unit = "s"
                  if estimated_time and estimated_time > 60:
                     estimated_time /= 60
                     time_unit = "m"
                  if estimated_time and estimated_time > 60:
                     estimated_time /= 60
                     time_unit = "h"

                  print(f"{speed:.2f} {speed_unit} - {downloaded / 1024**2:.2f} MB of {total_size / 1024**2:.2f} MB, {remaining:.2f} {remaining_unit} remaining, {estimated_time:.2f}{time_unit} estimated")

      print("Download complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Yandex Disk Downloader')
    parser.add_argument('-l', '--link', type=str, help='Link for Yandex Disk URL', required=True)
    parser.add_argument('-d', '--download_location', type=str, help='Download location in PC', required=True)
    args = parser.parse_args()

    downloader = YandexDiskDownloader(args.link, args.download_location)
    downloader.download()
