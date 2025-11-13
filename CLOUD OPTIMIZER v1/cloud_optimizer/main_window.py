# Date: 11/112025
# DEV: Martinez
# Cloud Optimizer v1 Free Utility by Martinez

import os
import sys
import threading
from collections import deque
from datetime import datetime
from PyQt6 import QtCore, QtGui, QtWidgets

# Monitor/Startup modularizados
from cloud_optimizer.monitor import Monitor
from cloud_optimizer.startup import (
    list_startup_programs,
    disable_startup_item,
    list_disabled_startup_items,
    restore_startup_item,
)
from cloud_optimizer.widgets.log_panel import LogPanelWidget

# Gráficos em tempo real (opcional)
try:
    import pyqtgraph as pg  # type: ignore
    HAS_PG = True
except Exception:
    HAS_PG = False
from cloud_optimizer.tweaks import (
    set_high_performance,
    clean_temp_files,
    optimize_network,
    optimize_services,
    disable_visual_effects,
    disable_useless_programs,
    is_admin,
)

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # base do projeto (onde está assets/)


class RestorePointWarningDialog(QtWidgets.QDialog):
    """Diálogo de aviso sobre ponto de restauração do sistema."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚠️ AVISO IMPORTANTE")
        self.setFixedSize(520, 280)
        self.setModal(True)
        
        # Remove bordas padrão para aplicar estilo customizado e permitir cantos arredondados reais
        # self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("""
            QDialog { background: transparent; }
            #restoreCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a0a1f, stop:1 #0f0515);
                border: 2px solid #9f59ff;
                border-radius: 12px;
            }
            QLabel {
                color: #e6e6e6;
                font-family: 'Segoe UI Variable', 'Inter', 'Segoe UI';
            }
            QCheckBox {
                color: #e6e6e6;
                font-family: 'Segoe UI Variable', 'Inter', 'Segoe UI';
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #9f59ff;
                border-radius: 4px;
                background: #1a1a1f;
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c66bff, stop:1 #9f59ff);
                border: 2px solid #c66bff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c66bff, stop:1 #9f59ff);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                font-size: 13px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #d488ff, stop:1 #ae72ff);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ad55ff, stop:1 #8a3de6);
            }
            QPushButton:disabled {
                background: #2f2f33;
                color: #777;
            }
        """)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        
        card = QtWidgets.QFrame()
        card.setObjectName("restoreCard")
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        outer.addWidget(card)
        
        # Ícone e título
        header = QtWidgets.QHBoxLayout()
        icon_label = QtWidgets.QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 36px;")
        header.addWidget(icon_label)
        
        title = QtWidgets.QLabel("PONTO DE RESTAURAÇÃO NECESSÁRIO")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ff9f59;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Mensagem de aviso
        message = QtWidgets.QLabel(
            "As otimizações realizadas pelo Cloud Optimizer modificam configurações "
            "importantes do sistema Windows.\n\n"
            "<b style='color:#ff9f59;'>ANTES DE CONTINUAR:</b>\n"
            "• Crie um Ponto de Restauração do Windows\n"
            "• Certifique-se de ter backups importantes\n"
            "• Aceite a responsabilidade por quaisquer mudanças\n\n"
            "<span style='color:#7d7d85; font-size:11px;'>"
            "O desenvolvedor não se responsabiliza por problemas causados pelas otimizações."
            "</span>"
        )
        message.setWordWrap(True)
        message.setTextFormat(QtCore.Qt.TextFormat.RichText)
        message.setStyleSheet("font-size: 12px; line-height: 1.5; padding: 8px;")
        layout.addWidget(message)
        
        # Checkbox de confirmação
        self.checkbox = QtWidgets.QCheckBox(
            "Eu criei um ponto de restauração e aceito os riscos das otimizações"
        )
        layout.addWidget(self.checkbox)
        
        # Botões
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.ok_btn = QtWidgets.QPushButton("Continuar")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        
        # Habilitar botão apenas quando checkbox estiver marcado
        self.checkbox.stateChanged.connect(
            lambda state: self.ok_btn.setEnabled(state == QtCore.Qt.CheckState.Checked.value)
        )


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(ROOT_DIR, "assets", "cloud_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # frameless desativado por padrão para estabilidade
        self._frameless_enabled = False
        if self._frameless_enabled:
            self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Cloud Optimizer v1")
        # Tamanho inicial e limites
        self.resize(1280, 720)
        self._min_w, self._min_h = 960, 560
        self._max_w, self._max_h = 1920, 1080
        self.setMinimumSize(self._min_w, self._min_h)
        self.setMaximumSize(self._max_w, self._max_h)

        self._anims = []
        self._nav_anim_map = {}
        self._press_anims = []
        self._startup_data = []
        self._startup_loading = False
        self._restore_warning_shown = False  # Controla se o aviso já foi exibido
        
        # Para arrastar a janela
        self._drag_pos = None
        # Para redimensionar (usado apenas em modo frameless)
        self._resize_edge = None  # valores possíveis: 'left','right','top','bottom','topleft','topright','bottomleft','bottomright'
        self._resize_start_geom = None
        self._resize_start_pos = None
        self._resize_margin = 6  # px de sensibilidade na borda
        self.top_bar = None

        self.available_handlers = {
            'Desempenho Máximo': set_high_performance,
            'Limpar Temporários': clean_temp_files,
            'Otimizar Rede': optimize_network,
            'Otimizar Serviços': optimize_services,
            'Reduzir Efeitos Visuais': disable_visual_effects,
            'Desativar Programas Inúteis': disable_useless_programs,
        }

        self._apply_fonts()
        self.setStyleSheet("""
            QMainWindow{background:#0a0a0a;font-family:'Segoe UI Variable','Inter','Segoe UI';}
            QLabel{font-family:'Segoe UI Variable','Inter','Segoe UI';}
            QPushButton{font-family:'Segoe UI Variable','Inter','Segoe UI';}
            QToolTip{color:#e6e6e6;background:#1a1a1a;border:1px solid #333;padding:6px;
                     font-family:'Segoe UI Variable','Inter','Segoe UI';}
            QScrollBar:vertical{border:none;width:10px;margin:0;background:#c66bff}
            QScrollBar::handle:vertical{background:#c66bff;min-height:30px;border-radius:5px}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0}
            QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{background:none}
        """)
        self._setup_ui()

    # ----------------- Setup / Estilos -----------------
    def _apply_fonts(self):
        try:
            fonts_dir_candidates = [
                os.path.join(ROOT_DIR, "assets", "fonts"),
                os.path.join(ROOT_DIR, "assets"),
            ]
            for bp in fonts_dir_candidates:
                if os.path.isdir(bp):
                    for fname in os.listdir(bp):
                        if fname.lower().endswith((".ttf", ".otf")) and ("inter" in fname.lower() or "segoe" in fname.lower()):
                            QtGui.QFontDatabase.addApplicationFont(os.path.join(bp, fname))
            families = QtGui.QFontDatabase.families()
            preferred = None
            for cand in ["Segoe UI Variable Text", "Segoe UI Variable", "Inter", "Segoe UI"]:
                if any(f.startswith(cand) for f in families):
                    preferred = cand
                    break
            font = QtGui.QFont(preferred if preferred else "Segoe UI")
            font.setPointSize(11)
            font.setHintingPreference(QtGui.QFont.HintingPreference.PreferFullHinting)
            font.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)
            if QtWidgets.QApplication.instance():
                QtWidgets.QApplication.instance().setFont(font)
        except Exception:
            pass

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        central.setStyleSheet("background:#000;")
        self.setCentralWidget(central)

        main_h = QtWidgets.QHBoxLayout(central)
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(0)

        content = QtWidgets.QWidget()
        content.setStyleSheet("background:#000;")
        content_v = QtWidgets.QVBoxLayout(content)
        content_v.setContentsMargins(12, 12, 12, 0)
        content_v.setSpacing(12)

        self.log_panel = LogPanelWidget(self)

        content_h = QtWidgets.QHBoxLayout(); content_h.setSpacing(12)
        content_h.addWidget(self._create_sidebar())

        self.stack = QtWidgets.QStackedWidget()
        # Inicializa monitor e página de monitoramento
        self.monitor = Monitor()
        self.page_monitor = self.build_monitor_page()
        self.stack.addWidget(self.page_monitor)
        self.nav_buttons["Monitoramento"].setChecked(True)
        self.stack.setCurrentWidget(self.page_monitor)

        content_h.addWidget(self.stack, 1)
        content_v.addLayout(content_h, 1)
        content_v.addWidget(self.log_panel)
        main_h.addWidget(content)

    # ----------------- Componentes UI -----------------
    # Log Panel passou a ser um widget reutilizável (LogPanelWidget)

    def _create_sidebar(self):
        sidebar = QtWidgets.QFrame(); sidebar.setFixedWidth(240); sidebar.setStyleSheet("QFrame{background:#0b0b0b;color:#e6e6e6}")
        v = QtWidgets.QVBoxLayout(sidebar); v.setContentsMargins(0,24,0,24)

        logo = QtWidgets.QLabel(); logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        img_path = os.path.join(ROOT_DIR, "assets", "cloud_logo.png")
        if os.path.exists(img_path):
            pix = QtGui.QPixmap(img_path)
            if not pix.isNull():
                pix = pix.scaled(200, 390, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                logo.setPixmap(pix); logo.setFixedSize(pix.size())
        v.addWidget(logo); v.addSpacing(32)

        self.nav_buttons = {}
        for name in ["Monitoramento", "Otimização", "inicialização"]:
            btn = QtWidgets.QPushButton(name); btn.setFixedHeight(48); btn.setFlat(True); btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton{color:#cfcfcf;padding:12px 24px;text-align:left;font-size:15px;font-weight:500;border-radius:10px;margin:2px 16px;background:transparent;border:none;letter-spacing:0.3px;}
                QPushButton:hover{color:#ffffff;background:rgba(255,255,255,0.05);} QPushButton:checked{color:#ffffff;background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 rgba(159,89,255,0.25), stop:1 rgba(127,0,255,0.12));border-left:3px solid #b987ff;padding-left:21px;font-weight:600;}
            """)
            btn.clicked.connect(lambda checked, n=name: self.on_nav(n))
            eff = QtWidgets.QGraphicsOpacityEffect(btn); eff.setOpacity(1.0); btn.setGraphicsEffect(eff)
            btn.pressed.connect(lambda b=btn: self._animate_press(b)); btn.released.connect(lambda b=btn: self._animate_release(b))
            v.addWidget(btn); self.nav_buttons[name] = btn
        v.addStretch()
        return sidebar

    # ----------------- Navegação / Animações -----------------
    def _animate_press(self, btn):
        try:
            eff = btn.graphicsEffect() or QtWidgets.QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(eff)
            entry = self._nav_anim_map.get(btn)
            if entry and entry.get("anim"):
                entry["anim"].stop()
            anim = QtCore.QPropertyAnimation(eff, b"opacity", self)
            anim.setDuration(180); anim.setStartValue(eff.opacity() or 1.0); anim.setEndValue(0.80)
            anim.setEasingCurve(QtCore.QEasingCurve.Type.OutQuint); anim.start()
            self._nav_anim_map[btn] = {"anim": anim}; self._press_anims.append(anim)
        except Exception:
            pass

    def _animate_release(self, btn):
        try:
            eff = btn.graphicsEffect();
            if not isinstance(eff, QtWidgets.QGraphicsOpacityEffect):
                return
            entry = self._nav_anim_map.get(btn)
            if entry and entry.get("anim"):
                entry["anim"].stop()
            anim = QtCore.QPropertyAnimation(eff, b"opacity", self)
            anim.setDuration(240); anim.setStartValue(eff.opacity() or 0.80); anim.setEndValue(1.0)
            anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic); anim.start()
            self._nav_anim_map[btn] = {"anim": anim}; self._press_anims.append(anim)
        except Exception:
            pass

    def on_nav(self, name):
        for btn in self.nav_buttons.values():
            btn.setChecked(btn.text() == name)
        pages = {
            'Monitoramento': ('page_monitor', self.build_monitor_page),
            'inicialização': ('page_startup', self.build_startup_page),
            'Otimização': ('page_tweaks', self.build_tweaks_page)
        }
        attr, builder = pages[name]
        if not hasattr(self, attr):
            try:
                page_obj = builder(); setattr(self, attr, page_obj); self.stack.addWidget(page_obj)
            except Exception as e:
                self.log_panel.append(f"Falha ao construir página '{name}': {e}"); return
        try:
            self.animate_stack_change(getattr(self, attr))
        except Exception as e:
            self.log_panel.append(f"Falha ao trocar página '{name}': {e}")

    def animate_stack_change(self, widget):
        try:
            eff = QtWidgets.QGraphicsOpacityEffect(); widget.setGraphicsEffect(eff); eff.setOpacity(0.0)
            self.stack.setCurrentWidget(widget)
            anim = QtCore.QPropertyAnimation(eff, b"opacity"); anim.setDuration(280); anim.setStartValue(0.0); anim.setEndValue(1.0)
            anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic); anim.start(); self._anims.append(anim)
        except Exception:
            self.stack.setCurrentWidget(widget)

    # ----------------- Páginas -----------------
    def build_tweaks_page(self):
        page = QtWidgets.QWidget()
        root = QtWidgets.QVBoxLayout(page)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(18)

        header_wrap = QtWidgets.QVBoxLayout(); header_wrap.setSpacing(6)
        header = QtWidgets.QLabel("OTIMIZAÇÃO <span style='color:#9900ff'>DO SISTEMA</span>")
        header.setTextFormat(QtCore.Qt.TextFormat.RichText)
        header.setStyleSheet("font-size:26px;font-weight:600;color:#e6e6e6;")
        subtitle = QtWidgets.QLabel("Aplique ajustes para melhorar desempenho e reduzir consumo de recursos.")
        subtitle.setStyleSheet("color:#8c8f96;font-size:12px;letter-spacing:0.3px;")
        deco = QtWidgets.QFrame(); deco.setFixedHeight(3); deco.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c66bff, stop:1 #8f54ff);border-radius:2px;")
        header_wrap.addWidget(header); header_wrap.addWidget(subtitle); header_wrap.addWidget(deco)
        root.addLayout(header_wrap)

        scroll = QtWidgets.QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;} QScrollBar:vertical{background:transparent;width:10px;margin:0;} QScrollBar::handle:vertical{background:rgba(159,89,255,0.45);min-height:26px;border-radius:5px;} QScrollBar::handle:vertical:hover{background:rgba(159,89,255,0.75);} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;} QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{background:transparent;}")
        inner = QtWidgets.QWidget(); inner.setStyleSheet("background:transparent;")
        inner_layout = QtWidgets.QGridLayout(inner)
        inner_layout.setSpacing(18); inner_layout.setContentsMargins(0,0,4,4)
        scroll.setWidget(inner)
        root.addWidget(scroll,1)

        actions = [
            ("Desempenho Máximo", "Ativa plano de energia desempenho máximo", set_high_performance, "⚡"),
            ("Limpar Temporários", "Remove temporários e libera espaço", clean_temp_files, "🧹"),
            ("Otimizar Rede", "Ajusta parâmetros e limpa cache DNS", optimize_network, "🌐"),
            ("Otimizar Serviços", "Desativa serviços pouco usados", optimize_services, "🛠"),
            ("Reduzir Efeitos Visuais", "Simplifica animações e transparências", disable_visual_effects, "🎨"),
            ("Desativar Programas Inúteis", "Remove inicialização de apps comuns", disable_useless_programs, "🚫"),
        ]

        col_count = 3
        self._tweak_buttons = {}
        for i,(title, desc, func, icon_txt) in enumerate(actions):
            r = i // col_count; c = i % col_count
            card = QtWidgets.QFrame(); card.setObjectName(f"tweak_card_{i}")
            card.setStyleSheet(
                f"QFrame#tweak_card_{i}{{background:#101114;border:1px solid rgba(159,89,255,0.16);border-radius:14px;}}"
                f"QFrame#tweak_card_{i}:hover{{background:#14171b;}}"
            )

            v = QtWidgets.QVBoxLayout(card); v.setContentsMargins(16,16,16,16); v.setSpacing(10)
            top_h = QtWidgets.QHBoxLayout(); top_h.setSpacing(10)
            icon_lbl = QtWidgets.QLabel(icon_txt); icon_lbl.setStyleSheet("font-size:20px; margin-right:4px;")
            ttl = QtWidgets.QLabel(title); ttl.setStyleSheet("color:#f2f2f5;font-size:15px;font-weight:600;letter-spacing:0.4px;")
            top_h.addWidget(icon_lbl,0); top_h.addWidget(ttl,1)
            v.addLayout(top_h)
            d = QtWidgets.QLabel(desc); d.setWordWrap(True); d.setStyleSheet("color:#9aa0a6;font-size:12px;line-height:150%;"); v.addWidget(d)

            btn = QtWidgets.QPushButton("EXECUTAR")
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor); btn.setFixedHeight(40)
            btn.setStyleSheet(
                "QPushButton{background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c66bff, stop:1 #9f59ff);color:#fff;border:none;border-radius:10px;font-weight:600;letter-spacing:0.6px;font-size:13px;}"
                "QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #d488ff, stop:1 #ae72ff);}" 
                "QPushButton:pressed{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ad55ff, stop:1 #8a3de6);}"
                "QPushButton:disabled{background:#2f2f33;color:#777;}"
            )

            progress_lbl = QtWidgets.QLabel("")
            progress_lbl.setStyleSheet("color:#7d7d85;font-size:11px;")

            def make_runner(f, t, b, pl):
                def run():
                    if b.isEnabled():
                        # Verificar se é admin
                        if not is_admin():
                            QtWidgets.QMessageBox.warning(
                                self,
                                "Permissão Necessária",
                                "Esta otimização requer privilégios de administrador.\n\n"
                                "Por favor, execute o Cloud Optimizer como administrador."
                            )
                            return
                        
                        # Mostrar aviso de ponto de restauração (apenas na primeira vez)
                        if not self._restore_warning_shown:
                            dialog = RestorePointWarningDialog(self)
                            if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                                return
                            self._restore_warning_shown = True
                        
                        b.setEnabled(False)
                        pl.setText("Executando...")
                        pl.setStyleSheet("color:#7d7d85;font-size:11px;")
                        self.log_panel.append(f"Iniciando: {t}")
                        
                        def job():
                            try:
                                f()
                                self.log_panel.append(f"✓ Concluído: {t}")
                                QtCore.QMetaObject.invokeMethod(pl, 'setText', QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, "✓ Concluído"))
                                QtCore.QMetaObject.invokeMethod(pl, 'setStyleSheet', QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, "color:#00ff88;font-size:11px;font-weight:600;"))
                            except Exception as e:
                                error_msg = str(e)
                                self.log_panel.append(f"✗ Erro em {t}: {error_msg}")
                                QtCore.QMetaObject.invokeMethod(pl, 'setText', QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, f"✗ Erro: {error_msg[:30]}..."))
                                QtCore.QMetaObject.invokeMethod(pl, 'setStyleSheet', QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, "color:#ff4444;font-size:11px;font-weight:600;"))
                            finally:
                                QtCore.QMetaObject.invokeMethod(b, 'setEnabled', QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(bool, True))
                        threading.Thread(target=job, daemon=True).start()
                return run
            btn.clicked.connect(make_runner(func, title, btn, progress_lbl))

            v.addWidget(btn)
            v.addWidget(progress_lbl)
            inner_layout.addWidget(card, r, c)
            self._tweak_buttons[title] = (btn, progress_lbl)

        # Ajusta colunas vazias para manter alinhamento
        inner_layout.setColumnStretch(col_count, 1)
        return page

    def _run_tweak_safe(self, func, title):
        try:
            func(); self.log_panel.append(f"Concluído: {title}")
        except Exception as e:
            self.log_panel.append(f"Erro em {title}: {e}")

    def build_monitor_page(self):
        # Wrapper com scroll
        wrapper = QtWidgets.QWidget(); outer_layout = QtWidgets.QVBoxLayout(wrapper); outer_layout.setContentsMargins(0,0,0,0); outer_layout.setSpacing(0)
        scroll = QtWidgets.QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:#000;border:none;} QScrollBar:vertical{background:transparent;width:10px;margin:0;} QScrollBar::handle:vertical{background:rgba(159,89,255,0.45);min-height:30px;border-radius:5px;} QScrollBar::handle:vertical:hover{background:rgba(159,89,255,0.75);} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;} QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{background:transparent;}")
        try:
            scroll.viewport().setStyleSheet("background:#000;")
        except Exception:
            pass
        content_widget = QtWidgets.QWidget(); content_widget.setStyleSheet("background:#000;"); layout = QtWidgets.QVBoxLayout(content_widget); layout.setContentsMargins(0,0,0,24)
        scroll.setWidget(content_widget); outer_layout.addWidget(scroll)
        header = QtWidgets.QHBoxLayout(); header.setContentsMargins(0,0,0,24)
        title = QtWidgets.QLabel("MONITORAMENTO <span style='color:#9900ff;'>DO PC</span>"); title.setTextFormat(QtCore.Qt.TextFormat.RichText); title.setStyleSheet("font-size:26px;font-weight:600;color:#e6e6e6;")
        header.addWidget(title); header.addStretch(); layout.addLayout(header)
        # Removidos cards de CPU e RAM - agora mostrados no gráfico
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(14)
        grid.setContentsMargins(12, 0, 12, 0)
        cards = [
            ("GPU", "N/A", "Uso de GPU"),
            ("Temp", "0°C", "Temperatura CPU"),
            ("Disco", "0 MB/s", "Atividade do disco"),
            ("Rede", "0 Mb/s", "Uso de rede"),
        ]
        self.monitor_values = {}
        self.monitor_cards = {}
        cols = 2  # 2 colunas agora
        total_cards = len(cards)
        for i,(name, initial, desc) in enumerate(cards):
            # Se for a última linha e só tem um card, centraliza usando 3 colunas
            if (i == total_cards - 1) and (total_cards % cols == 1):
                r = i // cols
                # Espaçador esquerda
                grid.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum), r, 0)
                # Card centralizado
                c = 1
            else:
                r = i // cols
                c = i % cols
            card_outer = QtWidgets.QFrame()
            card_outer.setObjectName(f"monitor_card_{i}")
            card_outer.setStyleSheet(f"QFrame#monitor_card_{i}{{background:#0f1113;border-radius:10px;}} ")
            card_outer.setMinimumHeight(120)
            card_outer.setMinimumWidth(400)
            outer_layout = QtWidgets.QHBoxLayout(card_outer)
            outer_layout.setContentsMargins(0,0,0,0)
            outer_layout.setSpacing(0)
            accent = QtWidgets.QFrame()
            accent.setFixedWidth(4)
            accent.setStyleSheet("QFrame{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c66bff, stop:1 #9f59ff);}")
            outer_layout.addWidget(accent)
            content = QtWidgets.QWidget()
            content.setStyleSheet("background:transparent;")
            content_layout = QtWidgets.QVBoxLayout(content)
            content_layout.setContentsMargins(16,14,16,14)
            content_layout.setSpacing(6)
            title_lbl = QtWidgets.QLabel(name)
            title_lbl.setStyleSheet("color:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c66bff, stop:1 #9f59ff);font-size:14px;font-weight:600;")
            content_layout.addWidget(title_lbl)
            value_lbl = QtWidgets.QLabel(initial)
            value_lbl.setStyleSheet("color:#f2f2f2;")
            value_lbl.setFont(QtGui.QFont("Segoe UI", 22, QtGui.QFont.Weight.Bold))
            value_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
            content_layout.addWidget(value_lbl)
            # Adiciona dica se for GPU ou Temp e valor for N/A
            tip_text = desc
            if name == "GPU" and initial == "N/A":
                tip_text += "\n⚠ Requer placa NVIDIA com drivers e nvidia-smi disponíveis."
            if name == "Temp" and initial == "N/A":
                tip_text += "\n⚠ Sensor de temperatura não disponível ou não suportado pelo sistema."
            desc_lbl = QtWidgets.QLabel(tip_text)
            desc_lbl.setStyleSheet("color:#9aa0a6;font-size:11px;")
            desc_lbl.setWordWrap(True)
            content_layout.addWidget(desc_lbl)
            outer_layout.addWidget(content,1)
            grid.addWidget(card_outer,r,c)
            self.monitor_values[name] = value_lbl
            self.monitor_cards[name] = card_outer
            def make_mask_applier(card):
                def apply():
                    try:
                        size = card.size()
                        path = QtGui.QPainterPath()
                        path.addRoundedRect(QtCore.QRectF(0,0,size.width(),size.height()),12,12)
                        region = QtGui.QRegion(path.toFillPolygon(QtGui.QTransform()).toPolygon())
                        card.setMask(region)
                    except:
                        pass
                return apply
            mask_func = make_mask_applier(card_outer)
            original_resize = card_outer.resizeEvent
            def new_resize(event):
                original_resize(event)
                mask_func()
            card_outer.resizeEvent = new_resize
            QtCore.QTimer.singleShot(0, mask_func)
            def make_hover(card_w, idx):
                def enter(e):
                    card_w.setStyleSheet(f"QFrame#monitor_card_{idx}{{background:#141619;border-radius:12px;}}")
                def leave(e):
                    card_w.setStyleSheet(f"QFrame#monitor_card_{idx}{{background:#0f1113;border-radius:12px;}}")
                return enter, leave
            enter_h, leave_h = make_hover(card_outer,i)
            card_outer.enterEvent = enter_h
            card_outer.leaveEvent = leave_h
            # Se for a última linha e só tem um card, adiciona espaçador à direita
            if (i == total_cards - 1) and (total_cards % cols == 1):
                grid.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum), r, 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        layout.addLayout(grid)

        # Área de gráficos em tempo real com PyQtGraph
        self._chart_points = 60  # 60 amostras
        if HAS_PG:
            try:
                # Inicializa séries de dados
                self._cpu_series = deque([0]*self._chart_points, maxlen=self._chart_points)
                self._ram_series = deque([0]*self._chart_points, maxlen=self._chart_points)
                
                # Container dos gráficos
                charts_frame = QtWidgets.QFrame()
                charts_frame.setObjectName("chartsFrame")
                charts_frame.setStyleSheet(
                    "QFrame#chartsFrame{"
                    "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                    " stop:0 #111320, stop:1 #0b0d13);"
                    "border:1px solid rgba(159,89,255,0.32);"
                    "border-radius:18px;"
                    "}"
                )

                charts_layout = QtWidgets.QVBoxLayout(charts_frame)
                charts_layout.setContentsMargins(20, 20, 20, 20)
                charts_layout.setSpacing(14)
                
                # Título da seção com legenda
                header_layout = QtWidgets.QHBoxLayout()
                header_layout.setSpacing(16)

                charts_title = QtWidgets.QLabel("GRÁFICOS EM <span style='color:#9900ff;'>TEMPO REAL</span>")
                charts_title.setTextFormat(QtCore.Qt.TextFormat.RichText)
                charts_title.setStyleSheet("font-size:18px;font-weight:600;color:#e6e6e6;background:transparent;border:none;")
                header_layout.addWidget(charts_title)

                header_layout.addStretch()

                # Legenda inline sem fundo
                legend_cpu = QtWidgets.QLabel(
                    "<span style='font-size:15px;vertical-align:middle;'>●</span> "
                    "<span style='color:#4dabf7;'>Processador (CPU)</span> "
                    "<span style='color:#f0ad4e;font-size:11px;'>⚠ Se estiver 0%, aguarde alguns segundos.</span>"
                )
                legend_cpu.setTextFormat(QtCore.Qt.TextFormat.RichText)
                legend_cpu.setStyleSheet("font-size:13px;color:#e6e6e6;background:transparent;border:none;padding:0px 8px;vertical-align:middle;")
                legend_cpu.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
                header_layout.addWidget(legend_cpu)

                legend_ram = QtWidgets.QLabel("<span style='font-size:15px;vertical-align:middle;'>●</span> <span style='color:#51cf66;'>Memória (RAM)</span>")
                legend_ram.setTextFormat(QtCore.Qt.TextFormat.RichText)
                legend_ram.setStyleSheet("font-size:13px;color:#e6e6e6;background:transparent;border:none;padding:0px 8px;vertical-align:middle;")
                legend_ram.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
                header_layout.addWidget(legend_ram)

                charts_layout.addLayout(header_layout)
                
                # Widget de plotagem
                self.plot_widget = pg.PlotWidget()
                self.plot_widget.setBackground('#07080d')
                self.plot_widget.setMinimumHeight(100)
                self.plot_widget.setMaximumHeight(350)
                self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
                self.plot_widget.setYRange(0, 105)
                self.plot_widget.setLimits(yMin=0, yMax=105)
                # Adiciona ticks customizados para mostrar 0, 20, 40, 60, 80, 100
                yticks = [(v, f"{v}%") for v in [0, 20, 40, 60, 80, 100]]
                self.plot_widget.getAxis('left').setTicks([yticks])
                self.plot_widget.setXRange(-self._chart_points + 1, 0)
                self.plot_widget.setLimits(xMin=-self._chart_points + 1, xMax=0)
                self.plot_widget.setStyleSheet("background:#07080d;border:1px solid rgba(159,89,255,0.18);")
                self.plot_widget.setLabel('left', 'Uso (%)', color='#9aa0a6', size='11pt')
                self.plot_widget.setLabel('bottom', 'Tempo (s atrás)', color='#9aa0a6', size='11pt')
                
                # Estiliza os eixos
                self.plot_widget.getAxis('left').setTextPen('#9aa0a6')
                self.plot_widget.getAxis('bottom').setTextPen('#9aa0a6')
                
                # Curvas de CPU (azul) e RAM (verde)
                self.cpu_curve = self.plot_widget.plot(
                    pen=pg.mkPen(color=(77, 171, 247), width=2.5),  # Azul #4dabf7
                    name='CPU %'
                )
                self.ram_curve = self.plot_widget.plot(
                    pen=pg.mkPen(color=(81, 207, 102), width=2.5),  # Verde #51cf66
                    name='RAM %'
                )
                
                charts_layout.addWidget(self.plot_widget)
                layout.addSpacing(18)
                layout.addWidget(charts_frame)
                
            except Exception as e:
                self.plot_widget = None
                self.log_panel.append(f"Aviso: Gráficos não disponíveis - {e}")
        else:
            self.plot_widget = None
            # Aviso se PyQtGraph não estiver instalado
            no_chart_label = QtWidgets.QLabel("⚠ Instale PyQtGraph para ver gráficos em tempo real: pip install pyqtgraph")
            no_chart_label.setStyleSheet("color:#9aa0a6;font-size:12px;padding:12px;")
            layout.addWidget(no_chart_label)

        layout.addStretch()
        # Timer de atualização com coleta assíncrona
        self._monitor_fetching = False
        self.monitor_timer = QtCore.QTimer()
        self.monitor_timer.timeout.connect(self._request_monitor_metrics)
        self.monitor_timer.start(1000)
        QtCore.QTimer.singleShot(0, self._request_monitor_metrics)
        QtCore.QTimer.singleShot(0, self._normalize_monitor_cards)
        return wrapper

    def _request_monitor_metrics(self):
        if self._monitor_fetching:
            return

        self._monitor_fetching = True

        def job():
            try:
                data = self.monitor.get_metrics()
            except Exception:
                data = {}

            QtCore.QMetaObject.invokeMethod(
                self,
                "_handle_monitor_metrics",
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(object, data),
            )

        threading.Thread(target=job, daemon=True).start()

    def _normalize_monitor_cards(self):
        try:
            for lbl in self.monitor_values.values():
                fm = QtGui.QFontMetrics(lbl.font()); h = fm.height() + 8
                if h > lbl.minimumHeight(): lbl.setMinimumHeight(h)
                lbl.setText(lbl.text())
        except Exception: pass

    @QtCore.pyqtSlot(object)
    def _handle_monitor_metrics(self, payload):
        self._monitor_fetching = False
        if isinstance(payload, dict) and payload:
            self._apply_monitor_metrics(payload)

    def _apply_monitor_metrics(self, metrics: dict):
        try:
            fmt = metrics.get('formatted', {})

            for key in ['GPU', 'Temp', 'Disco', 'Rede']:
                if key in self.monitor_values:
                    self.monitor_values[key].setText(fmt.get(key, 'N/A'))

            if hasattr(self, 'plot_widget') and self.plot_widget is not None:
                cpu_val = metrics.get('cpu_pct', 0.0)
                ram_val = metrics.get('ram_pct', 0.0)

                self._cpu_series.append(cpu_val)
                self._ram_series.append(ram_val)

                xs = list(range(-len(self._cpu_series) + 1, 1))
                self.cpu_curve.setData(xs, list(self._cpu_series))
                self.ram_curve.setData(xs, list(self._ram_series))
        except Exception:
            pass

    def build_startup_page(self):
        page = QtWidgets.QWidget(); root = QtWidgets.QVBoxLayout(page); root.setContentsMargins(0,0,0,0); root.setSpacing(18)
        header_wrap = QtWidgets.QVBoxLayout(); header_wrap.setSpacing(6)
        title = QtWidgets.QLabel("GERENCIAR PROGRAMAS NA INICIALIZAÇÃO")
        title.setStyleSheet("font-size:25px;font-weight:600;color:#f2f2f5;letter-spacing:0.6px;background:transparent;border:none;")
        header_wrap.addWidget(title)
        subtitle = QtWidgets.QLabel("Desative itens que iniciam com o Windows para reduzir uso de RAM e tempo de boot.")
        subtitle.setStyleSheet("color:#b9b9c5;font-size:13px;letter-spacing:0.3px;background:transparent;border:none;")
        header_wrap.addWidget(subtitle)
        deco = QtWidgets.QFrame(); deco.setFixedHeight(3); deco.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #c66bff, stop:1 #8f54ff);border-radius:2px;"); header_wrap.addWidget(deco); root.addLayout(header_wrap)
        card = QtWidgets.QFrame(); card.setStyleSheet("QFrame{background:rgba(255,255,255,0.02);border:1px solid rgba(198,107,255,0.12);border-radius:14px;}"); card_layout = QtWidgets.QVBoxLayout(card); card_layout.setContentsMargins(18,18,18,18); card_layout.setSpacing(14)
        top_row = QtWidgets.QHBoxLayout(); top_row.setSpacing(10)
        self.startup_search = QtWidgets.QLineEdit(); self.startup_search.setPlaceholderText("Buscar programa (nome ou executável)..."); self.startup_search.textChanged.connect(self.filter_startup_list); self.startup_search.setClearButtonEnabled(True)
        self.startup_search.setStyleSheet("""
            QLineEdit{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:8px 12px;color:#e7e7e9;font-size:13px;}
            QLineEdit:focus{border:1px solid #b987ff;background:rgba(255,255,255,0.07);}
        """); top_row.addWidget(self.startup_search,1)
        self.btn_refresh_startup = QtWidgets.QPushButton("⟳  ATUALIZAR LISTA"); self.btn_refresh_startup.clicked.connect(self.update_startup_programs); self.btn_refresh_startup.setCursor(QtCore.Qt.CursorShape.PointingHandCursor); self.btn_refresh_startup.setFixedHeight(38)
        self.btn_refresh_startup.setStyleSheet("""
            QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c66bff, stop:1 #9f59ff);color:#ffffff;font-weight:600;font-size:13px;border:none;padding:8px 22px;border-radius:11px;letter-spacing:0.4px;}
            QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #d488ff, stop:1 #ae72ff);} QPushButton:pressed{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ad55ff, stop:1 #8a3de6);}
        """); top_row.addWidget(self.btn_refresh_startup)

        # Botão para exibir itens desativados
        self.btn_disabled_items = QtWidgets.QPushButton("🗂  ITENS DESATIVADOS"); self.btn_disabled_items.setCursor(QtCore.Qt.CursorShape.PointingHandCursor); self.btn_disabled_items.setFixedHeight(38)
        self.btn_disabled_items.setStyleSheet("""
            QPushButton{background:rgba(255,255,255,0.06);color:#e7e7e9;font-weight:600;font-size:13px;border:1px solid rgba(255,255,255,0.10);padding:8px 18px;border-radius:11px;letter-spacing:0.3px;}
            QPushButton:hover{background:rgba(255,255,255,0.10);} QPushButton:pressed{background:rgba(255,255,255,0.08);} 
        """)
        self.btn_disabled_items.clicked.connect(self._open_disabled_items_dialog)
        top_row.addWidget(self.btn_disabled_items)

        # (Botões Dev/Test removidos a pedido do usuário)

        card_layout.addLayout(top_row)
        self.startup_list = QtWidgets.QListWidget(); self.startup_list.setSpacing(8)
        self.startup_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.startup_list.setStyleSheet("""
            QListWidget{background:transparent;border:none;outline:0;} QScrollBar:vertical{background:transparent;width:10px;margin:2px;} QScrollBar::handle:vertical{background:rgba(198,107,255,0.5);min-height:24px;border-radius:5px;} QScrollBar::handle:vertical:hover{background:rgba(198,107,255,0.8);} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}
        """); card_layout.addWidget(self.startup_list,1)
        info = QtWidgets.QLabel("Dica: Alguns itens podem voltar após updates do sistema. Revise periodicamente.")
        info.setStyleSheet("color:#7d7d85;font-size:11px;background:transparent;border:none;padding:4px;")
        card_layout.addWidget(info)
        root.addWidget(card,1); self.update_startup_programs(); return page

    def filter_startup_list(self):
        term = self.startup_search.text().strip().lower(); self.startup_list.clear(); data = self._startup_data

        if self._startup_loading and not data:
            item = QtWidgets.QListWidgetItem(); lbl = QtWidgets.QLabel("Carregando itens..."); lbl.setStyleSheet("color:#b987ff;font-size:13px;padding:24px;"); lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter); item.setSizeHint(QtCore.QSize(0,80)); self.startup_list.addItem(item); self.startup_list.setItemWidget(item,lbl); return

        filtered = data if not term else [d for d in data if term in (d['name'] + ' ' + d['exe'] + ' ' + d.get('value', '')).lower()]
        if not filtered:
            msg = "Nenhum resultado." if not self._startup_loading else "Carregando itens..."
            item = QtWidgets.QListWidgetItem(); lbl = QtWidgets.QLabel(msg); lbl.setStyleSheet("color:#7d7d89;font-size:13px;padding:24px;"); lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter); item.setSizeHint(QtCore.QSize(0,80)); self.startup_list.addItem(item); self.startup_list.setItemWidget(item,lbl); return
        for d in filtered:
            it = QtWidgets.QListWidgetItem(); w = self._create_startup_item_widget(d['name'], d['exe'], d, d['source']); it.setSizeHint(w.sizeHint()); self.startup_list.addItem(it); self.startup_list.setItemWidget(it,w)

    def update_startup_programs(self):
        if self._startup_loading:
            return

        self._startup_loading = True
        if hasattr(self, 'btn_refresh_startup') and self.btn_refresh_startup is not None:
            self.btn_refresh_startup.setEnabled(False)
            self.btn_refresh_startup.setText("Carregando...")

        def job():
            try:
                data = list_startup_programs()
                result = {"data": data, "error": None}
            except Exception as exc:
                result = {"data": [], "error": exc}

            QtCore.QMetaObject.invokeMethod(
                self,
                "_handle_startup_results",
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(object, result),
            )

        threading.Thread(target=job, daemon=True).start()

    @QtCore.pyqtSlot(object)
    def _handle_startup_results(self, payload):
        self._startup_loading = False

        if hasattr(self, 'btn_refresh_startup') and self.btn_refresh_startup is not None:
            self.btn_refresh_startup.setEnabled(True)
            self.btn_refresh_startup.setText("⟳  ATUALIZAR LISTA")

        if isinstance(payload, dict):
            data = payload.get("data", [])
            error = payload.get("error")
        else:
            data = []
            error = None

        if error:
            self.log_panel.append(f"Erro ao carregar itens de inicialização: {error}")

        self._startup_data = data or []
        self.filter_startup_list()

    def _create_startup_item_widget(self, name, exe, data, source):
        w = QtWidgets.QFrame()
        w.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(198,107,255,0.12);
                border-radius: 10px;
            }
            QFrame:hover {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(198,107,255,0.12);
                border-radius: 10px;
            }
        """)
        h = QtWidgets.QHBoxLayout(w); h.setContentsMargins(10,8,10,8); h.setSpacing(10)

        # Botão circular com ícone de power-off, sombra e animação
        btn = QtWidgets.QPushButton()
        btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn.setToolTip("Desativar da inicialização")
        btn.setFixedSize(32, 32)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff4444, stop:1 #c80000);
                border: 2px solid #ff8888;
                border-radius: 16px;
                color: #fff6f6;
                font-size: 18px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8888, stop:1 #ff4444);
                border: 2px solid #fff0f0;
                color: #fff;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c80000, stop:1 #ff4444);
                border: 2px solid #ff4444;
            }
            QPushButton:disabled {
                background: #2f2f33;
                color: #777;
                border: 2px solid #444;
            }
        """)
    # Sombra removida para evitar bugs de renderização
        # Ícone unicode power-off
        btn.setText("\u23FB")  # ⏻
        h.addWidget(btn)

        txt = QtWidgets.QLabel(f"<b>{name}</b><br><span style='color:#b987ff;font-size:11px'>{exe}</span>")
        txt.setTextFormat(QtCore.Qt.TextFormat.RichText)
        txt.setStyleSheet("color:#e7e7e9;font-size:12px;background:transparent;border:none;")
        h.addWidget(txt,1)
        # Selo de origem + admin quando necessário
        need_admin = (source == 'HKLM Run')
        src_text = source + ("  •  Admin" if need_admin else "")
        src = QtWidgets.QLabel(src_text)
        if need_admin:
            src.setToolTip("Requer executar como Administrador")
        src.setStyleSheet("color:#7d7d89;font-size:10px;background:transparent;border:none;")
        h.addWidget(src)

        # Conecta ação de desativar
        def on_disable():
            if not btn.isEnabled():
                return
            btn.setEnabled(False)
            self.log_panel.append(f"Desativando da inicialização: {name}")

            def job():
                try:
                    disable_startup_item(data)
                    self.log_panel.append(f"Concluído: {name} desativado")
                    # Atualiza a lista de forma segura na UI thread
                    QtCore.QTimer.singleShot(0, self.update_startup_programs)
                except PermissionError as e:
                    QtCore.QMetaObject.invokeMethod(btn, 'setEnabled', QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(bool, True))
                    # Log e aviso na UI thread
                    def _show_warn():
                        self.log_panel.append(f"Permissão necessária: {e}")
                        QtWidgets.QMessageBox.warning(
                            self,
                            'Permissão necessária',
                            'Para desativar itens do HKLM, execute como administrador.'
                        )
                    QtCore.QTimer.singleShot(0, _show_warn)
                except Exception as e:
                    QtCore.QMetaObject.invokeMethod(btn, 'setEnabled', QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(bool, True))
                    self.log_panel.append(f"Erro ao desativar {name}: {e}")
                
            threading.Thread(target=job, daemon=True).start()

        btn.clicked.connect(on_disable)
        return w

    def _open_disabled_items_dialog(self):
        try:
            items = list_disabled_startup_items()
            dlg = QtWidgets.QDialog(self)
            dlg.setWindowTitle("Itens Desativados")
            dlg.setStyleSheet("""
                QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #18122b, stop:1 #22113a);
                    border: 2px solid #9f59ff;
                    border-radius: 18px;
                }
                QLabel {
                    color: #f2f2f5;
                    font-size: 15px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }
                QListWidget {
                    background: rgba(255,255,255,0.06);
                    border: 1px solid #9f59ff;
                    border-radius: 12px;
                    padding: 10px;
                    color: #e7e7e9;
                    font-size: 14px;
                }
                QPushButton {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c66bff, stop:1 #9f59ff);
                    color: #fff;
                    font-weight: 700;
                    font-size: 15px;
                    border: none;
                    padding: 12px 0px;
                    border-radius: 12px;
                    margin-top: 8px;
                    letter-spacing: 0.5px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #d488ff, stop:1 #ae72ff);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ad55ff, stop:1 #8a3de6);
                }
            """)

            layout = QtWidgets.QVBoxLayout(dlg)
            layout.setContentsMargins(24, 24, 24, 24)
            layout.setSpacing(12)
            label = QtWidgets.QLabel("Itens desativados na inicialização do Windows:")
            layout.addWidget(label)
            listw = QtWidgets.QListWidget()
            layout.addWidget(listw, 1)

            def refresh_list(listw):
                listw.clear()
                current_items = list_disabled_startup_items()
                if not current_items:
                    listw.addItem(QtWidgets.QListWidgetItem("Nenhum item desativado."))
                    return
                for itdata in current_items:
                    it = QtWidgets.QListWidgetItem()
                    frame = QtWidgets.QFrame()
                    frame.setStyleSheet("QFrame{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.10);border-radius:8px;}QFrame:hover{background:rgba(255,255,255,0.05);}")
                    fh = QtWidgets.QHBoxLayout(frame)
                    fh.setContentsMargins(10,8,10,8)
                    fh.setSpacing(10)
                    subtitle_path = itdata.get('path', '')
                    right_badge = None
                    if itdata.get('kind') == 'registry':
                        subtitle_path = f"{itdata.get('hive')}\\{itdata.get('base')}"
                        if itdata.get('hive') == 'HKLM':
                            right_badge = QtWidgets.QLabel("Admin")
                            right_badge.setStyleSheet("color:#ffcc66;font-size:10px;background:rgba(255,204,102,0.12);border:1px solid rgba(255,204,102,0.25);padding:2px 6px;border-radius:6px;")
                            right_badge.setToolTip("Restaurar em HKLM requer executar como Administrador")
                    lbl = QtWidgets.QLabel(f"<b>{itdata['name']}</b><br><span style='color:#b987ff;font-size:11px'>{subtitle_path}</span>")
                    lbl.setTextFormat(QtCore.Qt.TextFormat.RichText)
                    lbl.setStyleSheet("color:#e7e7e9;font-size:12px;background:transparent;border:none;")
                    fh.addWidget(lbl,1)
                    restore_btn = QtWidgets.QPushButton("Restaurar")
                    restore_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                    restore_btn.setStyleSheet("""
                        QPushButton{background:#4da36f;color:#ffffff;font-weight:600;font-size:12px;border:none;padding:6px 14px;border-radius:8px;}
                        QPushButton:hover{background:#5ab884;} QPushButton:pressed{background:#3d8e5e;}
                    """)
                    fh.addWidget(restore_btn)
                    if right_badge is not None:
                        fh.addWidget(right_badge)
                    # Se for item de registro HKLM e não tiver admin, desabilita botão
                    if itdata.get('kind') == 'registry' and itdata.get('hive') == 'HKLM' and not is_admin():
                        restore_btn.setEnabled(False)
                        restore_btn.setToolTip("Execute o Cloud Optimizer como Administrador para restaurar este item (HKLM).")
                    def make_restore(entry, btn_ref=restore_btn):
                        def do_restore():
                            btn_ref.setEnabled(False)
                            self.log_panel.append(f"Restaurando: {entry['name']}")
                            def job():
                                try:
                                    restore_startup_item(entry)
                                    self.log_panel.append(f"Concluído: {entry['name']} restaurado")
                                    QtCore.QTimer.singleShot(0, self.update_startup_programs)
                                    QtCore.QTimer.singleShot(0, lambda: refresh_list(listw))
                                except Exception as e:
                                    self.log_panel.append(f"Erro ao restaurar {entry['name']}: {e}")
                                    QtCore.QTimer.singleShot(0, lambda: btn_ref.setEnabled(True))
                            threading.Thread(target=job, daemon=True).start()
                        return do_restore
                    restore_btn.clicked.connect(make_restore(itdata))
                    it.setSizeHint(frame.sizeHint())
                    listw.addItem(it)
                    listw.setItemWidget(it, frame)
            refresh_list(listw)

            # Botão de fechar
            btn_close = QtWidgets.QPushButton("Fechar")
            btn_close.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn_close.setStyleSheet("margin-top:12px;font-size:14px;background:#9f59ff;color:#fff;border-radius:8px;padding:8px 24px;")
            btn_close.clicked.connect(dlg.accept)
            layout.addWidget(btn_close)

            dlg.setMinimumWidth(480)
            dlg.exec()
        except Exception as e:
            self.log_panel.append(f"Erro ao abrir diálogo de itens desativados: {e}")

    # ----------------- Arrastar janela -----------------
    def _is_in_top_bar(self, global_pos: QtCore.QPoint) -> bool:
        """Retorna True se a posição global estiver dentro da barra superior."""
        if not getattr(self, '_frameless_enabled', False):
            return False
        try:
            if not hasattr(self, 'top_bar') or self.top_bar is None:
                return False
            top_left = self.top_bar.mapToGlobal(QtCore.QPoint(0, 0))
            rect = QtCore.QRect(top_left, self.top_bar.size())
            return rect.contains(global_pos)
        except Exception:
            return False

    def _detect_resize_edges(self, global_pos: QtCore.QPoint):
        """Retorna o identificador da borda/canto se o mouse estiver próximo."""
        if not getattr(self, '_frameless_enabled', False):
            return None
        margin = self._resize_margin
        geom = self.frameGeometry()
        left = geom.left(); right = geom.right(); top = geom.top(); bottom = geom.bottom()
        x = global_pos.x(); y = global_pos.y()

        on_left = abs(x - left) <= margin
        on_right = abs(x - right) <= margin
        on_top = abs(y - top) <= margin
        on_bottom = abs(y - bottom) <= margin

        if on_top and on_left:
            return 'topleft'
        if on_top and on_right:
            return 'topright'
        if on_bottom and on_left:
            return 'bottomleft'
        if on_bottom and on_right:
            return 'bottomright'
        if on_left:
            return 'left'
        if on_right:
            return 'right'
        if on_top:
            return 'top'
        if on_bottom:
            return 'bottom'
        return None

    def mousePressEvent(self, event):
        """Inicia arrasto apenas quando clicar na barra superior."""
        if not getattr(self, '_frameless_enabled', False):
            super().mousePressEvent(event)
            return
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            gpos = event.globalPosition().toPoint()
            edge = self._detect_resize_edges(gpos)
            if edge is not None:
                # Inicia redimensionamento
                self._resize_edge = edge
                self._resize_start_geom = self.frameGeometry()
                self._resize_start_pos = gpos
                event.accept()
                return
            if self._is_in_top_bar(gpos):
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Move a janela enquanto arrasta a partir da barra superior."""
        if not getattr(self, '_frameless_enabled', False):
            super().mouseMoveEvent(event)
            return
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        # Redimensionando
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton and self._resize_edge is not None:
            self._apply_resize(event.globalPosition().toPoint())
            event.accept()
            return
        # Atualiza cursor ao passar próximo das bordas
        edge = self._detect_resize_edges(event.globalPosition().toPoint())
        cursor_map = {
            'left': QtCore.Qt.CursorShape.SizeHorCursor,
            'right': QtCore.Qt.CursorShape.SizeHorCursor,
            'top': QtCore.Qt.CursorShape.SizeVerCursor,
            'bottom': QtCore.Qt.CursorShape.SizeVerCursor,
            'topleft': QtCore.Qt.CursorShape.SizeFDiagCursor,
            'bottomright': QtCore.Qt.CursorShape.SizeFDiagCursor,
            'topright': QtCore.Qt.CursorShape.SizeBDiagCursor,
            'bottomleft': QtCore.Qt.CursorShape.SizeBDiagCursor,
        }
        self.setCursor(cursor_map.get(edge, QtCore.Qt.CursorShape.ArrowCursor))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Finaliza o arrasto."""
        if not getattr(self, '_frameless_enabled', False):
            super().mouseReleaseEvent(event)
            return
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self._drag_pos is not None:
                self._drag_pos = None
                event.accept()
                return
            if self._resize_edge is not None:
                self._resize_edge = None
                self._resize_start_geom = None
                self._resize_start_pos = None
                self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def _apply_resize(self, gpos: QtCore.QPoint):
        """Aplica o redimensionamento conforme a borda sendo arrastada, respeitando min/max."""
        if (not getattr(self, '_frameless_enabled', False) or
                not self._resize_start_geom or not self._resize_edge or not self._resize_start_pos):
            return
        geom = QtCore.QRect(self._resize_start_geom)
        dx = gpos.x() - self._resize_start_pos.x()
        dy = gpos.y() - self._resize_start_pos.y()

        # Ajuste por borda/canto
        if 'left' in self._resize_edge:
            new_left = geom.left() + dx
            max_left = geom.right() - self._min_w
            min_left = geom.right() - self._max_w
            new_left = max(min(new_left, max_left), min_left)
            geom.setLeft(new_left)
        if 'right' in self._resize_edge:
            new_right = geom.right() + dx
            min_right = geom.left() + self._min_w
            max_right = geom.left() + self._max_w
            new_right = max(min(new_right, max_right), min_right)
            geom.setRight(new_right)
        if 'top' in self._resize_edge:
            new_top = geom.top() + dy
            max_top = geom.bottom() - self._min_h
            min_top = geom.bottom() - self._max_h
            new_top = max(min(new_top, max_top), min_top)
            geom.setTop(new_top)
        if 'bottom' in self._resize_edge:
            new_bottom = geom.bottom() + dy
            min_bottom = geom.top() + self._min_h
            max_bottom = geom.top() + self._max_h
            new_bottom = max(min(new_bottom, max_bottom), min_bottom)
            geom.setBottom(new_bottom)

        # Aplica geometria resultante
        self.setGeometry(geom)
