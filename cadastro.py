"""
cadastro de um novo usuario pela webcam. Captura varias amostras do rosto, incluindo angulos
e expressoes, p/ deixar o reconhecimento + robusto, e dai grava os encodings no banco de dados
"""
import time
import traceback

import cv2

import banco
import config
import processamento as proc

NOME_JANELA = "Cadastro"


def cadastrar_pela_camera(nome, cargo, nivel):
    cap = proc.adquirir_camera()
    amostras = []
    ultimo = 0.0

    try:
        # abre a janela e tenta deixá-la na frente (se o OpenCV não suportar, segue sem isso)
        cv2.namedWindow(NOME_JANELA)
        try:
            cv2.setWindowProperty(NOME_JANELA, cv2.WND_PROP_TOPMOST, 1)
        except cv2.error:
            pass

        # descarta os primeiros frames (a câmera ainda está ajustando a luz)
        for _ in range(5):
            cap.read()

        while len(amostras) < config.AMOSTRAS_CADASTRO:
            ok, frame = cap.read()
            if not ok or frame is None:
                raise RuntimeError("Falha ao ler imagem da câmera.")

            rgb = proc.preprocessar(frame)
            locais = proc.segmentar(rgb)

            msg = f"Amostras: {len(amostras)}/{config.AMOSTRAS_CADASTRO} (q = cancelar)"
            cor = (0, 255, 255)

            if len(locais) == 0:
                msg = "Nenhum rosto encontrado."
                cor = (0, 0, 255)
            elif len(locais) > 1:
                msg = "Apenas UMA pessoa no cadastro"
                cor = (0, 0, 255)
            else:
                top, right, bottom, left = proc.caixa_no_frame_original(locais[0])
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                agora = time.time()
                if agora - ultimo >= config.INTERVALO_AMOSTRA_S:
                    enc = proc.extrair_caracteristicas(rgb, locais)[0]
                    amostras.append(enc)
                    ultimo = agora
                    print(f"  amostra {len(amostras)}/{config.AMOSTRAS_CADASTRO} capturada")

            cv2.putText(frame, msg, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)
            cv2.imshow(NOME_JANELA, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Cadastro cancelado.")
                return None

    except Exception:
        # mostra o erro completo (arquivo, linha e motivo) em vez de esconder
        print("\n*** ERRO DURANTE A CAPTURA ***")
        traceback.print_exc()
        return None
    finally:
        cap.release()
        cv2.destroyAllWindows()

    # salvar no banco (fora do try acima para o erro do banco aparecer separado)
    try:
        uid = banco.cadastrar_usuario(nome, cargo, nivel, amostras)
    except Exception:
        print("\n*** ERRO AO SALVAR NO BANCO ***")
        traceback.print_exc()
        return None

    print(f"Usuário '{nome}' cadastrado (id {uid}, nível {nivel}) com {len(amostras)} amostras.")
    return uid