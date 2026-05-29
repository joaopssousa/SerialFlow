"""Tema dark completo do SerialForge"""

COLORS = {
    "bg_deep":      "#0a0c10",
    "bg_panel":     "#10141c",
    "bg_surface":   "#161b26",
    "bg_raised":    "#1d2436",
    "bg_hover":     "#242d42",
    "accent":       "#00d4ff",
    "accent_dim":   "#00d4ff22",
    "green":        "#00ff88",
    "green_dim":    "#00ff8822",
    "red":          "#ff4566",
    "red_dim":      "#ff456622",
    "amber":        "#ffaa00",
    "text_primary": "#e8edf5",
    "text_secondary":"#96adc7",
    "text_muted":   "#5a7899",
    "border":       "#253650",
    "border_bright":"#33506e",
}

C = COLORS

def get_stylesheet():
    return f"""
    * {{
        border: none;
        outline: none;
    }}
    
    QWidget {{
        background-color: {C['bg_deep']};
        color: {C['text_primary']};
        font-size: 12px;
    }}
    
    QMainWindow {{
        background-color: {C['bg_deep']};
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
        border-color: #00ff8833;
    }}
    QPushButton#btn_connect:hover {{
        background-color: #00ff8833;
    }}
    
    QPushButton#btn_disconnect {{
        background-color: {C['red_dim']};
        color: {C['red']};
        border-color: #ff456633;
    }}
    QPushButton#btn_disconnect:hover {{
        background-color: #ff456633;
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
        font-size: 13px;
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
    }}
    QStatusBar::item {{
        border: none;
    }}
    """
