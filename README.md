the soundtools library has some basic sound-waves which you can use to create music, and you can modify it and add you own sound-waves as well.

install the libraries
```shell
pip install -r REQUIREMENTS.txt
```

import it in your python file
```python
from soundtools import soundtools
```

to make an executable you can use pyinstaller but you have to include the tkinterdnd2 package
or just run the setup file
```shell
pyinstaller --collect-all tkinterdnd2 -F -w -i icon.ico app.py -n 'Media Player by Erfan ;D'
```