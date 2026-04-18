"""Main window do SerialForge - visual completo + backend funcional"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QPlainTextEdit,
    QLabel, QStatusBar, QFileDialog, QMessageBox, QFrame,
    QGridLayout, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from datetime import datetime

from app.style import get_stylesheet, COLORS as C
from app.serial_backend import SerialBackend
from app.widgets.pill_group import PillGroup
from app.widgets.toggle_row import ToggleRow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SerialForge")
        self.setMinimumSize(1180, 680)

        # Backend serial
        self.serial = SerialBackend()
        self.serial.data_received.connect(self.on_data_received)
        self.serial.connected.connect(self.on_connected)
        self.serial.disconnected.connect(self.on_disconnected)
        self.serial.error.connect(self.on_error)

        # Estado
        self.rx_bytes = 0
        self.tx_bytes = 0
        self.display_mode = "ASCII"
        self.show_timestamp = True
        self.show_direction = True
        self.current_main_view = "log"
        self.current_utility_view = "triggers"

        # Aplica tema
        self.setStyleSheet(get_stylesheet())

        self._build_ui()
        self._refresh_ports()
        self._set_main_view("log")
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
        body.addWidget(right_panel, stretch=1)

        layout.addLayout(body, stretch=1)

        self.statusbar = QStatusBar()
        self.statusbar.setStyleSheet(
            f"background-color: {C['bg_panel']}; color: {C['text_muted']}; "
            f"border-top: 1px solid {C['border']}; font-size: 10px;"
        )
        self.setStatusBar(self.statusbar)
        self._update_statusbar()

    def _build_toolbar(self):
        """Toolbar superior"""
        toolbar = QWidget()
        toolbar.setFixedHeight(46)
        toolbar.setStyleSheet(
            f"background-color: {C['bg_panel']}; border-bottom: 1px solid {C['border']};"
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
        self.btn_toggle_triggers.setFixedHeight(30)
        self.btn_toggle_triggers.clicked.connect(lambda: self._toggle_utility_panel("triggers"))

        self.btn_toggle_commands = QPushButton("⌘ Comandos")
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
        self.status_chip.setStyleSheet(
            f"background-color: {C['red_dim']}; color: {C['red']}; "
            f"border: 1px solid #ff456633; border-radius: 10px; "
            f"padding: 4px 10px; font-size: 10px; letter-spacing: 1px;"
        )
        layout.addWidget(self.status_chip)

        return toolbar

    def _build_sidebar(self):
        """Sidebar com configurações"""
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet(
            f"background-color: {C['bg_panel']}; border-right: 1px solid {C['border']};"
        )

        layout = QVBoxLayout(sidebar)
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
        layout.addWidget(params_section)

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

        self.main_stack = QStackedWidget()
        self.main_stack.addWidget(self._build_log_view())
        self.main_stack.addWidget(self._build_graph_view())
        main_layout.addWidget(self.main_stack, stretch=1)

        send_bar = self._build_send_bar()
        main_layout.addWidget(send_bar)

        self.utility_panel = self._build_utility_panel()

        layout.addWidget(main_area, stretch=1)
        layout.addWidget(self.utility_panel)
        return panel

    def _build_content_header(self):
        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet(
            f"background-color: {C['bg_panel']}; border-bottom: 1px solid {C['border']};"
        )

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(0)

        self.btn_view_log = QPushButton("Log de Comunicação")
        self.btn_view_log.setCheckable(True)
        self.btn_view_log.setFixedHeight(40)
        self.btn_view_log.clicked.connect(lambda: self._set_main_view("log"))

        self.btn_view_graph = QPushButton("Gráfico")
        self.btn_view_graph.setCheckable(True)
        self.btn_view_graph.setFixedHeight(40)
        self.btn_view_graph.clicked.connect(lambda: self._set_main_view("graph"))

        layout.addWidget(self.btn_view_log)
        layout.addWidget(self.btn_view_graph)
        layout.addStretch()

        self.lbl_context_hint = QLabel("Monitoramento em tempo real")
        self.lbl_context_hint.setStyleSheet(f"color: {C['text_muted']}; font-size: 11px;")
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
        empty_title.setStyleSheet(f"color: {C['text_secondary']}; font-size: 13px;")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_sub = QLabel("Selecione uma porta e clique em Conectar")
        empty_sub.setStyleSheet(f"color: {C['text_muted']}; font-size: 11px;")
        empty_sub.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_sub)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(
            "padding: 12px; font-family: 'Courier New', monospace; background: transparent; border: none;"
        )

        self.log_stack.addWidget(empty)
        self.log_stack.addWidget(self.log)
        layout.addWidget(self.log_stack, stretch=1)
        return container

    def _build_graph_view(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Gráfico")
        title.setStyleSheet(f"color: {C['text_primary']}; font-size: 18px; font-weight: bold;")

        description = QLabel(
            "Deixe esta área para visualizações temporais de RX/TX, throughput ou decodificação.\n"
            "Mantive como visão principal porque faz sentido alternar entre monitoramento textual e visual."
        )
        description.setStyleSheet(f"color: {C['text_secondary']}; font-size: 12px; line-height: 1.5;")
        description.setWordWrap(True)

        card = QFrame()
        card.setStyleSheet(
            f"background-color: {C['bg_panel']}; border: 1px solid {C['border']}; border-radius: 10px;"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(10)

        pill = QLabel("EM BREVE")
        pill.setStyleSheet(
            f"background-color: {C['accent_dim']}; color: {C['accent']}; border-radius: 10px;"
            "padding: 4px 10px; font-size: 10px; font-weight: bold; letter-spacing: 1px;"
        )
        pill.setAlignment(Qt.AlignCenter)
        pill.setFixedWidth(92)

        card_text = QLabel(
            "Sugestão: usar este painel para taxa por segundo, picos de atividade e filtros por direção."
        )
        card_text.setWordWrap(True)
        card_text.setStyleSheet(f"color: {C['text_secondary']}; font-size: 12px;")

        card_layout.addWidget(pill)
        card_layout.addWidget(card_text)
        card_layout.addStretch()

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(card, stretch=1)
        return container

    def _build_utility_panel(self):
        panel = QWidget()
        panel.setFixedWidth(330)
        panel.setStyleSheet(
            f"background-color: {C['bg_panel']}; border-left: 1px solid {C['border']};"
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(40)
        header.setStyleSheet(f"border-bottom: 1px solid {C['border']};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 0, 12, 0)

        self.lbl_utility_title = QLabel("Triggers")
        self.lbl_utility_title.setStyleSheet(f"color: {C['text_primary']}; font-size: 12px; font-weight: bold;")

        self.btn_hide_utility = QPushButton("✕")
        self.btn_hide_utility.setFixedSize(28, 28)
        self.btn_hide_utility.clicked.connect(lambda: self._set_utility_panel_visible(False))

        header_layout.addWidget(self.lbl_utility_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_hide_utility)
        layout.addWidget(header)

        switcher = QWidget()
        switcher_layout = QHBoxLayout(switcher)
        switcher_layout.setContentsMargins(12, 12, 12, 8)
        switcher_layout.setSpacing(6)

        self.btn_panel_triggers = QPushButton("Triggers")
        self.btn_panel_triggers.setCheckable(True)
        self.btn_panel_triggers.setFixedHeight(32)
        self.btn_panel_triggers.clicked.connect(lambda: self._set_utility_view("triggers"))

        self.btn_panel_commands = QPushButton("Comandos")
        self.btn_panel_commands.setCheckable(True)
        self.btn_panel_commands.setFixedHeight(32)
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
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(10)

        info = self._info_card(
            "Automação reativa",
            "Boa para regras como ‘se RX contém X, responder Y’ ou destacar frames importantes sem tirar o foco do log."
        )
        layout.addWidget(info)

        sample = self._ghost_block(
            "Exemplos úteis",
            "• Contém ACK → destacar em verde\n"
            "• Timeout de 3 s → alerta\n"
            "• Match em HEX → enviar resposta automática"
        )
        layout.addWidget(sample)
        layout.addStretch()
        return container

    def _build_commands_view(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(10)

        info = self._info_card(
            "Biblioteca de comandos",
            "Melhor em painel lateral porque costuma ser apoio ao trabalho principal: disparar frames salvos, presets e macros rápidas."
        )
        layout.addWidget(info)

        sample = self._ghost_block(
            "Sugestões de evolução",
            "• Favoritos\n"
            "• Histórico recente\n"
            "• Busca rápida / Ctrl+K\n"
            "• Tags por protocolo ou dispositivo"
        )
        layout.addWidget(sample)
        layout.addStretch()
        return container

    def _build_send_bar(self):
        bar = QWidget()
        bar.setFixedHeight(54)
        bar.setStyleSheet(
            f"background-color: {C['bg_panel']}; border-top: 1px solid {C['border']};"
        )

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 10, 12, 10)

        self.input_send = QLineEdit()
        self.input_send.setPlaceholderText("Enviar frame manual... (suporta \\n \\r \\xNN)")
        self.input_send.setFixedHeight(34)
        self.input_send.returnPressed.connect(self.on_send_clicked)

        self.btn_send = QPushButton("➤  Enviar")
        self.btn_send.setObjectName("btn_send")
        self.btn_send.setFixedHeight(34)
        self.btn_send.clicked.connect(self.on_send_clicked)
        self.btn_send.setEnabled(False)

        layout.addWidget(self.input_send, stretch=1)
        layout.addWidget(self.btn_send)
        return bar

    # ── Helpers UI ───────────────────────────────────────────────────────────

    def _section(self, title):
        section = QWidget()
        section.setStyleSheet(f"border-bottom: 1px solid {C['border']};")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(10)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 4, 0, 4)
        header_layout.setSpacing(8)

        lbl = QLabel(title.upper())
        lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 9px; letter-spacing: 2px; font-weight: bold;")

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {C['border']};")
        line.setFixedHeight(1)

        header_layout.addWidget(lbl)
        header_layout.addWidget(line, stretch=1)

        layout.addWidget(header)
        return section

    def _param_label(self, text):
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 9px; letter-spacing: 1px;")
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
        lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 9px; letter-spacing: 1px; border: none;")

        value = QLabel("0 B")
        value.setObjectName("stat_value")
        value.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold; border: none;")

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
        lbl_title.setStyleSheet(f"color: {C['text_primary']}; font-size: 13px; font-weight: bold;")

        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setStyleSheet(f"color: {C['text_secondary']}; font-size: 12px;")

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
        lbl_title.setStyleSheet(f"color: {C['text_muted']}; font-size: 10px; letter-spacing: 1px; font-weight: bold;")

        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setStyleSheet(f"color: {C['text_secondary']}; font-size: 12px;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_text)
        return block

    def _sep(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(22)
        sep.setStyleSheet(f"color: {C['border_bright']}; margin: 0 6px;")
        return sep

    def _tab_style(self, active):
        color = C['accent'] if active else C['text_muted']
        border = C['accent'] if active else 'transparent'
        return f"""
            QPushButton {{
                color: {color};
                background: transparent;
                border: none;
                border-bottom: 2px solid {border};
                padding: 0 18px;
                font-size: 11px;
                border-radius: 0;
            }}
            QPushButton:hover {{
                color: {C['text_primary'] if not active else C['accent']};
            }}
        """

    def _utility_toggle_style(self, active):
        bg = C['bg_surface'] if active else 'transparent'
        fg = C['text_primary'] if active else C['text_muted']
        border = C['accent'] if active else C['border']
        return (
            f"QPushButton {{background-color: {bg}; color: {fg}; border: 1px solid {border}; "
            f"border-radius: 8px; padding: 0 12px; font-size: 11px; font-weight: 600;}}"
            f"QPushButton:hover {{color: {C['text_primary']}; border: 1px solid {C['accent']};}}"
        )

    def _set_main_view(self, view_name):
        self.current_main_view = view_name
        is_log = view_name == "log"
        self.main_stack.setCurrentIndex(0 if is_log else 1)
        self.btn_view_log.setChecked(is_log)
        self.btn_view_graph.setChecked(not is_log)
        self.btn_view_log.setStyleSheet(self._tab_style(is_log))
        self.btn_view_graph.setStyleSheet(self._tab_style(not is_log))
        self.lbl_context_hint.setText("Monitoramento em tempo real" if is_log else "Visão visual e métricas")

    def _set_utility_view(self, view_name):
        self.current_utility_view = view_name
        is_triggers = view_name == "triggers"
        self.utility_stack.setCurrentIndex(0 if is_triggers else 1)
        self.btn_panel_triggers.setChecked(is_triggers)
        self.btn_panel_commands.setChecked(not is_triggers)
        self.btn_panel_triggers.setStyleSheet(self._utility_toggle_style(is_triggers))
        self.btn_panel_commands.setStyleSheet(self._utility_toggle_style(not is_triggers))
        self.lbl_utility_title.setText("Triggers" if is_triggers else "Comandos")
        self.btn_toggle_triggers.setStyleSheet(self._utility_toggle_style(is_triggers and self.utility_panel.isVisible()))
        self.btn_toggle_commands.setStyleSheet(self._utility_toggle_style((not is_triggers) and self.utility_panel.isVisible()))

    def _set_utility_panel_visible(self, visible):
        self.utility_panel.setVisible(visible)
        self.btn_toggle_triggers.setStyleSheet(
            self._utility_toggle_style(visible and self.current_utility_view == "triggers")
        )
        self.btn_toggle_commands.setStyleSheet(
            self._utility_toggle_style(visible and self.current_utility_view == "commands")
        )

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
        self.serial.connect(port, baudrate, bytesize, parity, stopbits)

    def on_disconnect_clicked(self):
        self.serial.disconnect()

    def on_clear_clicked(self):
        self.log.clear()
        self.rx_bytes = 0
        self.tx_bytes = 0
        self._update_stats()
        self.log_stack.setCurrentIndex(0)
        self._set_main_view("log")

    def on_save_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Log", "", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log.toPlainText())

    def on_send_clicked(self):
        text = self.input_send.text()
        if not text:
            return

        text = text.replace("\\n", "\n").replace("\\r", "\r")
        import re
        text = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), text)

        data = text.encode('latin-1', errors='replace')

        self.serial.write(data)
        self.append_tx(data)
        self.input_send.clear()

        self.tx_bytes += len(data)
        self._update_stats()

    def on_display_mode_changed(self, mode):
        self.display_mode = mode

    # ── Serial callbacks ─────────────────────────────────────────────────────

    def on_data_received(self, data):
        self.log_stack.setCurrentIndex(1)
        self._set_main_view("log")
        self.append_rx(data)
        self.rx_bytes += len(data)
        self._update_stats()

    def on_connected(self, port):
        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)
        self.btn_send.setEnabled(True)

        self.status_chip.setText(f"● CONECTADO  {port}")
        self.status_chip.setStyleSheet(
            f"background-color: {C['green_dim']}; color: {C['green']}; "
            f"border: 1px solid #00ff8833; border-radius: 10px; "
            f"padding: 4px 10px; font-size: 10px; letter-spacing: 1px;"
        )

        self.log_stack.setCurrentIndex(1)
        self._set_main_view("log")
        self.append_info(f"Conectado em {port}")
        self._update_statusbar()

    def on_disconnected(self):
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.btn_send.setEnabled(False)

        self.status_chip.setText("● DESCONECTADO")
        self.status_chip.setStyleSheet(
            f"background-color: {C['red_dim']}; color: {C['red']}; "
            f"border: 1px solid #ff456633; border-radius: 10px; "
            f"padding: 4px 10px; font-size: 10px; letter-spacing: 1px;"
        )

        self.append_info("Desconectado")
        self._update_statusbar()

    def on_error(self, msg):
        QMessageBox.critical(self, "Erro Serial", msg)
        self.append_info(f"ERRO: {msg}")

    # ── Log formatado ────────────────────────────────────────────────────────

    def append_rx(self, data):
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
        fmt_data.setForeground(QColor(C['text_primary']))
        text = self._format_data(data)
        cursor.insertText(f"{text}\n", fmt_data)

        self.log.setTextCursor(cursor)
        if self.toggle_autoscroll.isChecked():
            self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

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
