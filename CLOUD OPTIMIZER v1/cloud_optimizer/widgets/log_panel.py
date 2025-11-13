# Date: 10/112025
# DEV: Martinez
# Cloud Optimizer v1 Free Utility by Martinez

from PyQt6 import QtCore, QtGui, QtWidgets
from datetime import datetime


class LogPanelWidget(QtWidgets.QFrame):
    """Painel de log reutilizável com métodos append/clear/copy."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            """
            QFrame{background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 rgba(20,20,22,240), stop:1 rgba(12,12,14,240));
                   border:1px solid rgba(159,89,255,0.15);border-radius:12px;}
            """
        )
        v = QtWidgets.QVBoxLayout(self); v.setContentsMargins(14, 10, 14, 12); v.setSpacing(8)

        h = QtWidgets.QHBoxLayout(); h.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QtWidgets.QLabel("📋"); icon_lbl.setStyleSheet("font-size:16px;")
        lbl = QtWidgets.QLabel("Log de Atividades"); lbl.setStyleSheet("color:#f0f0f0;font-size:14px;font-weight:600;letter-spacing:0.3px;")
        h.addWidget(icon_lbl); h.addWidget(lbl); h.addStretch()

        btn_clear = QtWidgets.QPushButton("Limpar"); btn_clear.setCursor(QtCore.Qt.CursorShape.PointingHandCursor); btn_clear.setFixedHeight(26)
        btn_clear.setStyleSheet(
            """
            QPushButton{background:rgba(255,255,255,0.04);color:#cfcfcf;border:1px solid rgba(255,255,255,0.08);border-radius:7px;padding:4px 12px;font-size:11px;font-weight:500;}
            QPushButton:hover{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);color:#ffffff;}
            QPushButton:pressed{background:rgba(255,255,255,0.06);}
            """
        ); btn_clear.clicked.connect(self.clear_logs)

        btn_copy = QtWidgets.QPushButton("Copiar Logs"); btn_copy.setCursor(QtCore.Qt.CursorShape.PointingHandCursor); btn_copy.setFixedHeight(26)
        btn_copy.setStyleSheet(
            """
            QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #b987ff, stop:1 #9f59ff);color:#ffffff;border:none;border-radius:7px;padding:4px 14px;font-size:11px;font-weight:600;letter-spacing:0.3px;}
            QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c99bff, stop:1 #af6bff);} 
            QPushButton:pressed{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #a975ff, stop:1 #8f47ff);}
            """
        ); btn_copy.clicked.connect(self.copy_logs)

        h.addWidget(btn_clear); h.addWidget(btn_copy); v.addLayout(h)

        separator = QtWidgets.QFrame(); separator.setFixedHeight(1); separator.setStyleSheet("background:rgba(159,89,255,0.1);")
        v.addWidget(separator)

        self.status_box = QtWidgets.QTextEdit(); self.status_box.setReadOnly(True); self.status_box.setFixedHeight(115)
        self.status_box.setStyleSheet(
            """
            QTextEdit{background:rgba(0,0,0,0.25);color:#e8e8e8;border:1px solid rgba(255,255,255,0.03);border-radius:8px;padding:10px;font-family:'Consolas','Courier New',monospace;font-size:11px;selection-background-color:rgba(159,89,255,0.3);} 
            QScrollBar:vertical{background:transparent;width:8px;margin:2px;border-radius:4px;} 
            QScrollBar::handle:vertical{background:rgba(180,120,255,0.6);min-height:20px;border-radius:4px;} 
            QScrollBar::handle:vertical:hover{background:rgba(180,120,255,0.9);} 
            QScrollBar::add-line,QScrollBar::sub-line{height:0;}
            """
        )
        self.status_box.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.status_box.setPlaceholderText("Nenhuma atividade registrada ainda...")
        v.addWidget(self.status_box)
        self.setFixedHeight(190)

    # API pública
    def append(self, msg: str) -> None:
        try:
            ts = datetime.now().strftime('%H:%M:%S')
            self.status_box.append(f"[{ts}] {msg}")
        except Exception:
            pass

    def clear_logs(self) -> None:
        try:
            self.status_box.clear()
            self.append('Logs limpos.')
        except Exception:
            pass

    def copy_logs(self) -> None:
        try:
            QtWidgets.QApplication.clipboard().setText(self.status_box.toPlainText())
            self.append('Logs copiados para a área de transferência.')
        except Exception:
            pass
