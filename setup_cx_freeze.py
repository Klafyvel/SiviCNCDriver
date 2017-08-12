from cx_Freeze import setup, Executable
import sivicncdriver

# On appelle la fonction setup
setup(
    name = "SiviCNCDriver",
    version = sivicncdriver.__version__,
    description = 'A software to control my CNC',
    executables = [Executable("siviCNCDriver.py")],
)