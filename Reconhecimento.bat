@echo off
set PYTHONUTF8=1
chcp 65001 >nul
cd /d "%~dp0"

:: Verifica se o ambiente virtual já existe
if exist venv\Scripts\activate.bat goto ativar

echo Criando o ambiente virtual pela primeira vez...
python -m venv venv
if errorlevel 1 goto erro_python
call venv\Scripts\activate.bat

echo.
echo Instalando todas as dependencias e a interface grafica...
python -m pip install --upgrade pip
pip install "setuptools<82" numpy opencv-python Pillow Click customtkinter
if errorlevel 1 goto erro_pip
pip install dlib-bin
if errorlevel 1 goto erro_pip
pip install face_recognition_models
pip install face_recognition --no-deps
if errorlevel 1 goto erro_pip
goto rodar

:ativar
call venv\Scripts\activate.bat

:rodar
echo Iniciando o sistema com Interface Grafica...
python main.py
pause
exit /b

:erro_python
echo.
echo Nao encontrei o Python instalado no sistema.
echo Instale o Python em python.org marcando a opcao "Add python.exe to PATH".
pause
exit /b 1

:erro_pip
echo.
echo Ocorreu um erro ao instalar as bibliotecas.
pause
exit /b 1