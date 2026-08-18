"""Painel de comandos com suporte a arquivos .sfcmd"""
import json
import os
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from app.style import COLORS as C, FONTS as F
from app.widgets.command_entry import CommandEntry
from app.widgets.command_dialog import CommandDialog


class CommandsView(QWidget):
    send_frame = Signal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._commands = []
        self._entries = []
        self._current_file = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        # File controls
        file_row = QHBoxLayout()

        self.btn_open = QPushButton("⬆ Abrir")
        self.btn_open.setFixedHeight(28)
        self.btn_open.clicked.connect(self._open_file)

        self.btn_save = QPushButton("⬇ Salvar")
        self.btn_save.setFixedHeight(28)
        self.btn_save.clicked.connect(self._save_file)

        self.lbl_file = QLabel("sem arquivo")
        self.lbl_file.setStyleSheet(f"color: {C['text_muted']}; font-size: {F['small']}px; background: transparent;")

        file_row.addWidget(self.btn_open)
        file_row.addWidget(self.btn_save)
        file_row.addStretch()
        file_row.addWidget(self.lbl_file)
        layout.addLayout(file_row)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._list_container = QWidget()
        self._list_container.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        layout.addWidget(scroll, stretch=1)

        # Add button
        btn_add = QPushButton("+ Adicionar comando")
        btn_add.setFixedHeight(34)
        btn_add.clicked.connect(self._add_command)
        layout.addWidget(btn_add)

    # ── Command management ────────────────────────────────────────────────────

    def _add_command(self):
        dialog = CommandDialog(parent=self)
        if dialog.exec():
            cmd = dialog.get_result()
            self._commands.append(cmd)
            self._insert_entry(cmd)

    def _insert_entry(self, command, idx=None):
        entry = CommandEntry(command, parent=self._list_container)
        entry.send_requested.connect(self._on_send)
        entry.edit_requested.connect(lambda e=entry: self._edit_entry(e))
        entry.delete_requested.connect(lambda e=entry: self._delete_entry(e))

        if idx is None:
            pos = self._list_layout.count() - 1  # before stretch
            self._list_layout.insertWidget(pos, entry)
            self._entries.append(entry)
        else:
            self._list_layout.insertWidget(idx, entry)
            self._entries.insert(idx, entry)

    def _edit_entry(self, entry):
        idx = self._entries.index(entry)
        dialog = CommandDialog(command=self._commands[idx], parent=self)
        if not dialog.exec():
            return

        entry.cleanup()
        new_cmd = dialog.get_result()
        self._commands[idx] = new_cmd

        self._list_layout.removeWidget(entry)
        entry.deleteLater()
        self._entries.pop(idx)

        self._insert_entry(new_cmd, idx=idx)

    def _delete_entry(self, entry):
        idx = self._entries.index(entry)
        entry.cleanup()
        self._list_layout.removeWidget(entry)
        entry.deleteLater()
        self._entries.pop(idx)
        self._commands.pop(idx)

    # ── Send ─────────────────────────────────────────────────────────────────

    def _on_send(self, command):
        payload = command.get("payload", "")
        fmt = command.get("format", "ASCII")
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
            self.send_frame.emit(data)
        except Exception:
            pass

    # ── File I/O ──────────────────────────────────────────────────────────────

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir comandos", "",
            "SerialFlow Commands (*.sfcmd);;JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir o arquivo:\n{e}")
            return

        self._clear_all()
        for cmd in data.get("commands", []):
            self._commands.append(cmd)
            self._insert_entry(cmd)

        self._current_file = path
        self.lbl_file.setText(os.path.basename(path))

    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar comandos",
            self._current_file or "comandos.sfcmd",
            "SerialFlow Commands (*.sfcmd);;JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"commands": self._commands}, f, indent=2, ensure_ascii=False)
            self._current_file = path
            self.lbl_file.setText(os.path.basename(path))
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível salvar:\n{e}")

    def _clear_all(self):
        for entry in self._entries:
            entry.cleanup()
            entry.deleteLater()
        self._entries.clear()
        self._commands.clear()
