import os
import subprocess

CWD = os.getcwd()

class Playlist():
    def __init__(self, playlist_url) -> None:
        self.playlist_url = playlist_url

        self._META_DIR = os.path.join(CWD, 'meta')
        self._MUSIC_DIR = os.path.join(CWD, 'Music')

        self._META_FILENAME_TEMPLATE = os.path.join(self._META_DIR, '%(playlist)s', '%(title)s')
        self._MUSIC_FILEMAME_TEMPLATE = os.path.join(self._MUSIC_DIR, '%(playlist)s', '[%(upload_date)s] %(title)s')
        
        if not os.path.isdir(self._MUSIC_DIR):
            os.mkdir(self._MUSIC_DIR)

        self.download_metas()
    
    def download_metas(self):
        subprocess.run([
            'yt-dlp',
            '--skip-download', 
            '--write-info-json',
            '--no-write-playlist-metafiles',
            '-o', self._META_FILENAME_TEMPLATE,
            self.playlist_url
        ])
    

    def download(self, meta_path):
        # Renew download url
        subprocess.run([
            'yt-dlp',
            '--skip-download',
            '--load-info-json', meta_path,
            '--write-info-json',
            '-o', self._META_FILENAME_TEMPLATE
        ])

        result = subprocess.run([
            'yt-dlp',
            '--load-info-json', meta_path,
            '-f', '251',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '128k',
            '--embed-thumbnail',
            '--embed-metadata',
            '--convert-thumbnail', 'jpg',
            '--ppa', 'ExtractAudio+ffmpeg_o:-filter:a loudnorm',
            '--ppa', '''EmbedThumbnail+ffmpeg_o:-c:v mjpeg -vf crop=\"'if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)',scale=\"-1:1080\"\"''',
            '-o', self._MUSIC_FILEMAME_TEMPLATE,
        ])

        if result.returncode == 0:
            os.remove(meta_path)
        
        return


    def download_all(self):
        if not os.path.isdir(self._META_DIR):
            return
        
        for dirpath, dirnames, filenames in os.walk(self._META_DIR):
            if filenames == []:
                continue

            for filename in filenames:
                if not filename.endswith('.info.json'):
                    continue
                self.download(meta_path=os.path.join(dirpath, filename))
        
        while True:
            for dirpath, dirnames, filenames in os.walk(self._META_DIR, topdown=False):
                if dirnames + filenames == []:
                    os.rmdir(dirpath)
                    break

            if os.listdir(self._META_DIR) == []:
                os.rmdir(self._META_DIR)
            
            break
    

def main():
    try:
        user_input = input("Enter a playlist url to donwload or 'update' to update or Ctrl-c to exit: ")
    except KeyboardInterrupt:
        ...

    if user_input == "update":
        ...
    else:
        playlist = Playlist(user_input)
        playlist.download_all()
        return main()


if __name__ == "__main__":
    main()