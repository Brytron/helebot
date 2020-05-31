#!C:\Users\Brytron\PycharmProjects\helebot_0.2\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'dateutils==0.6.8','console_scripts','dateadd'
__requires__ = 'dateutils==0.6.8'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('dateutils==0.6.8', 'console_scripts', 'dateadd')()
    )
