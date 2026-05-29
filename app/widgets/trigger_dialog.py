"""Dialog de criação/edição de trigger"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QStackedWidget, QWidget
)
from app.style import get_stylesheet, COLORS as C
from app.widgets.pill_group import PillGroup

_HIGHLIGHT_COLORS = [
    ("#ffaa00", "Âmbar"),
    ("#ff4566", "Vermelho"),
    ("#00ff88", "Verde"),
    ("#00d4ff", "Ciano"),
    ("#c084fc", "Roxo"),
    ("#ff7f50", "Laranja"),
]

_MATCH_LABELS = ["contém", "igual", "começa com", "termina com", "regex"]
_MATCH_KEYS   = ["contains", "equals", "starts_with", "ends_with", "regex"]

_ACTION_LABELS = ["Destacar", "Nova linha", "Parar", "Enviar cmd"]
_ACTION_KEYS   = ["highlight", "newline", "stop", "send_command"]


class TriggerDialog(QDialog):
    def __init__(self, trigger=None, commands=None, parent=None):
        super().__init__(parent)
        self._commands = commands or []
        self.setWindowTitle("Editar Trigger" if trigger else "Novo Trigger")
        self.setMinimumWidth(460)
        self.setModal(True)
        self.setStyleSheet(get_stylesheet())
        self._selected_color = _HIGHLIGHT_COLORS[0][0]
        self._build_ui()
        if trigger:
            self._populate(trigger)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self._section_label("Nome"))
        self.input_name = QLineEdit()
        self.input_name.setFixedHeight(34)
        self.input_name.setPlaceholderText("ex: ACK detectado, Erro de CRC")
        layout.addWidget(self.input_name)

        match_row = QHBoxLayout()
        match_row.setSpacing(10)

        col_fmt = QVBoxLayout()
        col_fmt.setSpacing(4)
        col_fmt.addWidget(self._section_label("Formato"))
        self.pill_format = PillGroup(["ASCII", "HEX"])
        self.pill_format.setFixedHeight(34)
        col_fmt.addWidget(self.pill_format)

        col_type = QVBoxLayout()
        col_type.setSpacing(4)
        col_type.addWidget(self._section_label("Tipo de match"))
        self.combo_match = QComboBox()
        self.combo_match.addItems(_MATCH_LABELS)
        self.combo_match.setFixedHeight(34)
        col_type.addWidget(self.combo_match)

        match_row.addLayout(col_fmt, stretch=1)
        match_row.addLayout(col_type, stretch=2)
        layout.addLayout(match_row)

        layout.addWidget(self._section_label("Padrão"))
        self.input_pattern = QLineEdit()
        self.input_pattern.setFixedHeight(34)
        self.input_pattern.setPlaceholderText("ASCII: ACK   |   HEX: FF 00 01")
        layout.addWidget(self.input_pattern)

        layout.addWidget(self._section_label("Ação"))
        self.pill_action = PillGroup(_ACTION_LABELS)
        self.pill_action.setFixedHeight(34)
        self.pill_action.selection_changed.connect(self._on_action_changed)
        layout.addWidget(self.pill_action)

        self.action_stack = QStackedWidget()
        self.action_stack.setFixedHeight(46)

        # Page 0: Highlight — color picker
        page_highlight = QWidget()
        hl_layout = QHBoxLayout(page_highlight)
        hl_layout.setContentsMargins(0, 4, 0, 4)
        hl_layout.setSpacing(6)
        self._color_btns = []
        for hex_color, name in _HIGHLIGHT_COLORS:
            btn = QPushButton()
            btn.setFixedSize(34, 34)
            btn.setToolTip(name)
            btn.clicked.connect(lambda _, c=hex_color: self._select_color(c))
            self._color_btns.append((hex_color, btn))
            hl_layout.addWidget(btn)
        hl_layout.addStretch()
        self.action_stack.addWidget(page_highlight)

        # Page 1: Newline — info text
        page_newline = QWidget()
        nl_layout = QHBoxLayout(page_newline)
        nl_layout.setContentsMargins(0, 4, 0, 4)
        lbl_nl = QLabel("Uma linha em branco será inserida após o frame no log.")
        lbl_nl.setStyleSheet(f"color: {C['text_muted']}; font-size: 11px;")
        lbl_nl.setWordWrap(True)
        nl_layout.addWidget(lbl_nl)
        self.action_stack.addWidget(page_newline)

        # Page 2: Stop — info text
        page_stop = QWidget()
        st_layout = QHBoxLayout(page_stop)
        st_layout.setContentsMargins(0, 4, 0, 4)
        lbl_st = QLabel("A comunicação serial será encerrada ao receber este frame.")
        lbl_st.setStyleSheet(f"color: {C['red']}; font-size: 11px;")
        lbl_st.setWordWrap(True)
        st_layout.addWidget(lbl_st)
        self.action_stack.addWidget(page_stop)

        # Page 3: Send command — command selector
        page_cmd = QWidget()
        cmd_layout = QHBoxLayout(page_cmd)
        cmd_layout.setContentsMargins(0, 4, 0, 4)
        cmd_layout.setSpacing(8)
        lbl_cmd = QLabel("Comando:")
        lbl_cmd.setStyleSheet(f"color: {C['text_secondary']}; font-size: 12px;")
        self.combo_command = QComboBox()
        self.combo_command.setFixedHeight(34)
        for cmd in self._commands:
            self.combo_command.addItem(cmd.get("name", ""), cmd)
        if not self._commands:
            self.combo_command.addItem("(nenhum comando cadastrado)")
        cmd_layout.addWidget(lbl_cmd)
        cmd_layout.addWidget(self.combo_command, stretch=1)
        self.action_stack.addWidget(page_cmd)

        layout.addWidget(self.action_stack)

        # Select first color
        self._select_color(_HIGHLIGHT_COLORS[0][0])

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(34)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Salvar")
        btn_save.setFixedHeight(34)
        btn_save.setStyleSheet(
            f"QPushButton {{ background-color: {C['accent_dim']}; color: {C['accent']}; "
            f"border: 1px solid {C['accent']}44; border-radius: 6px; padding: 0 20px; font-weight: bold; }}"
            f"QPushButton:hover {{ background-color: {C['accent']}33; }}"
        )
        btn_save.clicked.connect(self.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _section_label(self, text):
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 9px; letter-spacing: 1px; background: transparent;"
        )
        return lbl

    def _on_action_changed(self, label):
        idx = _ACTION_LABELS.index(label) if label in _ACTION_LABELS else 0
        self.action_stack.setCurrentIndex(idx)

    def _select_color(self, hex_color):
        self._selected_color = hex_color
        for color, btn in self._color_btns:
            selected = color == hex_color
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {color}; border-radius: 6px; "
                f"border: 3px solid {'white' if selected else 'transparent'}; }}"
                f"QPushButton:hover {{ border-color: {C['text_primary']}; }}"
            )

    def _populate(self, trigger):
        self.input_name.setText(trigger.get("name", ""))

        if trigger.get("match_format", "ASCII") == "HEX":
            self.pill_format._group.button(1).setChecked(True)
            self.pill_format._on_clicked(1)

        mt = trigger.get("match_type", "contains")
        if mt in _MATCH_KEYS:
            self.combo_match.setCurrentIndex(_MATCH_KEYS.index(mt))

        self.input_pattern.setText(trigger.get("pattern", ""))

        action = trigger.get("action", "highlight")
        if action in _ACTION_KEYS:
            idx = _ACTION_KEYS.index(action)
            self.pill_action._group.button(idx).setChecked(True)
            self.pill_action._on_clicked(idx)
            self.action_stack.setCurrentIndex(idx)

        if action == "highlight":
            self._select_color(trigger.get("highlight_color", _HIGHLIGHT_COLORS[0][0]))

        if action == "send_command":
            cmd_name = trigger.get("command_name", "")
            for i in range(self.combo_command.count()):
                if self.combo_command.itemText(i) == cmd_name:
                    self.combo_command.setCurrentIndex(i)
                    break

    def get_result(self):
        action_idx = self.action_stack.currentIndex()
        action = _ACTION_KEYS[action_idx]

        result = {
            "name":         self.input_name.text().strip() or "Sem nome",
            "match_format": self.pill_format.current(),
            "match_type":   _MATCH_KEYS[self.combo_match.currentIndex()],
            "pattern":      self.input_pattern.text(),
            "action":       action,
            "enabled":      True,
        }

        if action == "highlight":
            result["highlight_color"] = self._selected_color
        elif action == "send_command":
            result["command_name"] = self.combo_command.currentText()

        return result
