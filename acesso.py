"""
autenticacao em tempo real pra abrir o "cofre"
tem uma regra de permissao que eh: acesso liberado se nivel do usuario >= nivel da porta, e o nivel
3 tem exclusividade do ministro. 
"""

import time
from collections import deque
import cv2
import banco
import config 
import processamento as proc 

def _pode_acessar(nivel_usuario, nivel_porta):
    if nivel_porta == 3:
        return nivel_usuario == 3
    return nivel_usuario >= nivel_porta


def desenhar(frame, local, texto, cor):
    top, right, bottom, left = proc.caixa_no_frame_original(local)
    cv2.rectangle(frame, (left, top), (right, bottom), cor, 2)
    cv2.putText(frame, texto, (left, max(bottom + 25, 25)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)


def verificar_acesso(nivel_porta):
    infos, matriz = banco.carregar_base()
    if len(infos) == 0:
        raise RuntimeError("Nenhum usuario cadastrado :// cadastre alguem primeiro!")

    cap = proc.adquirir_camera()
    janela = deque(maxlen=config.FRAMES_CONFIRMACAO)
    piscou = not config.EXIGIR_PISCADA
    olho_fechado = False
    inicio = time.time()

    concedido, nome, nivel_usuario, motivo = False, "Desconhecido", 0, "Tempo esgotado"
    try:
        while True:
            if time.time() - inicio > config.TEMPO_LIMITE_S:
                break
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError("falha ao ler imagem da camera !")
            rgb = proc.preprocessar(frame)
            locais = proc.segmentar(rgb)
            msg, cor = f"Aproxime o rosto (porta nivel {nivel_porta})", (0, 255, 255)

            if len(locais) == 0:
                janela.clear()
            elif len(locais) > 1:
                janela.clear()
                msg, cor = "Mais de uma pessoa: uma de cada vez.", (0, 0, 255)
                for rosto in locais:
                    desenhar(frame, rosto, "", cor)
            else:
                local = locais[0]
                enc = proc.extrair_caracteristicas(rgb, [local])[0]
                idx, dist = proc.classificar(enc, matriz)
                janela.append(idx if idx is None else infos[idx]["id"])

                if config.EXIGIR_PISCADA and not piscou:
                    ear = proc.ear_medio(rgb, [local])
                    if ear is not None:
                        if ear < config.EAR_LIMIAR:
                            olho_fechado = True
                        elif olho_fechado:
                            piscou = True

                desenhar(frame, local, "analisando...", (255, 200, 0))

                if len(janela) == janela.maxlen and len(set(janela)) == 1:
                    if idx is None:
                        nome, nivel_usuario = "Desconhecido", 0
                        concedido, motivo = False, "Rosto não cadastrado"
                        desenhar(frame, local, "NEGADO - desconhecido", (0, 0, 255))
                        break
                    if not piscou:
                        msg, cor = "Pisque para confirmar que voce e real", (0, 165, 255)
                    else:
                        nome, nivel_usuario = infos[idx]["nome"], infos[idx]["nivel"]
                        if _pode_acessar(nivel_usuario, nivel_porta):
                            concedido, motivo = True, "Acesso autorizado"
                            desenhar(frame, local, f"LIBERADO - {nome}", (0, 255, 0))
                        else:
                            concedido = False
                            motivo = f"Nível {nivel_usuario} insuficiente para porta {nivel_porta}"
                            desenhar(frame, local, f"NEGADO - {nome} (nivel {nivel_usuario})", (0, 0, 255))
                        break

            cv2.putText(frame, msg, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)
            cv2.imshow("Cofre - autenticacao (q = sair)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                motivo = "Cancelado pelo usuário"
                break

        # mostra o resultado final por 2 segundos
        if motivo != "Cancelado pelo usuário" and motivo != "Tempo esgotado":
            cv2.imshow("Cofre - autenticacao (q = sair)", frame)
            cv2.waitKey(2000)
    finally:
        cap.release()
        cv2.destroyAllWindows()

    banco.registrar_acesso(nome, nivel_usuario, nivel_porta,
                           "CONCEDIDO" if concedido else "NEGADO", motivo)
    return concedido, nome, motivo