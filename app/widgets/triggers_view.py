"""Painel de triggers com suporte a arquivos .sftrig"""
import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFileDialog, QMessageBox
)
from app.style import COLORS as C
from app.widgets.trigger_entry import TriggerEntry
from app.widgets.trigger_dialog import TriggerDialog


class TriggersView(QWidget):
    def __init__(self, get_commands=None, parent=None):
        super().__init__(parent)
        self._get_commands = get_commands or (lambda: [])
        self._triggers = []
        self._entries = []
        self._current_file = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        file_row = QHBoxLayout()

        self.btn_open = QPushButton("⬆ Abrir")
        self.btn_open.setFixedHeight(28)
        self.btn_open.clicked.connect(self._open_file)

        self.btn_save = QPushButton("⬇ Salvar")
        self.btn_save.setFixedHeight(28)
        self.btn_save.clicked.connect(self._save_file)

        self.lbl_file = QLabel("sem arquivo")
        self.lbl_file.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 10px; background: transparent;"
        )

        file_row.addWidget(self.btn_open)
        file_row.addWidget(self.btn_save)
        file_row.addStretch()
        file_row.addWidget(self.lbl_file)
        layout.addLayout(file_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._list_container = QWidget()
        self._list_container.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        layout.addWidget(scroll, stretch=1)

        btn_add = QPushButton("+ Adicionar trigger")
        btn_add.setFixedHeight(34)
        btn_add.clicked.connect(self._add_trigger)
        layout.addWidget(btn_add)

    # ── Trigger management ────────────────────────────────────────────────────

    def _add_trigger(self):
        dialog = TriggerDialog(commands=self._get_commands(), parent=self)
        if dialog.exec():
            trig = dialog.get_result()
            self._triggers.append(trig)
            self._insert_entry(trig)

    def _insert_entry(self, trigger, idx=None):
        entry = TriggerEntry(trigger, parent=self._list_container)
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
        dialog = TriggerDialog(
            trigger=self._triggers[idx],
            commands=self._get_commands(),
            parent=self,
        )
        if not dialog.exec():
            return

        new_trig = dialog.get_result()
        self._triggers[idx] = new_trig

        self._list_layout.removeWidget(entry)
        entry.deleteLater()
        self._entries.pop(idx)

        self._insert_entry(new_trig, idx=idx)

    def _delete_entry(self, entry):
        idx = self._entries.index(entry)
        self._list_layout.removeWidget(entry)
        entry.deleteLater()
        self._entries.pop(idx)
        self._triggers.pop(idx)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_triggers(self):
        return list(self._triggers)

    # ── File I/O ──────────────────────────────────────────────────────────────

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir triggers", "",
            "SerialFlow Triggers (*.sftrig);;JSON (*.json)"
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
        for trig in data.get("triggers", []):
            self._triggers.append(trig)
            self._insert_entry(trig)

        self._current_file = path
        self.lbl_file.setText(os.path.basename(path))

    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar triggers",
            self._current_file or "triggers.sftrig",
            "SerialFlow Triggers (*.sftrig);;JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"triggers": self._triggers}, f, indent=2, ensure_ascii=False)
            self._current_file = path
            self.lbl_file.setText(os.path.basename(path))
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível salvar:\n{e}")

    def _clear_all(self):
        for entry in self._entries:
            entry.deleteLater()
        self._entries.clear()
        self._triggers.clear()
