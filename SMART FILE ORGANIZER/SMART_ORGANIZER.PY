import os
import shutil
import logging
from pathlib import Path

# --- Activity Logging Setup ---
# Ye program ke har action ko ek .log file mein save karega
logging.basicConfig(
    filename='organizer_activity.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- File Type Categories ---
CATEGORY_MAP = {
    "Images": ['.jpg', '.jpeg', '.png', '.gif', '.svg'],
    "Documents": ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.csv', '.pptx'],
    "Videos": ['.mp4', '.mkv', '.avi', '.mov'],
    "Audio": ['.mp3', '.wav', '.aac'],
    "Archives": ['.zip', '.rar', '.tar', '.gz'],
    "Code": ['.py', '.html', '.css', '.js', '.json']
}

def get_category(extension):
    for category, extensions in CATEGORY_MAP.items():
        if extension.lower() in extensions:
            return category
    return "Others"

def organize_files(target_dir):
    # pathlib ka Path object modern aur asaan tarika hai paths handle karne ka
    folder_path = Path(target_dir)
    
    if not folder_path.exists() or not folder_path.is_dir():
        print("❌ Invalid directory path! Please check the path and try again.")
        return

    print(f"📂 Scanning directory: {folder_path}...")
    moved_count = 0

    # Folder ke andar mojood har file ko check karna
    for file_path in folder_path.iterdir():
        # Directories (folders) aur hidden files ko ignore karein
        if file_path.is_dir() or file_path.name.startswith('.'):
            continue

        # File ki extension nikalna (e.g., '.jpg')
        extension = file_path.suffix
        if not extension:
            continue

        # File type detect karna aur target folder decide karna
        category = get_category(extension)
        target_folder = folder_path / category

        # Automatic Folder Creation
        if not target_folder.exists():
            target_folder.mkdir()
            logging.info(f"Created new folder: {category}")

        # Duplicate Detection & Rename Conflicting Files
        dest_file_path = target_folder / file_path.name
        counter = 1
        while dest_file_path.exists():
            # Agar file pehle se hai, to naam ke aage _1, _2 laga dega (e.g., file_1.jpg)
            new_name = f"{file_path.stem}_{counter}{file_path.suffix}"
            dest_file_path = target_folder / new_name
            counter += 1

        # File ko move karna
        try:
            shutil.move(str(file_path), str(dest_file_path))
            logging.info(f"Moved: {file_path.name} -> {category}/{dest_file_path.name}")
            moved_count += 1
        except Exception as e:
            logging.error(f"Error moving {file_path.name}: {e}")

    print(f"✅ Organization complete! Successfully moved {moved_count} files.")
    print("📝 Check 'organizer_activity.log' for a detailed history of changes.")

if __name__ == "__main__":
    print("=== 🛠️ Smart File Organizer ===")
    print("Example path: C:\\Users\\YourName\\Downloads  OR  /Users/YourName/Downloads")
    target_directory = input("Enter the path of the messy folder you want to organize: ")
    organize_files(target_directory)