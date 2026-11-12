import os
import time
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk

import acesso
import banco
import cadastro
import config
import processamento as proc
import relatorio

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class CofreApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema de Cofre Biométrico")
        self.geometry("1050x680")
        self.resizable(False, False)

        banco.inicializar()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.container_principal.grid(row=0, column=0, sticky="nsew")
        self.container_principal.grid_columnconfigure(0, weight=1)
        self.container_principal.grid_rowconfigure(0, weight=1)

        self.usuario_logado = None
        self.is_root = False
        self.nivel_usuario = 3

        self.mostrar_tela_login()

    def limpar_container(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_tela_login(self):
        self.limpar_container()
        self.usuario_logado = None
        self.is_root = False
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.container_principal.grid(row=0, column=0, sticky="nsew")
        self.container_principal.grid_columnconfigure(0, weight=1)
        self.container_principal.grid_rowconfigure(0, weight=1)

        tela_login = TelaLogin(self.container_principal, self)
        tela_login.grid(row=0, column=0, sticky="nsew")

    def iniciar_sistema(self, nome_usuario, is_root=False, nivel=3):
        self.usuario_logado = nome_usuario
        self.is_root = is_root
        self.nivel_usuario = nivel
        self.limpar_container()
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        self._criar_menu_lateral()

        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.telas = {}
        self._inicializar_telas()
        
        self.mostrar_tela("Autenticação")

    def _criar_menu_lateral(self):
        menu_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        menu_frame.grid(row=0, column=0, sticky="nsew")

        titulo = ctk.CTkLabel(
            menu_frame,
            text="COFRE\nBIOMÉTRICO",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        titulo.pack(padx=20, pady=(20, 10))

        lbl_user = ctk.CTkLabel(
            menu_frame,
            text=f"Logado: {self.usuario_logado}\nNível: {self.nivel_usuario}",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="cyan"
        )
        lbl_user.pack(padx=10, pady=(0, 20))

        btn_acesso = ctk.CTkButton(
            menu_frame,
            text="🔐 Autenticação",
            height=35,
            command=lambda: self.mostrar_tela("Autenticação"),
        )
        btn_acesso.pack(padx=20, pady=6)

        if self.is_root:
            btn_cadastro = ctk.CTkButton(
                menu_frame,
                text="👤 Cadastrar Utilizador",
                height=35,
                fg_color="#2b7a0b",
                hover_color="#1e5407",
                command=lambda: self.mostrar_tela("Cadastro"),
            )
            btn_cadastro.pack(padx=20, pady=6)

            btn_usuarios = ctk.CTkButton(
                menu_frame,
                text="📋 Utilizadores",
                height=35,
                command=lambda: self.mostrar_tela("Usuarios"),
            )
            btn_usuarios.pack(padx=20, pady=6)

            # Nova aba de Rastreio / Auditoria exclusiva do ROOT
            btn_rastreio = ctk.CTkButton(
                menu_frame,
                text="🔍 Rastreio e Logs",
                height=35,
                fg_color="#8c52ff",
                hover_color="#6e35cc",
                command=lambda: self.mostrar_tela("Rastreio"),
            )
            btn_rastreio.pack(padx=20, pady=6)

        btn_relatorios = ctk.CTkButton(
            menu_frame,
            text="📊 Relatórios / Ficheiros",
            height=35,
            command=lambda: self.mostrar_tela("Relatorios"),
        )
        btn_relatorios.pack(padx=20, pady=6)

        btn_sair = ctk.CTkButton(
            menu_frame,
            text="🚪 Sair (Logout)",
            height=35,
            fg_color="#a83232",
            hover_color="#7a2323",
            command=self.mostrar_tela_login,
        )
        btn_sair.pack(padx=20, pady=(25, 10))

    def _inicializar_telas(self):
        self.telas["Autenticação"] = TelaAutenticacao(self.container, self)
        if self.is_root:
            self.telas["Cadastro"] = TelaCadastro(self.container, self)
            self.telas["Usuarios"] = TelaUsuarios(self.container, self)
            self.telas["Rastreio"] = TelaRastreio(self.container, self)
            
        self.telas["Relatorios"] = TelaRelatorios(self.container, self)

        for tela in self.telas.values():
            tela.grid(row=0, column=0, sticky="nsew")

    def mostrar_tela(self, nome_tela):
        for nome, tela in self.telas.items():
            if hasattr(tela, "parar_camera"):
                tela.parar_camera()

        if nome_tela in self.telas:
            tela = self.telas[nome_tela]
            tela.tkraise()
            if hasattr(tela, "ao_exibir"):
                tela.ao_exibir()


class TelaLogin(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frame_centro = ctk.CTkFrame(self, width=400, height=450, corner_radius=15)
        frame_centro.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            frame_centro,
            text="🔒 COFRE BIOMÉTRICO",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(30, 20))

        ctk.CTkLabel(frame_centro, text="Identificação / Utilizador:").pack(anchor="w", padx=40)
        self.ent_user = ctk.CTkEntry(frame_centro, width=320, placeholder_text="Ex: ROOT")
        self.ent_user.pack(pady=(0, 15), padx=40)

        ctk.CTkLabel(frame_centro, text="Palavra-passe (Senha):").pack(anchor="w", padx=40)
        self.ent_pass = ctk.CTkEntry(frame_centro, width=320, show="*", placeholder_text="Ex: 1234")
        self.ent_pass.pack(pady=(0, 20), padx=40)

        ctk.CTkButton(
            frame_centro,
            text="Entrar com ID e Senha",
            width=320,
            command=self.login_senha
        ).pack(pady=5, padx=40)

        ctk.CTkLabel(frame_centro, text="--- OU ---", text_color="gray").pack(pady=10)

        ctk.CTkButton(
            frame_centro,
            text="📸 Entrar com Rosto (Biometria)",
            width=320,
            fg_color="#1f538d",
            hover_color="#14375e",
            command=self.login_com_rosto
        ).pack(pady=(0, 30), padx=40)

    def login_senha(self):
        user = self.ent_user.get().strip()
        senha = self.ent_pass.get().strip()

        if user.upper() == "ROOT" and senha == "1234":
            banco.registrar_log("ROOT", "LOGIN", "Login efetuado com ID e Senha (Admin)")
            messagebox.showinfo("Sucesso", "Login efetuado como ROOT (Administrador)!")
            self.controller.iniciar_sistema("ROOT (Admin)", is_root=True, nivel=3)
            return

        try:
            infos, matriz = banco.carregar_base()
            encontrado = None
            for u in infos:
                if u["nome"].lower() == user.lower():
                    encontrado = u
                    break
            if encontrado and senha == "1234":
                banco.registrar_log(encontrado['nome'], "LOGIN", f"Login efetuado com senha (Nível {encontrado['nivel']})")
                messagebox.showinfo("Sucesso", f"Login efetuado como {encontrado['nome']}!")
                self.controller.iniciar_sistema(encontrado['nome'], is_root=False, nivel=encontrado['nivel'])
                return
        except Exception:
            pass

        messagebox.showerror("Erro de Login", "Credenciais inválidas! Verifique o utilizador e a senha.")

    def login_com_rosto(self):
        top = ctk.CTkToplevel(self)
        top.title("Login Biométrico Facial")
        top.geometry("600x500")
        top.grab_set()

        lbl_video = ctk.CTkLabel(top, text="A iniciar câmara...", width=480, height=320, fg_color="black")
        lbl_video.pack(pady=20)

        lbl_msg = ctk.CTkLabel(top, text="Aproxime o rosto para se identificar...", font=ctk.CTkFont(size=14))
        lbl_msg.pack(pady=5)

        def processar_rosto():
            try:
                infos, matriz = banco.carregar_base()
                if len(infos) == 0:
                    lbl_msg.configure(text="Nenhum utilizador cadastrado na base!", text_color="red")
                    return
            except Exception as e:
                lbl_msg.configure(text=f"Erro: {str(e)}", text_color="red")
                return

            cap = proc.adquirir_camera()
            from collections import deque
            janela = deque(maxlen=config.FRAMES_CONFIRMACAO)
            inicio = time.time()
            sucesso = False
            user_encontrado = None

            try:
                while top.winfo_exists():
                    if time.time() - inicio > config.TEMPO_LIMITE_S:
                        break
                    ok, frame = cap.read()
                    if not ok:
                        break

                    rgb = proc.preprocessar(frame)
                    locais = proc.segmentar(rgb)

                    if len(locais) == 1:
                        local = locais[0]
                        enc = proc.extrair_caracteristicas(rgb, [local])[0]
                        idx, dist = proc.classificar(enc, matriz)
                        janela.append(idx if idx is None else infos[idx]["id"])

                        if len(janela) == janela.maxlen and len(set(janela)) == 1:
                            if idx is not None:
                                user_encontrado = infos[idx]
                                sucesso = True
                                break

                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_tk = ImageTk.PhotoImage(image=img_pil)
                    if top.winfo_exists():
                        lbl_video.configure(image=img_tk, text="")
                        lbl_video.image = img_tk
                    time.sleep(0.03)
            finally:
                cap.release()

            if top.winfo_exists():
                top.destroy()

            if sucesso:
                nome = user_encontrado['nome']
                nivel = user_encontrado['nivel']
                banco.registrar_log(nome, "LOGIN_FACIAL", f"Login facial bem-sucedido (Nível {nivel})")
                messagebox.showinfo("Sucesso", f"Bem-vindo, {nome}!")
                is_root_user = (nome.upper() == "ROOT")
                self.controller.iniciar_sistema(nome, is_root=is_root_user, nivel=3 if is_root_user else nivel)
            else:
                messagebox.showwarning("Falha", "Rosto não reconhecido ou tempo esgotado.")

        import threading
        threading.Thread(target=processar_rosto, daemon=True).start()


class TelaAutenticacao(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.cap = None
        self.rodando = False

        ctk.CTkLabel(
            self,
            text="Autenticação para Acesso ao Cofre",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=10)

        self.video_label = ctk.CTkLabel(
            self, text="Câmara Desligada", width=600, height=360, fg_color="#1a1a1a"
        )
        self.video_label.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(
            self, text="Aguardando início...", font=ctk.CTkFont(size=15)
        )
        self.lbl_status.pack(pady=5)

        f_controles = ctk.CTkFrame(self)
        f_controles.pack(pady=10)

        ctk.CTkLabel(f_controles, text="Nível da Porta:").pack(side="left", padx=10)
        self.combo_nivel = ctk.CTkComboBox(
            f_controles, values=["1 - Geral", "2 - Diretor", "3 - Ministro"]
        )
        self.combo_nivel.pack(side="left", padx=10)

        self.btn_iniciar = ctk.CTkButton(
            f_controles, text="Iniciar Leitura", command=self.iniciar_autenticacao
        )
        self.btn_iniciar.pack(side="left", padx=10)

    def iniciar_autenticacao(self):
        if self.rodando:
            return

        nivel_porta = int(self.combo_nivel.get().split(" ")[0])
        try:
            infos, matriz = banco.carregar_base()
            if len(infos) == 0:
                messagebox.showwarning("Aviso", "Nenhum utilizador cadastrado na base!")
                return
        except Exception as e:
            messagebox.showerror("Erro no Banco", str(e))
            return

        self.rodando = True
        self.btn_iniciar.configure(state="disabled")

        import threading
        threading.Thread(
            target=self._loop_autenticacao, args=(nivel_porta, infos, matriz), daemon=True
        ).start()

    def _loop_autenticacao(self, nivel_porta, infos, matriz):
        from collections import deque

        self.cap = proc.adquirir_camera()
        janela = deque(maxlen=config.FRAMES_CONFIRMACAO)
        piscou = not config.EXIGIR_PISCADA
        olho_fechado = False
        inicio = time.time()

        concedido, nome, nivel_usuario, motivo = (
            False,
            "Desconhecido",
            0,
            "Tempo esgotado",
        )

        try:
            while self.rodando:
                if time.time() - inicio > config.TEMPO_LIMITE_S:
                    break
                ok, frame = self.cap.read()
                if not ok:
                    break

                rgb = proc.preprocessar(frame)
                locais = proc.segmentar(rgb)

                if len(locais) == 0:
                    janela.clear()
                    self.lbl_status.configure(
                        text=f"Aproxime o rosto (Porta nível {nivel_porta})",
                        text_color="yellow",
                    )
                elif len(locais) > 1:
                    janela.clear()
                    self.lbl_status.configure(
                        text="Apenas UMA pessoa de cada vez!", text_color="red"
                    )
                    for rosto in locais:
                        acesso.desenhar(frame, rosto, "", (0, 0, 255))
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

                    acesso.desenhar(frame, local, "A analisar...", (255, 200, 0))

                    if len(janela) == janela.maxlen and len(set(janela)) == 1:
                        if idx is None:
                            nome, nivel_usuario = "Desconhecido", 0
                            concedido, motivo = False, "Rosto não cadastrado"
                            acesso.desenhar(frame, local, "NEGADO", (0, 0, 255))
                            break
                        if not piscou:
                            self.lbl_status.configure(
                                text="Pisque para confirmar que é real!",
                                text_color="orange",
                            )
                        else:
                            nome, nivel_usuario = (
                                infos[idx]["nome"],
                                infos[idx]["nivel"],
                            )
                            if acesso._pode_acessar(nivel_usuario, nivel_porta):
                                concedido, motivo = True, "Acesso autorizado"
                                acesso.desenhar(
                                    frame, local, f"LIBERADO - {nome}", (0, 255, 0)
                                )
                            else:
                                concedido = False
                                motivo = f"Nível {nivel_usuario} insuficiente para porta {nivel_porta}"
                                acesso.desenhar(
                                    frame, local, f"NEGADO - {nome}", (0, 0, 255)
                                )
                            break

                self._atualizar_video(frame)
                time.sleep(0.03)

        finally:
            if self.cap:
                self.cap.release()
            self.rodando = False
            self.btn_iniciar.configure(state="normal")
            self.after(0, self.resetar_visor)

        banco.registrar_acesso(
            nome,
            nivel_usuario,
            nivel_porta,
            "CONCEDIDO" if concedido else "NEGADO",
            motivo,
        )
        
        # Regista log de auditoria da tentativa de acesso ao cofre
        banco.registrar_log(self.controller.usuario_logado, "AUTENTICACAO_COFRE", f"Porta Nível {nivel_porta} - Utilizador: {nome} - Status: {'CONCEDIDO' if concedido else 'NEGADO'}")

        if concedido:
            self.lbl_status.configure(
                text=f"✅ ACESSO LIBERADO: {nome}", text_color="green"
            )
        else:
            self.lbl_status.configure(
                text=f"❌ ACESSO NEGADO: {motivo}", text_color="red"
            )

    def _atualizar_video(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.configure(image=img_tk, text="")
        self.video_label.image = img_tk

    def resetar_visor(self):
        self.video_label.configure(image="", text="Câmara Desligada")
        self.video_label.image = None

    def parar_camera(self):
        self.rodando = False
        if self.cap:
            self.cap.release()
        self.after(0, self.resetar_visor)


class TelaCadastro(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.cap = None
        self.rodando = False

        ctk.CTkLabel(
            self,
            text="Cadastro de Novo Utilizador (Restrito ao ROOT)",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=10)

        f_form = ctk.CTkFrame(self)
        f_form.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(f_form, text="Nome Completo:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.ent_nome = ctk.CTkEntry(f_form, width=250)
        self.ent_nome.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(f_form, text="Cargo:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ent_cargo = ctk.CTkEntry(f_form, width=250)
        self.ent_cargo.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(f_form, text="Nível:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.combo_nivel = ctk.CTkComboBox(f_form, values=["1 - Geral", "2 - Diretor", "3 - Ministro"], width=250)
        self.combo_nivel.grid(row=2, column=1, padx=10, pady=5)

        self.video_label = ctk.CTkLabel(self, text="Câmara Desligada", width=480, height=270, fg_color="#1a1a1a")
        self.video_label.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(self, text="Preencha os dados e clique em Capturar", font=ctk.CTkFont(size=14))
        self.lbl_status.pack(pady=5)

        self.btn_capturar = ctk.CTkButton(self, text="Capturar Amostras", command=self.iniciar_captura)
        self.btn_capturar.pack(pady=5)

    def iniciar_captura(self):
        nome = self.ent_nome.get().strip()
        cargo = self.ent_cargo.get().strip()
        nivel = int(self.combo_nivel.get().split(" ")[0])

        if not nome:
            messagebox.showwarning("Aviso", "Digite o nome completo.")
            return

        self.rodando = True
        self.btn_capturar.configure(state="disabled")

        import threading
        threading.Thread(
            target=self._loop_captura, args=(nome, cargo, nivel), daemon=True
        ).start()

    def _loop_captura(self, nome, cargo, nivel):
        self.cap = proc.adquirir_camera()
        amostras = []
        ultimo = 0.0

        try:
            while self.rodando and len(amostras) < config.AMOSTRAS_CADASTRO:
                ok, frame = self.cap.read()
                if not ok:
                    break

                rgb = proc.preprocessar(frame)
                locais = proc.segmentar(rgb)

                if len(locais) == 0:
                    self.lbl_status.configure(text="Nenhum rosto encontrado na câmara", text_color="red")
                elif len(locais) > 1:
                    self.lbl_status.configure(text="Apenas UMA pessoa na tela para o cadastro", text_color="red")
                else:
                    top, right, bottom, left = proc.caixa_no_frame_original(locais[0])
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                    agora = time.time()
                    if agora - ultimo >= config.INTERVALO_AMOSTRA_S:
                        enc = proc.extrair_caracteristicas(rgb, locais)[0]
                        amostras.append(enc)
                        ultimo = agora

                    self.lbl_status.configure(
                        text=f"Amostras capturadas: {len(amostras)}/{config.AMOSTRAS_CADASTRO}",
                        text_color="cyan",
                    )

                self._atualizar_video(frame)
                time.sleep(0.03)

            if len(amostras) == config.AMOSTRAS_CADASTRO:
                banco.cadastrar_usuario(nome, cargo, nivel, amostras)
                banco.registrar_log(self.controller.usuario_logado, "CADASTRO_UTILIZADOR", f"Utilizador '{nome}' cadastrado com sucesso (Nível {nivel})")
                self.lbl_status.configure(text=f"✅ Utilizador '{nome}' cadastrado com sucesso!", text_color="green")
                messagebox.showinfo("Sucesso", f"Utilizador {nome} cadastrado com sucesso!")
                self.ent_nome.delete(0, 'end')
                self.ent_cargo.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Erro ao Cadastrar", str(e))
        finally:
            if self.cap:
                self.cap.release()
            self.rodando = False
            self.btn_capturar.configure(state="normal")
            self.after(0, self.resetar_visor)

    def _atualizar_video(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.configure(image=img_tk, text="")
        self.video_label.image = img_tk

    def resetar_visor(self):
        self.video_label.configure(image="", text="Câmera Desligada")
        self.video_label.image = None

    def parar_camera(self):
        self.rodando = False
        if self.cap:
            self.cap.release()
        self.after(0, self.resetar_visor)


class TelaUsuarios(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(
            self,
            text="Utilizadores Cadastrados",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=10)

        self.tree = ttk.Treeview(
            self,
            columns=("ID", "Nome", "Cargo", "Nível", "Amostras"),
            show="headings",
            height=12,
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Cargo", text="Cargo")
        self.tree.heading("Nível", text="Nível")
        self.tree.heading("Amostras", text="Amostras")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nome", width=200, anchor="w")
        self.tree.column("Cargo", width=150, anchor="w")
        self.tree.column("Nível", width=80, anchor="center")
        self.tree.column("Amostras", width=100, anchor="center")
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

        f_botoes = ctk.CTkFrame(self)
        f_botoes.pack(pady=10)

        ctk.CTkButton(f_botoes, text="Atualizar Lista", command=self.ao_exibir).pack(side="left", padx=10)
        
        if self.controller.is_root:
            ctk.CTkButton(
                f_botoes,
                text="Excluir Selecionado",
                fg_color="red",
                command=self.remover,
            ).pack(side="left", padx=10)

    def ao_exibir(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for u in banco.listar_usuarios():
            self.tree.insert("", "end", values=u)

    def remover(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um utilizador para remover.")
            return
        
        dados_utilizador = self.tree.item(item[0])["values"]
        uid = dados_utilizador[0]
        nome_removido = dados_utilizador[1]

        if messagebox.askyesno("Confirmar", f"Deseja remover o utilizador ID {uid} ({nome_removido})?"):
            banco.remover_usuario(uid)
            banco.registrar_log(self.controller.usuario_logado, "EXCLUSAO_UTILIZADOR", f"Removeu o utilizador '{nome_removido}' (ID: {uid})")
            self.ao_exibir()


class TelaRastreio(ctk.CTkFrame):
    """Nova Tela de Auditoria e Logs do Sistema (Exclusiva para o ROOT)"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(
            self, text="🔍 Rastreio e Auditoria do Sistema", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Estilo escuro para a tabela
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview", 
                          background="#2b2b2b", 
                          foreground="white", 
                          fieldbackground="#2b2b2b", 
                          rowheight=25)
        estilo.configure("Treeview.Heading", 
                          background="#8c52ff", 
                          foreground="white", 
                          font=('Helvetica', 10, 'bold'))
        estilo.map("Treeview", background=[('selected', '#6e35cc')])

        self.tree_logs = ttk.Treeview(
            self,
            columns=("ID", "Utilizador", "Ação", "Detalhes", "Data/Hora"),
            show="headings",
            height=14,
        )
        self.tree_logs.heading("ID", text="ID")
        self.tree_logs.heading("Utilizador", text="Utilizador")
        self.tree_logs.heading("Ação", text="Ação Realizada")
        self.tree_logs.heading("Detalhes", text="Detalhes")
        self.tree_logs.heading("Data/Hora", text="Data e Hora")

        self.tree_logs.column("ID", width=50, anchor="center")
        self.tree_logs.column("Utilizador", width=130, anchor="w")
        self.tree_logs.column("Ação", width=150, anchor="w")
        self.tree_logs.column("Detalhes", width=320, anchor="w")
        self.tree_logs.column("Data/Hora", width=140, anchor="center")
        self.tree_logs.pack(pady=10, padx=20, fill="both", expand=True)

        f_botoes = ctk.CTkFrame(self, fg_color="transparent")
        f_botoes.pack(pady=10)

        ctk.CTkButton(f_botoes, text="Atualizar Logs", command=self.ao_exibir).pack(side="left", padx=10)
        ctk.CTkButton(f_botoes, text="Exportar Logs (CSV)", fg_color="#2b7a0b", hover_color="#1e5407", command=self.exportar_logs).pack(side="left", padx=10)

    def ao_exibir(self):
        for row in self.tree_logs.get_children():
            self.tree_logs.delete(row)
        
        logs = banco.listar_logs()
        for log in logs:
            self.tree_logs.insert("", "end", values=log)

    def exportar_logs(self):
        logs = banco.listar_logs()
        if not logs:
            messagebox.showwarning("Aviso", "Não existem logs registados para exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Ficheiro CSV", "*.csv"), ("Ficheiro de Texto", "*.txt")],
            title="Guardar Relatório de Rastreio"
        )
        if not caminho:
            return

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write("ID;Utilizador;Acao;Detalhes;Data_Hora\n")
                for log in logs:
                    f.write(f"{log[0]};{log[1]};{log[2]};{log[3]};{log[4]}\n")
            
            banco.registrar_log(self.controller.usuario_logado, "EXPORTAR_LOGS", f"Exportou {len(logs)} registos de auditoria")
            messagebox.showinfo("Sucesso", f"Relatório de rastreio exportado com sucesso para:\n{caminho}")
            self.ao_exibir()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível exportar o ficheiro: {str(e)}")


class TelaRelatorios(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(
            self, text="Relatórios e Ficheiros do Sistema", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        if self.controller.is_root:
            f_upload = ctk.CTkFrame(self)
            f_upload.pack(pady=10, padx=20, fill="x")

            ctk.CTkLabel(f_upload, text="Subir Ficheiro para o Sistema:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="w")
            
            ctk.CTkLabel(f_upload, text="Nível Mínimo de Visualização:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.combo_nivel_arquivo = ctk.CTkComboBox(f_upload, values=["1 - Geral", "2 - Diretor", "3 - Ministro"], width=200)
            self.combo_nivel_arquivo.grid(row=1, column=1, padx=10, pady=5, sticky="w")

            ctk.CTkButton(f_upload, text="Selecionar Ficheiro e Enviar", fg_color="#2b7a0b", hover_color="#1e5407", command=self.subir_arquivo).grid(row=2, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(self, text="Ficheiros Disponíveis para o seu Nível (Dê duplo clique para abrir):", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview", 
                          background="#2b2b2b", 
                          foreground="white", 
                          fieldbackground="#2b2b2b", 
                          rowheight=25)
        estilo.configure("Treeview.Heading", 
                          background="#1f538d", 
                          foreground="white", 
                          font=('Helvetica', 10, 'bold'))
        estilo.map("Treeview", background=[('selected', '#1f538d')])

        self.tree_arq = ttk.Treeview(
            self,
            columns=("ID", "Nome", "Nível", "Data"),
            show="headings",
            height=10,
        )
        self.tree_arq.heading("ID", text="ID")
        self.tree_arq.heading("Nome", text="Nome do Ficheiro")
        self.tree_arq.heading("Nível", text="Nível Exigido")
        self.tree_arq.heading("Data", text="Data de Upload")

        self.tree_arq.column("ID", width=50, anchor="center")
        self.tree_arq.column("Nome", width=350, anchor="w")
        self.tree_arq.column("Nível", width=100, anchor="center")
        self.tree_arq.column("Data", width=150, anchor="center")
        self.tree_arq.pack(pady=5, padx=20, fill="both", expand=True)

        self.tree_arq.bind("<Double-1>", self.abrir_ficheiro_selecionado)

        f_botoes = ctk.CTkFrame(self, fg_color="transparent")
        f_botoes.pack(pady=10)

        ctk.CTkButton(f_botoes, text="Atualizar Lista", command=self.ao_exibir).pack(side="left", padx=10)
        ctk.CTkButton(f_botoes, text="Abrir Ficheiro", fg_color="#1f538d", hover_color="#14375e", command=self.abrir_ficheiro_selecionado).pack(side="left", padx=10)
        
        if self.controller.is_root:
            ctk.CTkButton(f_botoes, text="Deletar Ficheiro", fg_color="#a83232", hover_color="#7a2323", command=self.deletar_ficheiro_selecionado).pack(side="left", padx=10)

        self.caminhos_arquivos = {}

    def subir_arquivo(self):
        caminho = filedialog.askopenfilename(title="Selecionar Ficheiro para Upload")
        if not caminho:
            return
        
        nome_arquivo = os.path.basename(caminho)
        nivel_minimo = int(self.combo_nivel_arquivo.get().split(" ")[0])

        try:
            banco.salvar_arquivo_banco(nome_arquivo, caminho, nivel_minimo)
            banco.registrar_log(self.controller.usuario_logado, "UPLOAD_FICHEIRO", f"Subiu o ficheiro '{nome_arquivo}' (Nível mín: {nivel_minimo})")
            messagebox.showinfo("Sucesso", f"Ficheiro '{nome_arquivo}' enviado com sucesso!")
            self.ao_exibir()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o ficheiro: {str(e)}")

    def deletar_ficheiro_selecionado(self):
        selecao = self.tree_arq.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um ficheiro na lista para deletar.")
            return

        item_id = self.tree_arq.item(selecao[0])["values"][0]
        nome_arquivo = self.tree_arq.item(selecao[0])["values"][1]

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja remover o ficheiro '{nome_arquivo}' do sistema?"):
            try:
                banco.remover_arquivo_banco(item_id)
                banco.registrar_log(self.controller.usuario_logado, "DELETAR_FICHEIRO", f"Removeu o ficheiro '{nome_arquivo}' (ID: {item_id})")
                messagebox.showinfo("Sucesso", "Ficheiro removido com sucesso!")
                self.ao_exibir()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível remover o ficheiro: {str(e)}")

    def abrir_ficheiro_selecionado(self, event=None):
        selecao = self.tree_arq.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um ficheiro na lista para abrir.")
            return

        item_id = self.tree_arq.item(selecao[0])["values"][0]
        nome_arquivo = self.tree_arq.item(selecao[0])["values"][1]
        caminho_real = self.caminhos_arquivos.get(item_id)

        if caminho_real and os.path.exists(caminho_real):
            try:
                banco.registrar_log(self.controller.usuario_logado, "ABRIR_FICHEIRO", f"Abriu o ficheiro '{nome_arquivo}'")
                os.startfile(caminho_real)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o ficheiro: {str(e)}")
        else:
            messagebox.showerror("Erro", "O ficheiro físico não foi encontrado no caminho original.")

    def ao_exibir(self):
        for row in self.tree_arq.get_children():
            self.tree_arq.delete(row)
        
        self.caminhos_arquivos.clear()
        nivel_atual = self.controller.nivel_usuario
        arquivos = banco.listar_arquivos_por_nivel(nivel_atual)
        
        for arq in arquivos:
            uid, nome, caminho, nivel_min, data = arq
            self.caminhos_arquivos[uid] = caminho
            self.tree_arq.insert("", "end", values=(uid, nome, nivel_min, data))


if __name__ == "__main__":
    app = CofreApp()
    app.mainloop()