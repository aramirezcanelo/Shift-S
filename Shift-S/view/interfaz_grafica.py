from PyQt6.QtCore import Qt, QPropertyAnimation
from PyQt6.QtGui import QColor, QCursor
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLineEdit, QPushButton, QLabel, QGraphicsDropShadowEffect, 
                             QGraphicsOpacityEffect, QListWidget, QMessageBox)
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

class InterfazCalculadora(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Calculadora de Transformadas Directas de Laplace")
        self.resize(650, 820)
        self.setMinimumSize(580, 700)
        
        # --- HOJA DE ESTILOS PREMIUM (QSS) ENFOCADA EN USABILIDAD ---
        self.setStyleSheet("""
            QWidget { 
                background-color: #f8fafc; 
                font-family: 'Segoe UI', -apple-system, Arial, sans-serif; 
            }
            
            /* Caja de entrada principal */
            QLineEdit { 
                border: 2px solid #cbd5e1; 
                border-radius: 10px; 
                padding: 12px 14px; 
                font-size: 16px; 
                color: #0f172a; 
                background-color: #ffffff; 
            }
            QLineEdit:focus { 
                border: 2px solid #10b981; 
                background-color: #ffffff; 
            }
            
            /* --- BOTONES DEL TECLADO AUXILIAR POR CATEGORÍAS --- */
            QPushButton { 
                border: 1px solid #e2e8f0; 
                border-radius: 8px; 
                padding: 11px; 
                font-size: 13px; 
                font-weight: 600; 
            }
            
            /* Categoría 1: Estructura EDO y Condiciones (Ámbar / Naranja) */
            QPushButton[category="edo"] {
                background-color: #fff7ed;
                color: #c2410c;
                border-color: #fed7aa;
            }
            QPushButton[category="edo"]:hover {
                background-color: #ffedd5;
                border-color: #fdba74;
            }
            
            /* Categoría 2: Variables y Constantes (Verde tenue) */
            QPushButton[category="var"] {
                background-color: #f0fdf4;
                color: #166534;
                border-color: #bbf7d0;
            }
            QPushButton[category="var"]:hover {
                background-color: #dcfce7;
                border-color: #86efac;
            }
            
            /* Categoría 3: Funciones Matemáticas (Azul tenue) */
            QPushButton[category="func"] {
                background-color: #eff6ff;
                color: #1e40af;
                border-color: #bfdbfe;
            }
            QPushButton[category="func"]:hover {
                background-color: #dbeafe;
                border-color: #93c5fd;
            }
            
            /* Categoría 4: Operadores y Agrupadores (Gris Pizarra) */
            QPushButton[category="op"] {
                background-color: #f1f5f9;
                color: #475569;
                border-color: #e2e8f0;
            }
            QPushButton[category="op"]:hover {
                background-color: #e2e8f0;
                border-color: #cbd5e1;
            }
            
            /* Botón de Información de Formato */
            QPushButton#btn_info { 
                background-color: #1e293b; 
                color: #ffffff; 
                border-radius: 10px; 
                font-size: 15px; 
                font-weight: bold; 
                min-width: 48px; 
                max-width: 48px; 
                border: none; 
            }
            QPushButton#btn_info:hover { 
                background-color: #0f172a; 
            }
            
            /* Botón Principal: Calcular */
            QPushButton#btn_ir { 
                background-color: #10b981; 
                color: #ffffff; 
                border-radius: 10px; 
                font-size: 15px; 
                font-weight: bold;
                padding: 12px; 
                border: none; 
            }
            QPushButton#btn_ir:hover { background-color: #059669; }
            QPushButton#btn_ir:pressed { background-color: #047857; }
            
            /* Botón Secundario: Eliminar */
            QPushButton#btn_limpiar { 
                background-color: #ef4444; 
                color: #ffffff; 
                border-radius: 10px; 
                font-size: 15px; 
                font-weight: bold;
                padding: 12px; 
                border: none; 
            }
            QPushButton#btn_limpiar:hover { background-color: #dc2626; }
            QPushButton#btn_limpiar:pressed { background-color: #b91c1c; }

            /* Historial de consultas */
            QListWidget { 
                border: 1px solid #e2e8f0; 
                border-radius: 10px; 
                background-color: #ffffff; 
                color: #334155; 
                padding: 8px; 
                font-size: 13px;
            }
            QListWidget::item { 
                padding: 8px 10px; 
                border-bottom: 1px solid #f1f5f9; 
            }
            QListWidget::item:hover { 
                background-color: #f8fafc; 
                color: #0f172a;
                border-radius: 6px;
            }
        """)

        # Layout Principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(32, 28, 32, 28)

        # --- SECCIÓN 1: INPUT COMPUESTO ---
        input_line_layout = QHBoxLayout()
        input_line_layout.setSpacing(8)
        
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Ej. y'' + 3*y' + 2*y = 0; y(0)=1; y'(0)=5")
        input_line_layout.addWidget(self.entry)

        self.btn_info = QPushButton("!?")
        self.btn_info.setObjectName("btn_info")
        self.btn_info.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_info.clicked.connect(self.mostrar_ejemplos)
        input_line_layout.addWidget(self.btn_info)
        main_layout.addLayout(input_line_layout)

        # --- SECCIÓN 2: TECLADO MATEMÁTICO EN REJILLA SIMÉTRICA (4x6) ---
        pad_grid = QGridLayout()
        pad_grid.setSpacing(8)
        
        # Estructura de matriz: (Texto Visual, Token de Inserción, Categoría Estilo, Fila, Columna)
        botones = [
            # Fila 0: Bloque de Control Estructural de EDOs
            ('y', 'y', 'edo', 0, 0),
            ("y'", "y'", 'edo', 0, 1),
            ("y''", "y''", 'edo', 0, 2),
            ('=', '=', 'edo', 0, 3),
            (';', '; ', 'edo', 0, 4),
            ('y(0)=', 'y(0)=', 'edo', 0, 5),
            
            # Fila 1: Variables, Constantes y Potencias comunes
            ('t', 't', 'var', 1, 0),
            ('s', 's', 'var', 1, 1),
            ('\u03c0', 'pi', 'var', 1, 2),
            ('alpha', 'a', 'var', 1, 3),
            ('s²', 's**2', 'op', 1, 4),
            ('tⁿ', 't**n', 'op', 1, 5),
            
            # Fila 2: Funciones Estándar y Agrupadores
            ('sin', 'sin(', 'func', 2, 0),
            ('cos', 'cos(', 'func', 2, 1),
            ('eⁿ', 'exp(', 'func', 2, 2),
            ('(', '(', 'op', 2, 3),
            (')', ')', 'op', 2, 4),
            ('/', '/', 'op', 2, 5),
            
            # Fila 3: Extensiones Avanzadas y Operadores Aritméticos
            ('sinh', 'sinh(', 'func', 3, 0),
            ('cosh', 'cosh(', 'func', 3, 1),
            ("y'(0)=", "y'(0)=", 'edo', 3, 2),
            ('+', '+', 'op', 3, 3),
            ('-', '-', 'op', 3, 4),
            ('*', '*', 'op', 3, 5)
        ]
        
        for txt, val, cat, fila, col in botones:
            btn = QPushButton(txt)
            btn.setProperty("category", cat)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, v=val: self.insertar(v))
            pad_grid.addWidget(btn, fila, col)
            
        main_layout.addLayout(pad_grid)

        # --- SECCIÓN 3: BOTONES DE ACCIÓN INFERIORES ---
        layout_botones_accion = QHBoxLayout()
        layout_botones_accion.setSpacing(10)
        
        self.btn_ir = QPushButton("Calcular")
        self.btn_ir.setObjectName("btn_ir")
        self.btn_ir.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_limpiar = QPushButton("Eliminar")
        self.btn_limpiar.setObjectName("btn_limpiar")
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Sombras suavizadas de diseño moderno (Canal Alfa RGBA)
        color_sombra = QColor(15, 23, 42, 35) 
        
        shadow_ir = QGraphicsDropShadowEffect()
        shadow_ir.setBlurRadius(12)
        shadow_ir.setColor(color_sombra)
        shadow_ir.setOffset(0, 3)
        self.btn_ir.setGraphicsEffect(shadow_ir)

        shadow_limpiar = QGraphicsDropShadowEffect()
        shadow_limpiar.setBlurRadius(12)
        shadow_limpiar.setColor(color_sombra)
        shadow_limpiar.setOffset(0, 3)
        self.btn_limpiar.setGraphicsEffect(shadow_limpiar)

        layout_botones_accion.addWidget(self.btn_ir, stretch=3)
        layout_botones_accion.addWidget(self.btn_limpiar, stretch=1)
        main_layout.addLayout(layout_botones_accion)

        # --- SECCIÓN 4: VISUALIZADOR DE RESULTADOS ---
        self.lbl_res = QLabel("Procedimiento y Solución:")
        self.lbl_res.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b; margin-top: 6px;")
        main_layout.addWidget(self.lbl_res)

        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 10px; background-color: #ffffff;")
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        
        self.fade_effect = QGraphicsOpacityEffect()
        self.web_view.setGraphicsEffect(self.fade_effect)
        main_layout.addWidget(self.web_view, stretch=5) 

        # --- SECCIÓN 5: HISTORIAL DE CONSULTAS ---
        self.lbl_historial = QLabel("Historial de Consultas:")
        self.lbl_historial.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b; margin-top: 4px;")
        main_layout.addWidget(self.lbl_historial)
        
        self.historial_list = QListWidget()
        main_layout.addWidget(self.historial_list, stretch=2)

        self.setLayout(main_layout)

    def insertar(self, val):
        self.entry.insert(val)
        self.entry.setFocus()

    def mostrar_ejemplos(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Formatos y Ejemplos de EDO")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("<b>Formatos estructurales para sistemas dinámicos (EDO):</b>")
        msg.setInformativeText(
            "<b>Estructura base:</b> EDO principal separada por punto y coma (;) de sus condiciones iniciales.\n\n"
            "<b>Ejemplo Lineal Distinto (2do Orden):</b>\n"
            "y'' + 3*y' + 2*y = 0; y(0)=1; y'(0)=5\n\n"
            "<b>Ejemplo Sistema Amortiguado (Repetido):</b>\n"
            "y'' + 6*y' + 9*y = 0; y(0)=1; y'(0)=2\n\n"
            "<b>Ejemplo Caso Cuadrático (Oscilatorio):</b>\n"
            "y'' + 4*y = cos(t); y(0)=0; y'(0)=0\n\n"
            "<b>Ejemplo de Alto Orden (Hasta 10):</b>\n"
            "y'''''' - y = 0; y(0)=1"
        )
        msg.setStyleSheet("""
            QLabel { font-size: 13px; color: #334155; min-width: 420px; max-width: 420px; }
            QPushButton { background-color: #0f172a; color: white; padding: 6px 18px; font-weight: bold; border-radius: 6px; }
            QPushButton:hover { background-color: #1e293b; }
        """)
        msg.exec()

    def animar_calculo(self):
        self.anim_fade = QPropertyAnimation(self.fade_effect, b"opacity")
        self.anim_fade.setDuration(280)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        self.anim_fade.start()

    def mostrar_html(self, html_str):
        self.web_view.setHtml(html_str)
        
    def obtener_texto(self):
        return self.entry.text().strip()