<h1 align="left">● SoundTools library</h1>

the soundtools library has some basic sound-waves which you can use to create music, and you can modify it and add you own sound-waves as well.


<h3 align="left">● installing the libraries</h3>

```shell
pip install -r REQUIREMENTS.txt
```

<h3 align="left">● creating an executable</h3>

make sure to include the tkinterdnd2 library
```shell
pip install -U pyinstaller
pyinstaller --collect-all tkinterdnd2 -F -w -i icon.ico app.py -n 'Audio Player by Erfan ;D'
```

if got errors run this command instead
```shell
pyinstaller --collect-all TkinterDnD2 -F -w -i icon.ico app.py -n 'Audio Player by Erfan ;D'
```
