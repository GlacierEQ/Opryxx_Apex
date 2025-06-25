import os
import shutil
from datetime import datetime

def organize_files(directory):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    document_extensions = ['.doc', '.docx', '.pdf', '.txt', '.rtf']
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
    music_extensions = ['.mp3', '.wav', '.flac', '.aac']
    archive_extensions = ['.zip', '.rar', '.7z']
    software_extensions = ['.exe', '.msi', '.pkg']
    
    os.makedirs(os.path.join(directory, 'Images'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'Documents'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'Videos'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'Music'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'Archives'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'Software'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'Others'), exist_ok=True)
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_extension = os.path.splitext(filename)[1].lower()
            try:
                if file_extension in image_extensions:
                    shutil.move(filepath, os.path.join(directory, 'Images', filename))
                elif file_extension in document_extensions:
                    shutil.move(filepath, os.path.join(directory, 'Documents', filename))
                elif file_extension in video_extensions:
                    shutil.move(filepath, os.path.join(directory, 'Videos', filename))
                elif file_extension in music_extensions:
                    shutil.move(filepath, os.path.join(directory, 'Music', filename))
                elif file_extension in archive_extensions:
                    shutil.move(filepath, os.path.join(directory, 'Archives', filename))
                elif file_extension in software_extensions:
                    shutil.move(filepath, os.path.join(directory, 'Software', filename))
                else:
                    shutil.move(filepath, os.path.join(directory, 'Others', filename))
                print(f"Moved {filename} to appropriate folder")
            except Exception as e:
                print(f"Error moving {filename}: {e}")

if __name__ == "__main__":
    downloads_dir = os.path.join(os.environ['USERPROFILE'], 'Downloads')
    organize_files(downloads_dir)
