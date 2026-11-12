"""
relatorio.py - relatórios extras: CSV com todos os acessos, resumo em txt
e salvamento das imagens de cada fase do processamento (dissertação)
"""
import csv
from collections import Counter
from datetime import datetime

import cv2

import banco
import config
import processamento as proc


def gerar_relatorio_acessos():
    acessos = banco.listar_acessos()
    config.RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")

    caminho_csv = config.RELATORIOS_DIR / f"acessos_{carimbo}.csv"
    with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["data_hora", "nome", "nivel_usuario", "nivel_porta", "resultado", "motivo"])
        w.writerows(acessos)

    total = len(acessos)
    concedidos = sum(1 for a in acessos if a[4] == "CONCEDIDO")
    negados = total - concedidos
    desconhecidos = sum(1 for a in acessos if a[1] == "Desconhecido")
    por_usuario = Counter(a[1] for a in acessos if a[4] == "CONCEDIDO")

    linhas = [
        "Relatório de acessos ao cofre",
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        f"Total de tentativas: {total}",
        f"Concedidos: {concedidos}",
        f"Negados: {negados} (rostos desconhecidos: {desconhecidos})",
        "Acessos concedidos por usuário:",
    ] + [f" - {n}: {q}" for n, q in por_usuario.most_common()]

    caminho_txt = config.RELATORIOS_DIR / f"resumo_{carimbo}.txt"
    caminho_txt.write_text("\n".join(linhas), encoding="utf-8")
    print("\n".join(linhas))
    print(f"\nArquivos salvos em: {config.RELATORIOS_DIR}")


def salvar_fases():
    cap = proc.adquirir_camera()
    try:
        for _ in range(10):
            ok, frame = cap.read()
        if not ok:
            raise RuntimeError("Falha ao ler imagem da câmera!")
    finally:
        cap.release()

    pasta = config.RELATORIOS_DIR / "fases"
    pasta.mkdir(parents=True, exist_ok=True)

    cv2.imwrite(str(pasta / "1_aquisicao.jpg"), frame)
    rgb = proc.preprocessar(frame)
    cv2.imwrite(str(pasta / "2_preprocessamento.jpg"), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))

    locais = proc.segmentar(rgb)
    seg = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    for top, right, bottom, left in locais:
        cv2.rectangle(seg, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.imwrite(str(pasta / "3_segmentacao.jpg"), seg)

    if locais:
        enc = proc.extrair_caracteristicas(rgb, locais)[0]
        (pasta / "4_caracteristicas.txt").write_text(
            "Vetor de 128 características do rosto:\n" + ", ".join(f"{v:.4f}" for v in enc),
            encoding="utf-8",
        )

    print(f"Imagens das fases salvas em: {pasta} (rostos detectados: {len(locais)})")