the soundtools library has some basic sound-waves which you can use to create music, and you can modify it and add you own sound-waves as well.

install the libraries
```shell
pip install -r REQUIREMENTS.txt
```

to make an executable you can use pyinstaller, but you have to include the "tkinterdnd2" package.
```shell
pip install -U pyinstaller
pyinstaller --collect-all tkinterdnd2 -F -w -i icon.ico app.py -n 'Audio Player by Erfan ;D'
```

if got errors run this command instead
```shell
pyinstaller --collect-all TkinterDnD2 -F -w -i icon.ico app.py -n 'Audio Player by Erfan ;D'
```
or just run the setup file
