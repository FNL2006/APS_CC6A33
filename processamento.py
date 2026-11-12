"""
fases do processamento digital
1- aquisicao = adquirir_camera ()
2- pre processamento = preprocessar ()
3- segmentacao = segmentar ()
4- extracao de caracteristicas = extrair_caracteristicas ()
5- classificacao = classificar ()
(com adicional da prova de vida: razao_aspecto_olho / ear_medio)
"""

import cv2
import numpy as np
import face_recognition
import config


# aquisicao #
def adquirir_camera():
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            "Nao foi possivel abrir a camera. Verifique se ela está conectada."
        )
    return cap


## pre processamento :O ##
def preprocessar(frame_bgr):
    pequeno = cv2.resize(frame_bgr, (0, 0), fx=config.ESCALA, fy=config.ESCALA)
    lab = cv2.cvtColor(pequeno, cv2.COLOR_BGR2LAB)
    canal_l, canal_a, canal_b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    canal_l = clahe.apply(canal_l)
    melhorado = cv2.cvtColor(cv2.merge((canal_l, canal_a, canal_b)), cv2.COLOR_LAB2BGR)
    rgb = cv2.cvtColor(melhorado, cv2.COLOR_BGR2RGB)
    return np.ascontiguousarray(rgb)


## segmentacao :) ##
def segmentar(rgb):
    return face_recognition.face_locations(rgb, model=config.MODELO_DETECCAO)


def caixa_no_frame_original(local):
    return tuple(int(v / config.ESCALA) for v in local)


## extracao de caracteristicas ##
def extrair_caracteristicas(rgb, locais):
    return face_recognition.face_encodings(rgb, locais)


## classificacao ##
def classificar(encoding, matriz):
    if len(matriz) == 0:
        return None, float("inf")
    distancias = face_recognition.face_distance(matriz, encoding)
    i = int(np.argmin(distancias))
    if distancias[i] <= config.TOLERANCIA:
        return i, float(distancias[i])
    return None, float(distancias[i])


## prova de vida :^) ##
def _dist(p, q):
    return float(np.linalg.norm(np.array(p) - np.array(q)))


def razao_aspecto_olho(olho):
    return (_dist(olho[1], olho[5]) + _dist(olho[2], olho[4])) / (2.0 * _dist(olho[0], olho[3]))


def ear_medio(rgb, locais):
    pontos = face_recognition.face_landmarks(rgb, locais)
    if not pontos:
        return None
    esq = razao_aspecto_olho(pontos[0]["left_eye"])
    dir_ = razao_aspecto_olho(pontos[0]["right_eye"])
    return (esq + dir_) / 2.0