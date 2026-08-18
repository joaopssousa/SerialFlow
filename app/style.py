"""Tema dark completo do SerialForge"""

def rgba(hex_color, alpha):
    """Cor translúcida para QSS. Não usar hex de 8 dígitos: o Qt lê #AARRGGBB."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alpha})"


COLORS = {
    "bg_deep":      "#0a0c10",
    "bg_panel":     "#10141c",
    "bg_surface":   "#161b26",
    "bg_raised":    "#1d2436",
    "bg_hover":     "#242d42",
    "accent":       "#00d4ff",
    "accent_dim":   rgba("#00d4ff", 0.13),
    "green":        "#00ff88",
    "green_dim":    rgba("#00ff88", 0.13),
    "red":          "#ff4566",
    "red_dim":      rgba("#ff4566", 0.13),
    "amber":        "#ffaa00",
    "text_primary": "#e8edf5",
    "text_secondary":"#96adc7",
    "text_muted":   "#5a7899",
    "border":       "#253650",
    "border_bright":"#33506e",
}

C = COLORS

# Escala tipográfica única (px). Ajustar aqui recalibra a UI inteira.
FONTS = {
    "label": 10,   # micro-labels uppercase (seções, parâmetros)
    "small": 12,   # texto secundário: hints, toggles, chips, statusbar
    "base":  13,   # texto padrão: botões, campos, nomes
    "title": 14,   # títulos de painel
    "stat":  20,   # valores das estatísticas
    "log":   14,   # log de comunicação
}

F = FONTS

# Fonte monoespaçada usada só onde há dados (log, previews de frame)
MONO = "'JetBrains Mono', 'DejaVu Sans Mono', 'Courier New', monospace"

def get_stylesheet():
    return f"""
    * {{
        border: none;
        outline: none;
    }}
    
    /* Sem background aqui: um fundo global opaco faria cada widget filho
       pintar por cima do painel pai, cobrindo bordas e fundos dos containers */
    QWidget {{
        color: {C['text_primary']};
        font-size: {F['base']}px;
    }}

    QMainWindow, QDialog {{
        background-color: {C['bg_deep']};
    }}

    QToolTip {{
        background-color: {C['bg_raised']};
        color: {C['text_primary']};
        border: 1px solid {C['border_bright']};
        padding: 4px 8px;
    }}
    
    QPushButton {{
        background-color: transparent;
        border: 1px solid {C['border_bright']};
        border-radius: 6px;
        padding: 6px 14px;
        color: {C['text_secondary']};
    }}
    QPushButton:hover {{
        background-color: {C['bg_raised']};
        color: {C['text_primary']};
    }}
    QPushButton:pressed {{
        background-color: {C['bg_hover']};
    }}
    QPushButton:checked {{
        background-color: {C['bg_surface']};
        color: {C['text_primary']};
        border: 1px solid {C['accent']};
    }}
    QPushButton:checked:hover {{
        background-color: {C['bg_raised']};
        border: 1px solid {C['accent']};
    }}

    QPushButton#btn_connect {{
        background-color: {C['green_dim']};
        color: {C['green']};
        border-color: {rgba('#00ff88', 0.2)};
    }}
    QPushButton#btn_connect:hover {{
        background-color: {rgba('#00ff88', 0.2)};
    }}

    QPushButton#btn_disconnect {{
        background-color: {C['red_dim']};
        color: {C['red']};
        border-color: {rgba('#ff4566', 0.2)};
    }}
    QPushButton#btn_disconnect:hover {{
        background-color: {rgba('#ff4566', 0.2)};
    }}

    QPushButton:disabled,
    QPushButton#btn_connect:disabled,
    QPushButton#btn_disconnect:disabled {{
        color: {C['text_muted']};
        background-color: transparent;
        border-color: {C['border']};
    }}

    QSizeGrip {{
        background: transparent;
    }}
    
    QComboBox {{
        background-color: {C['bg_surface']};
        border: 1px solid {C['border_bright']};
        border-radius: 6px;
        padding: 6px 28px 6px 10px;
        color: {C['text_primary']};
        min-height: 20px;
    }}
    QComboBox:hover {{
        border-color: {C['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 22px;
    }}
    QComboBox::down-arrow {{
        image: none;
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {C['text_muted']};
    }}
    QComboBox QAbstractItemView {{
        background-color: {C['bg_raised']};
        border: 1px solid {C['border_bright']};
        border-radius: 6px;
        selection-background-color: {C['accent_dim']};
        selection-color: {C['accent']};
        padding: 4px;
    }}
    QComboBox QAbstractItemView::item {{
        padding: 6px 10px;
        border-radius: 4px;
        min-height: 22px;
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: {C['bg_hover']};
    }}
    
    QLineEdit {{
        background-color: {C['bg_surface']};
        border: 1px solid {C['border_bright']};
        border-radius: 6px;
        padding: 8px 12px;
        color: {C['text_primary']};
    }}
    QLineEdit:hover {{
        border-color: {C['border_bright']};
    }}
    QLineEdit:focus {{
        border-color: {C['accent']};
        background-color: {C['bg_raised']};
    }}
    
    QPlainTextEdit {{
        background-color: transparent;
        border: none;
        color: {C['text_primary']};
        font-family: {MONO};
        font-size: {F['log']}px;
        selection-background-color: {C['accent_dim']};
    }}
    
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
    }}
    QScrollBar::handle:vertical {{
        background: {C['border_bright']};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {C['text_muted']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    
    QStatusBar {{
        background-color: {C['bg_panel']};
        color: {C['text_muted']};
        border-top: 1px solid {C['border']};
        font-size: {F['small']}px;
    }}
    QStatusBar::item {{
        border: none;
    }}
    """
