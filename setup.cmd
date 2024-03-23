echo installing the requirements
pip install -r REQUIREMENTS.txt

echo installing pyinstaller
pip install -U pyinstaller

echo creating an executable file
pyinstaller --collect-all tkinterdnd2 -F -w -i icon.ico app.py -n 'Audio Player by Erfan ;D'