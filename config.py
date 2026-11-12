"""
parametros globais do sistema de biometria, apenas :P
"""

from pathlib import Path
BASE_DIR = Path (__file__).resolve().parent
DADOS_DIR = BASE_DIR / "dados"
DB_PATH = DADOS_DIR / "cofre.db"
RELATORIOS_DIR = BASE_DIR / "relatorios"

# aquisicao de imagens #
CAMERA_INDEX = 0
#0 eh a webcam padrao :)
ESCALA = 0.5 
#reduz o frame pra acelerar o processo e 0.5 eh metade do tamanho :P
# ----- #
# segmentacao (pra detectar o rosto wtv) #
MODELO_DETECCAO = "hog"
#hog = cpu, rapido ou "cnn" = gpu, + preciso #
# classificacao #
TOLERANCIA = 0.5
FRAMES_CONFIRMACAO = 5
# cadastro #
AMOSTRAS_CADASTRO = 10
INTERVALO_AMOSTRA_S = 0.6
# seguranca extra (prova de vida sei la tanto faz) #
EXIGIR_PISCADA = True
EAR_LIMIAR = 0.21
TEMPO_LIMITE_S= 20
#exige piscada, e ai abaixo disso o olho eh considerado fechado e tb tem o tempo max pra tentar abrir o "cofre#

# niveis de acesso #
NIVEIS = {
    1: "Permissao geral",
    2: "Diretor de divisao",
    3: "Ministro do meio ambiente",
}