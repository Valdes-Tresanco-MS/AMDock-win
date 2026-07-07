@echo off
python -m venv env
call env\Scripts\activate.bat
python -m pip install ./openbabel_wheel-3.1.1.20-cp311-cp311-win_amd64.whl
pip install pandas lxml pytz XlsxWriter --no-index --find-links .
python setup.py install
python -m pip install ./pymol-3.2.0a0-cp311-cp311-win_amd64.whl --no-index --find-links .
plip
pause
