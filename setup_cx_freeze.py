from cx_Freeze import setup, Executable
import sivicncdriver

# On appelle la fonction setup
addtional_mods = ['numpy.core._methods', 'numpy.lib.format']
setup(
    name = "SiviCNCDriver",
    version = sivicncdriver.__version__,
    description = 'A software to control my CNC',
    executables = [Executable("siviCNCDriver.py")],
    options = {'build_exe': {
    	'includes': addtional_mods,
    	'namespace_packages' : ['mpl_toolkits'],
    }},
)