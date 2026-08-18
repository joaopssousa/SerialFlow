"""Main window do SerialForge - visual completo + backend funcional"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QPlainTextEdit,
    QLabel, QStatusBar, QFileDialog, QMessageBox, QFrame,
    QGridLayout, QStackedWidget, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from datetime import datetime

import re
from app.style import get_stylesheet, COLORS as C, FONTS as F, MONO
from app.serial_backend import SerialBackend
from app.widgets.pill_group import PillGroup
from app.widgets.toggle_row import ToggleRow
from app.widgets.line_indicator import LineIndicator
from app.widgets.commands_view import CommandsView
from app.widgets.triggers_view import TriggersView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SerialForge")
        self.setMinimumSize(1180, 680)

        # Backend serial
        self.serial = SerialBackend()
        self.serial.data_received.connect(self.on_data_received)
        self.serial.lines_changed.connect(self.on_lines_changed)
        self.serial.connected.connect(self.on_connected)
        self.serial.disconnected.connect(self.on_disconnected)
        self.serial.error.connect(self.on_error)

        # Estado
        self.rx_bytes = 0
        self.tx_bytes = 0
        self.display_mode = "ASCII"
        self.show_timestamp = True
        self.show_direction = True
        self.current_utility_view = "triggers"
        self._rx_buffer = b""
        self._rx_flush_timer = QTimer(self)
        self._rx_flush_timer.setSingleShot(True)
        self._rx_flush_timer.setInterval(50)
        self._rx_flush_timer.timeout.connect(self._flush_rx_buffer)

        # Aplica tema
        self.setStyleSheet(get_stylesheet())

        self._build_ui()
        self._refresh_ports()
        self._set_utility_view("triggers")
        self._set_utility_panel_visible(False)

    def _build_ui(self):
        """Constrói a interface"""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = self._build_toolbar()
        layout.addWidget(toolbar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        sidebar = self._build_sidebar()
        right_panel = self._build_right_panel()

        body.addWidget(sidebar)
        body.addWidget(self._vdivider())
        body.addWidget(right_panel, stretch=1)

        layout.addLayout(body, stretch=1)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self._update_statusbar()

    def _build_toolbar(self):
        """Toolbar superior"""
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(46)
        # Seletor por objectName: sem ele o estilo cascatearia para os filhos
        toolbar.setStyleSheet(
            f"#toolbar {{ background-color: {C['bg_panel']}; "
            f"border-bottom: 1px solid {C['border']}; }}"
        )

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(4)

        self.btn_connect = QPushButton("⏺  Conectar")
        self.btn_connect.setObjectName("btn_connect")
        self.btn_connect.setFixedHeight(30)
        self.btn_connect.clicked.connect(self.on_connect_clicked)

        self.btn_disconnect = QPushButton("⏹  Desconectar")
        self.btn_disconnect.setObjectName("btn_disconnect")
        self.btn_disconnect.setFixedHeight(30)
        self.btn_disconnect.clicked.connect(self.on_disconnect_clicked)
        self.btn_disconnect.setEnabled(False)

        self.btn_clear = QPushButton("↺  Limpar")
        self.btn_clear.setFixedHeight(30)
        self.btn_clear.clicked.connect(self.on_clear_clicked)

        self.btn_save = QPushButton("↓  Salvar Log")
        self.btn_save.setFixedHeight(30)
        self.btn_save.clicked.connect(self.on_save_clicked)

        self.btn_toggle_triggers = QPushButton("⚡ Triggers")
        self.btn_toggle_triggers.setCheckable(True)
        self.btn_toggle_triggers.setFixedHeight(30)
        self.btn_toggle_triggers.clicked.connect(lambda: self._toggle_utility_panel("triggers"))

        self.btn_toggle_commands = QPushButton("⌘ Comandos")
        self.btn_toggle_commands.setCheckable(True)
        self.btn_toggle_commands.setFixedHeight(30)
        self.btn_toggle_commands.clicked.connect(lambda: self._toggle_utility_panel("commands"))

        layout.addWidget(self.btn_connect)
        layout.addWidget(self.btn_disconnect)
        layout.addWidget(self._sep())
        layout.addWidget(self.btn_clear)
        layout.addWidget(self.btn_save)
        layout.addWidget(self._sep())
        layout.addWidget(self.btn_toggle_triggers)
        layout.addWidget(self.btn_toggle_commands)
        layout.addStretch()

        self.status_chip = QLabel("● DESCONECTADO")
        self.status_chip.setStyleSheet(self._chip_style("#2d0a0f", "#ff6b7a", "#5c1520"))
        layout.addWidget(self.status_chip)

        return toolbar

    def _build_sidebar(self):
        """Sidebar com configurações"""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet(f"#sidebar {{ background-color: {C['bg_panel']}; }}")

        outer = QVBoxLayout(sidebar)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header de 40px igual aos painéis da direita: a linha divisória
        # horizontal abaixo dele fica contínua pela janela inteira
        header = QWidget()
        header.setObjectName("sidebar_header")
        header.setFixedHeight(40)
        header.setStyleSheet(
            f"#sidebar_header {{ background-color: {C['bg_panel']}; "
            f"border-bottom: 1px solid {C['border']}; }}"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 12, 0)
        lbl_header = QLabel("Configuração")
        lbl_header.setStyleSheet(
            f"color: {C['text_primary']}; font-size: {F['title']}px; font-weight: bold;"
        )
        header_layout.addWidget(lbl_header)
        header_layout.addStretch()
        outer.addWidget(header)

        # Seções dentro de um scroll: em janelas baixas a sidebar rola em vez
        # de comprimir e sobrepor os widgets
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        port_section = self._section("Porta Serial")
        port_layout = QVBoxLayout()
        port_layout.setSpacing(8)

        port_row = QHBoxLayout()
        self.combo_port = QComboBox()
        self.btn_refresh = QPushButton("↺")
        self.btn_refresh.setFixedSize(41, 34)
        self.btn_refresh.clicked.connect(self._refresh_ports)
        port_row.addWidget(self.combo_port)
        port_row.addWidget(self.btn_refresh)
        port_layout.addLayout(port_row)

        port_section.layout().addLayout(port_layout)
        layout.addWidget(port_section)

        params_section = self._section("Parâmetros")
        grid = QGridLayout()
        grid.setSpacing(8)

        grid.addWidget(self._param_label("Baudrate"), 0, 0)
        self.combo_baud = QComboBox()
        self.combo_baud.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.combo_baud.setCurrentText("115200")
        grid.addWidget(self.combo_baud, 1, 0)

        grid.addWidget(self._param_label("Data Bits"), 0, 1)
        self.combo_data = QComboBox()
        self.combo_data.addItems(["5", "6", "7", "8"])
        self.combo_data.setCurrentText("8")
        grid.addWidget(self.combo_data, 1, 1)

        grid.addWidget(self._param_label("Paridade"), 2, 0)
        self.combo_parity = QComboBox()
        self.combo_parity.addItems(["Nenhuma", "Par", "Ímpar"])
        grid.addWidget(self.combo_parity, 3, 0)

        grid.addWidget(self._param_label("Stop Bits"), 2, 1)
        self.combo_stop = QComboBox()
        self.combo_stop.addItems(["1", "1.5", "2"])
        grid.addWidget(self.combo_stop, 3, 1)

        params_section.layout().addLayout(grid)

        self.toggle_rtscts = ToggleRow("Flow Control RTS/CTS", checked=False)
        self.toggle_rtscts.toggled.connect(self._on_rtscts_toggled)
        params_section.layout().addWidget(self.toggle_rtscts)

        layout.addWidget(params_section)

        lines_section = self._section("Linhas de Controle")
        leds_row = QHBoxLayout()
        leds_row.setSpacing(4)

        self._line_leds = {}
        for key, label, is_output in (
            ("rts", "RTS", True),
            ("dtr", "DTR", True),
            ("cts", "CTS", False),
            ("dsr", "DSR", False),
            ("cd",  "DCD", False),
            ("ri",  "RI",  False),
        ):
            led = LineIndicator(label, output=is_output)
            if is_output:
                led.clicked.connect(lambda k=key: self._on_line_clicked(k))
            self._line_leds[key] = led
            leds_row.addWidget(led)
        leds_row.addStretch()

        lines_section.layout().addLayout(leds_row)
        layout.addWidget(lines_section)

        display_section = self._section("Modo de Exibição")
        display_layout = QVBoxLayout()
        display_layout.setSpacing(6)

        self.pill_mode = PillGroup(["ASCII", "HEX"])
        self.pill_mode.selection_changed.connect(self.on_display_mode_changed)
        display_layout.addWidget(self.pill_mode)

        self.toggle_timestamp = ToggleRow("Mostrar Timestamp", checked=True)
        self.toggle_timestamp.toggled.connect(lambda v: setattr(self, 'show_timestamp', v))
        display_layout.addWidget(self.toggle_timestamp)

        self.toggle_direction = ToggleRow("Mostrar Direção TX/RX", checked=True)
        self.toggle_direction.toggled.connect(lambda v: setattr(self, 'show_direction', v))
        display_layout.addWidget(self.toggle_direction)

        self.toggle_autoscroll = ToggleRow("Auto-scroll", checked=True)
        display_layout.addWidget(self.toggle_autoscroll)

        display_section.layout().addLayout(display_layout)
        layout.addWidget(display_section)

        stats_section = self._section("Estatísticas")
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)

        rx_card = self._stat_card("Recebido", C['accent'])
        self.lbl_rx = rx_card.findChild(QLabel, "stat_value")

        tx_card = self._stat_card("Enviado", C['green'])
        self.lbl_tx = tx_card.findChild(QLabel, "stat_value")

        stats_row.addWidget(rx_card)
        stats_row.addWidget(tx_card)
        stats_section.layout().addLayout(stats_row)
        layout.addWidget(stats_section)

        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        scroll.setWidget(content)
        outer.addWidget(scroll, stretch=1)

        return sidebar

    def _build_right_panel(self):
        """Painel principal com conteúdo e utilidades"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        main_area = QWidget()
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        content_header = self._build_content_header()
        main_layout.addWidget(content_header)

        main_layout.addWidget(self._build_log_view(), stretch=1)

        send_bar = self._build_send_bar()
        main_layout.addWidget(send_bar)

        self.utility_panel = self._build_utility_panel()
        self.utility_divider = self._vdivider()

        layout.addWidget(main_area, stretch=1)
        layout.addWidget(self.utility_divider)
        layout.addWidget(self.utility_panel)
        return panel

    def _build_content_header(self):
        bar = QWidget()
        bar.setObjectName("content_header")
        bar.setFixedHeight(40)
        bar.setStyleSheet(
            f"#content_header {{ background-color: {C['bg_panel']}; "
            f"border-bottom: 1px solid {C['border']}; }}"
        )

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(0)

        lbl_title = QLabel("Log de Comunicação")
        lbl_title.setStyleSheet(
            f"color: {C['accent']}; font-size: {F['base']}px; "
            f"border-bottom: 2px solid {C['accent']}; padding: 0 18px;"
        )
        lbl_title.setFixedHeight(40)

        layout.addWidget(lbl_title)
        layout.addStretch()

        self.lbl_context_hint = QLabel("Monitoramento em tempo real")
        self.lbl_context_hint.setStyleSheet(f"color: {C['text_muted']}; font-size: {F['small']}px;")
        layout.addWidget(self.lbl_context_hint)

        return bar

    def _build_log_view(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.log_stack = QStackedWidget()

        empty = QWidget()
        empty_layout = QVBoxLayout(empty)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_icon = QLabel("📡")
        empty_icon.setStyleSheet("font-size: 36px;")
        empty_icon.setAlignment(Qt.AlignCenter)
        empty_title = QLabel("Aguardando conexão...")
        empty_title.setStyleSheet(f"color: {C['text_secondary']}; font-size: {F['title']}px;")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_sub = QLabel("Selecione uma porta e clique em Conectar")
        empty_sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {F['small']}px;")
        empty_sub.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_sub)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(
            "padding: 12px; background: transparent; border: none;"
        )

        self.log_stack.addWidget(empty)
        self.log_stack.addWidget(self.log)
        layout.addWidget(self.log_stack, stretch=1)
        return container

    def _build_utility_panel(self):
        panel = QWidget()
        panel.setObjectName("utility_panel")
        panel.setFixedWidth(360)
        panel.setStyleSheet(f"#utility_panel {{ background-color: {C['bg_panel']}; }}")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("utility_header")
        header.setFixedHeight(40)
        header.setStyleSheet(f"#utility_header {{ border-bottom: 1px solid {C['border']}; }}")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 0, 12, 0)

        self.lbl_utility_title = QLabel("Triggers")
        self.lbl_utility_title.setStyleSheet(f"color: {C['text_primary']}; font-size: {F['title']}px; font-weight: bold;")

        self.btn_hide_utility = QPushButton("×")
        self.btn_hide_utility.setFixedSize(28, 28)
        # O padding global de QPushButton (6px 14px) não deixa área útil num
        # botão de 28px e o glifo some
        self.btn_hide_utility.setStyleSheet(
            f"QPushButton {{ padding: 0; border: 1px solid {C['border_bright']}; "
            f"border-radius: 6px; color: {C['text_secondary']}; background: transparent; }}"
            f"QPushButton:hover {{ background: {C['bg_raised']}; color: {C['text_primary']}; }}"
        )
        self.btn_hide_utility.clicked.connect(lambda: self._set_utility_panel_visible(False))

        header_layout.addWidget(self.lbl_utility_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_hide_utility)
        layout.addWidget(header)

        switcher = QWidget()
        switcher_layout = QHBoxLayout(switcher)
        switcher_layout.setContentsMargins(20, 20, 20, 8)
        switcher_layout.setSpacing(6)

        self.btn_panel_triggers = QPushButton("Triggers")
        self.btn_panel_triggers.setCheckable(True)
        self.btn_panel_triggers.setFixedHeight(30)
        self.btn_panel_triggers.clicked.connect(lambda: self._set_utility_view("triggers"))

        self.btn_panel_commands = QPushButton("Comandos")
        self.btn_panel_commands.setCheckable(True)
        self.btn_panel_commands.setFixedHeight(30)
        self.btn_panel_commands.clicked.connect(lambda: self._set_utility_view("commands"))

        switcher_layout.addWidget(self.btn_panel_triggers)
        switcher_layout.addWidget(self.btn_panel_commands)
        layout.addWidget(switcher)

        self.utility_stack = QStackedWidget()
        self.utility_stack.addWidget(self._build_triggers_view())
        self.utility_stack.addWidget(self._build_commands_view())
        layout.addWidget(self.utility_stack, stretch=1)
        return panel

    def _build_triggers_view(self):
        self._triggers_view = TriggersView(
            get_commands=lambda: self._commands_view._commands if hasattr(self, '_commands_view') else []
        )
        return self._triggers_view

    def _build_commands_view(self):
        self._commands_view = CommandsView()
        self._commands_view.send_frame.connect(self._on_command_send)
        return self._commands_view

    def _build_send_bar(self):
        bar = QWidget()
        bar.setObjectName("send_bar")
        bar.setFixedHeight(54)
        bar.setStyleSheet(
            f"#send_bar {{ background-color: {C['bg_panel']}; border-top: 1px solid {C['border']}; }}"
        )

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 10, 12, 10)

        self.input_send = QLineEdit()
        self.input_send.setFixedHeight(34)
        self._update_send_placeholder()
        self.input_send.returnPressed.connect(self.on_send_clicked)

        self.btn_send = QPushButton("➤  Enviar")
        self.btn_send.setFixedSize(100, 34)
        self.btn_send.setStyleSheet(
            f"QPushButton {{ background-color: {C['accent']}; color: {C['bg_deep']}; "
            f"border: none; font-weight: bold; border-radius: 6px; padding: 0 14px; }}"
            f"QPushButton:hover {{ background-color: #33dbff; }}"
            f"QPushButton:disabled {{ background-color: {C['bg_raised']}; "
            f"color: {C['text_muted']}; border: 1px solid {C['border_bright']}; }}"
        )
        self.btn_send.clicked.connect(self.on_send_clicked)
        self.btn_send.setEnabled(False)

        layout.addWidget(self.input_send, stretch=1)
        layout.addWidget(self.btn_send)
        return bar

    # ── Helpers UI ───────────────────────────────────────────────────────────

    def _section(self, title):
        section = QWidget()
        section.setObjectName("section")
        # Seletor por objectName: sem ele o border-bottom cascatearia para os filhos
        section.setStyleSheet(f"#section {{ border-bottom: 1px solid {C['border']}; }}")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 2)
        header_layout.setSpacing(8)

        bar = QFrame()
        bar.setObjectName("section_bar")
        bar.setFixedSize(2, 11)
        bar.setStyleSheet(f"#section_bar {{ background-color: {C['accent']}; border-radius: 1px; }}")

        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            f"color: {C['text_secondary']}; font-size: {F['label']}px; letter-spacing: 2px; font-weight: bold;"
        )

        header_layout.addWidget(bar)
        header_layout.addWidget(lbl)
        header_layout.addStretch()

        layout.addWidget(header)
        return section

    def _param_label(self, text):
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: {F['label']}px; letter-spacing: 1px;")
        return lbl

    def _stat_card(self, label, color):
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {C['bg_surface']}; "
            f"border: 1px solid {C['border']}; "
            f"border-radius: 6px;"
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: {F['label']}px; letter-spacing: 1px; border: none;")

        value = QLabel("0 B")
        value.setObjectName("stat_value")
        value.setStyleSheet(f"color: {color}; font-size: {F['stat']}px; font-weight: bold; border: none;")

        layout.addWidget(lbl)
        layout.addWidget(value)
        return card

    def _info_card(self, title, text):
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {C['bg_surface']}; border: 1px solid {C['border']}; border-radius: 10px;"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {C['text_primary']}; font-size: {F['title']}px; font-weight: bold;")

        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setStyleSheet(f"color: {C['text_secondary']}; font-size: {F['base']}px;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_text)
        return card

    def _ghost_block(self, title, text):
        block = QFrame()
        block.setStyleSheet(
            f"background-color: transparent; border: 1px dashed {C['border_bright']}; border-radius: 10px;"
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet(f"color: {C['text_muted']}; font-size: {F['label']}px; letter-spacing: 1px; font-weight: bold;")

        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setStyleSheet(f"color: {C['text_secondary']}; font-size: {F['base']}px;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_text)
        return block

    @staticmethod
    def _chip_style(bg, fg, border):
        return (
            f"background-color: {bg}; color: {fg}; "
            f"border: 1px solid {border}; border-radius: 10px; "
            f"padding: 4px 10px; font-size: {F['small']}px; letter-spacing: 1px;"
        )

    def _vdivider(self):
        # Divisória vertical como widget próprio: nenhum filho pinta por cima
        d = QFrame()
        d.setFixedWidth(1)
        d.setStyleSheet(f"background-color: {C['border']};")
        return d

    def _sep(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(22)
        sep.setStyleSheet(f"color: {C['border_bright']}; margin: 0 6px;")
        return sep

    def _set_utility_view(self, view_name):
        self.current_utility_view = view_name
        is_triggers = view_name == "triggers"
        self.utility_stack.setCurrentIndex(0 if is_triggers else 1)
        self.btn_panel_triggers.setChecked(is_triggers)
        self.btn_panel_commands.setChecked(not is_triggers)
        self.lbl_utility_title.setText("Triggers" if is_triggers else "Comandos")
        self.btn_toggle_triggers.setChecked(is_triggers and self.utility_panel.isVisible())
        self.btn_toggle_commands.setChecked((not is_triggers) and self.utility_panel.isVisible())

    def _set_utility_panel_visible(self, visible):
        self.utility_panel.setVisible(visible)
        self.utility_divider.setVisible(visible)
        self.btn_toggle_triggers.setChecked(visible and self.current_utility_view == "triggers")
        self.btn_toggle_commands.setChecked(visible and self.current_utility_view == "commands")

    def _toggle_utility_panel(self, target_view):
        if self.utility_panel.isVisible() and self.current_utility_view == target_view:
            self._set_utility_panel_visible(False)
            return
        self._set_utility_view(target_view)
        self._set_utility_panel_visible(True)

    def _refresh_ports(self):
        ports = SerialBackend.list_ports()
        self.combo_port.clear()
        self.combo_port.insertItem(0, "loop:// (teste interno)")
        if ports:
            self.combo_port.addItems(ports)
        else:
            self.combo_port.addItem("(nenhuma porta)")

    # ── Handlers ─────────────────────────────────────────────────────────────

    def on_connect_clicked(self):
        port = self.combo_port.currentText()
        if port in ("(nenhuma porta)", ""):
            return

        if port.startswith("loop://"):
            port = "loop://"


        baudrate = int(self.combo_baud.currentText())
        bytesize = int(self.combo_data.currentText())
        parity_map = {"Nenhuma": "N", "Par": "E", "Ímpar": "O"}
        parity = parity_map.get(self.combo_parity.currentText(), "N")
        stopbits = float(self.combo_stop.currentText())
        rtscts = self.toggle_rtscts.isChecked()
        self.serial.connect(port, baudrate, bytesize, parity, stopbits, rtscts)

    def on_disconnect_clicked(self):
        self.serial.disconnect()

    def on_clear_clicked(self):
        self.log.clear()
        self.rx_bytes = 0
        self.tx_bytes = 0
        self._rx_buffer = b""
        self._rx_flush_timer.stop()
        self._update_stats()
        self.log_stack.setCurrentIndex(0)

    def on_save_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Log", "", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log.toPlainText())

    def on_send_clicked(self):
        text = self.input_send.text()
        if not text:
            return

        if self.display_mode == "HEX":
            try:
                data = bytes.fromhex(text.replace(" ", ""))
            except ValueError:
                self._flash_send_error(
                    "Frame HEX inválido — use pares hexadecimais (ex: 0A 4E FF 0D)"
                )
                return
            if not data:
                return
        else:
            text = text.replace("\\n", "\n").replace("\\r", "\r")
            text = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), text)
            data = text.encode('latin-1', errors='replace')

        self.serial.write(data)
        self.append_tx(data)
        self.input_send.clear()

        self.tx_bytes += len(data)
        self._update_stats()

    def _on_command_send(self, data: bytes):
        if not (self.serial.serial_port and self.serial.serial_port.is_open):
            return
        self.serial.write(data)
        self.append_tx(data)
        self.tx_bytes += len(data)
        self._update_stats()

    def on_display_mode_changed(self, mode):
        self.display_mode = mode
        self._update_send_placeholder()

    def _update_send_placeholder(self):
        if self.display_mode == "HEX":
            self.input_send.setPlaceholderText("Enviar frame em HEX... (ex: 0A 4E 30 2C 0D)")
        else:
            self.input_send.setPlaceholderText("Enviar frame manual... (suporta \\n \\r \\xNN)")

    def _flash_send_error(self, msg):
        self.input_send.setStyleSheet(f"QLineEdit {{ border: 1px solid {C['red']}; }}")
        self.statusbar.showMessage(f"⚠ {msg}")
        QTimer.singleShot(1800, lambda: self.input_send.setStyleSheet(""))
        QTimer.singleShot(3500, self._update_statusbar)

    # ── Linhas de controle ───────────────────────────────────────────────────

    def _on_rtscts_toggled(self, enabled):
        # Com flow control por hardware o driver assume o RTS: bloqueia o manual
        self.serial.set_flow_control(enabled)
        connected = bool(self.serial.serial_port and self.serial.serial_port.is_open)
        self._line_leds["rts"].setLineEnabled(connected and not enabled)
        self._update_statusbar()

    def _on_line_clicked(self, line):
        if not (self.serial.serial_port and self.serial.serial_port.is_open):
            return
        if line == "rts" and self.toggle_rtscts.isChecked():
            return
        new_state = not self._line_leds[line].isOn()
        if line == "rts":
            self.serial.set_rts(new_state)
        else:
            self.serial.set_dtr(new_state)
        self._line_leds[line].setOn(new_state)

    def on_lines_changed(self, lines):
        for key, led in self._line_leds.items():
            led.setOn(lines.get(key, False))

    def _set_leds_connected(self, connected):
        for key, led in self._line_leds.items():
            if key == "rts":
                led.setLineEnabled(connected and not self.toggle_rtscts.isChecked())
            else:
                led.setLineEnabled(connected)
            if not connected:
                led.setOn(False)
        if connected:
            lines = self.serial.get_lines()
            if lines:
                self.on_lines_changed(lines)

    # ── Serial callbacks ─────────────────────────────────────────────────────

    def on_data_received(self, data):
        self.log_stack.setCurrentIndex(1)
        self.append_rx(data)
        self.rx_bytes += len(data)
        self._update_stats()

    def on_connected(self, port):
        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)
        self.btn_send.setEnabled(True)

        self.status_chip.setText(f"● CONECTADO  {port}")
        self.status_chip.setStyleSheet(self._chip_style("#0a2918", "#33ffaa", "#1a5c35"))

        self.log_stack.setCurrentIndex(1)
        self._set_leds_connected(True)
        self.append_info(f"Conectado em {port}")
        self._update_statusbar()

    def on_disconnected(self):
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.btn_send.setEnabled(False)

        self.status_chip.setText("● DESCONECTADO")
        self.status_chip.setStyleSheet(self._chip_style("#2d0a0f", "#ff6b7a", "#5c1520"))

        self._set_leds_connected(False)
        self.append_info("Desconectado")
        self._update_statusbar()

    def closeEvent(self, event):
        # Encerra a thread do reader antes de sair; sem isso o Qt aborta
        # com "QThread: Destroyed while thread is still running"
        if self.serial.serial_port and self.serial.serial_port.is_open:
            self.serial.disconnect()
        super().closeEvent(event)

    def on_error(self, msg):
        QMessageBox.critical(self, "Erro Serial", msg)
        self.append_info(f"ERRO: {msg}")

    # ── Log formatado ────────────────────────────────────────────────────────

    def append_rx(self, data):
        self._rx_buffer += data
        self._rx_flush_timer.stop()

        while True:
            nl = self._rx_buffer.find(b'\n')
            if nl == -1:
                if len(self._rx_buffer) > 512:
                    self._write_rx_line(self._rx_buffer)
                    self._rx_buffer = b""
                elif self._rx_buffer:
                    self._rx_flush_timer.start()
                break
            line = self._rx_buffer[:nl].rstrip(b'\r')
            self._rx_buffer = self._rx_buffer[nl + 1:]
            self._write_rx_line(line)

    def _flush_rx_buffer(self):
        if self._rx_buffer:
            self._write_rx_line(self._rx_buffer)
            self._rx_buffer = b""

    def _write_rx_line(self, line_data):
        fired = self._check_triggers(line_data)

        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)

        if self.show_timestamp:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
            fmt_ts = QTextCharFormat()
            fmt_ts.setForeground(QColor(C['text_muted']))
            cursor.insertText(f"{ts}  ", fmt_ts)

        if self.show_direction:
            fmt_rx = QTextCharFormat()
            fmt_rx.setForeground(QColor(C['accent']))
            fmt_rx.setFontWeight(QFont.Bold)
            cursor.insertText("RX  ", fmt_rx)

        fmt_data = QTextCharFormat()
        if fired:
            action = fired.get("action")
            if action == "highlight":
                bg = fired.get("highlight_color", "#ffaa00")
                fmt_data.setBackground(QColor(bg))
                fmt_data.setForeground(QColor("#0a0c10"))
                fmt_data.setFontWeight(QFont.Bold)
            elif action == "stop":
                fmt_data.setBackground(QColor(C['red']))
                fmt_data.setForeground(QColor("#0a0c10"))
                fmt_data.setFontWeight(QFont.Bold)
            else:
                fmt_data.setForeground(QColor(C['text_primary']))
        else:
            fmt_data.setForeground(QColor(C['text_primary']))

        cursor.insertText(f"{self._format_data(line_data)}\n", fmt_data)

        if fired:
            action = fired.get("action")
            if action == "newline":
                cursor.insertText("\n", QTextCharFormat())
            elif action == "send_command":
                self._send_trigger_command(fired.get("command_name", ""))
            elif action == "stop":
                self.serial.disconnect()

        self.log.setTextCursor(cursor)
        if self.toggle_autoscroll.isChecked():
            self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def _check_triggers(self, line_data):
        if not hasattr(self, '_triggers_view'):
            return None
        for trigger in self._triggers_view.get_triggers():
            if not trigger.get("enabled", True):
                continue
            if self._match_trigger(trigger, line_data):
                return trigger
        return None

    def _match_trigger(self, trigger, line_data):
        match_format = trigger.get("match_format", "ASCII")
        match_type   = trigger.get("match_type", "contains")
        pattern      = trigger.get("pattern", "")

        if not pattern:
            return False

        if match_format == "HEX":
            subject = ' '.join(f'{b:02X}' for b in line_data).upper()
            pattern = pattern.upper()
        else:
            subject = line_data.decode('latin-1', errors='replace')

        try:
            if match_type == "contains":
                return pattern in subject
            elif match_type == "equals":
                return pattern == subject
            elif match_type == "starts_with":
                return subject.startswith(pattern)
            elif match_type == "ends_with":
                return subject.endswith(pattern)
            elif match_type == "regex":
                return bool(re.search(pattern, subject))
        except Exception:
            return False
        return False

    def _send_trigger_command(self, command_name):
        if not hasattr(self, '_commands_view'):
            return
        if not (self.serial.serial_port and self.serial.serial_port.is_open):
            return
        for cmd in self._commands_view._commands:
            if cmd.get("name") == command_name:
                payload = cmd.get("payload", "")
                fmt = cmd.get("format", "ASCII")
                try:
                    if fmt == "ASCII":
                        text = payload.replace("\\n", "\n").replace("\\r", "\r")
                        text = re.sub(
                            r'\\x([0-9a-fA-F]{2})',
                            lambda m: chr(int(m.group(1), 16)),
                            text,
                        )
                        data = text.encode("latin-1", errors="replace")
                    else:
                        data = bytes.fromhex(payload.replace(" ", ""))
                    self._on_command_send(data)
                except Exception:
                    pass
                break

    def append_tx(self, data):
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)

        if self.show_timestamp:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
            fmt_ts = QTextCharFormat()
            fmt_ts.setForeground(QColor(C['text_muted']))
            cursor.insertText(f"{ts}  ", fmt_ts)

        if self.show_direction:
            fmt_tx = QTextCharFormat()
            fmt_tx.setForeground(QColor(C['green']))
            fmt_tx.setFontWeight(QFont.Bold)
            cursor.insertText("TX  ", fmt_tx)

        fmt_data = QTextCharFormat()
        fmt_data.setForeground(QColor(C['text_primary']))
        text = self._format_data(data)
        cursor.insertText(f"{text}\n", fmt_data)

        self.log.setTextCursor(cursor)
        if self.toggle_autoscroll.isChecked():
            self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def append_info(self, msg):
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(C['amber']))
        cursor.insertText(f"─ {msg}\n", fmt)

        self.log.setTextCursor(cursor)
        if self.toggle_autoscroll.isChecked():
            self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def _format_data(self, data):
        if self.display_mode == "ASCII":
            return data.decode('latin-1', errors='replace').replace('\r', '\\r').replace('\n', '\\n')
        elif self.display_mode == "HEX":
            return ' '.join(f"{b:02X}" for b in data)
        elif self.display_mode == "Dec":
            return ' '.join(str(b) for b in data)
        elif self.display_mode == "Bin":
            return ' '.join(f"{b:08b}" for b in data)
        return repr(data)

    def _update_stats(self):
        self.lbl_rx.setText(self._fmt_bytes(self.rx_bytes))
        self.lbl_tx.setText(self._fmt_bytes(self.tx_bytes))
        self._update_statusbar()

    def _update_statusbar(self):
        cfg = (
            f"{self.combo_baud.currentText()} bps · {self.combo_data.currentText()}"
            f"{self.combo_parity.currentText()[0]}{self.combo_stop.currentText()}"
        )
        if self.toggle_rtscts.isChecked():
            cfg += " · RTS/CTS"
        self.statusbar.showMessage(
            f"● Porta: {self.combo_port.currentText() if self.combo_port.count() else '---'}  |  "
            f"RX: {self._fmt_bytes(self.rx_bytes)}  |  TX: {self._fmt_bytes(self.tx_bytes)}  |  {cfg}"
        )

    @staticmethod
    def _fmt_bytes(n):
        if n < 1024:
            return f"{n} B"
        elif n < 1024**2:
            return f"{n/1024:.1f} KB"
        return f"{n/1024**2:.1f} MB"
