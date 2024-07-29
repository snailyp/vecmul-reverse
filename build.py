import PyInstaller.__main__
import platform


def build_for_current_platform():
    system = platform.system().lower()
    if system == "windows":
        build_for_windows()
    elif system == "darwin":
        build_for_mac()
    elif system == "linux":
        build_for_linux()
    else:
        print(f"Unsupported platform: {system}")


def build_for_windows():
    PyInstaller.__main__.run([
        './vecmul_service.py',
        '--onefile',
        '--name=vecmul2api',
        '--add-data=.env:.',
    ])


def build_for_mac():
    PyInstaller.__main__.run([
        './vecmul_service.py',
        '--onefile',
        '--name=vecmul2api',
        '--add-data=.env:.',
    ])


def build_for_linux():
    PyInstaller.__main__.run([
        './vecmul_service.py',
        '--onefile',
        '--name=vecmul2api',
        '--add-data=.env:.',
    ])


if __name__ == "__main__":
    build_for_current_platform()
