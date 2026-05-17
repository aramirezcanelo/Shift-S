import sys
import sympy as sp  # Biblioteca para cálculo simbólico (álgebra, integrales, Laplace)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QRect
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QListWidget, QMessageBox)
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView  # Componente para renderizar HTML y MathJax (fórmulas bonitas)

class SymbolabPremium(QWidget):
    def __init__(self):
        super().__init__()
        # Definimos las variables matemáticas que usará SymPy. 'positive=True' ayuda a simplificar directo
        self.t = sp.symbols('t', positive=True)
        self.s = sp.symbols('s', positive=True)
        # Constantes típicas de los problemas de examen
        self.a, self.b, self.k, self.n = sp.symbols('a b k n', real=True)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Calculadora de Transformadas Directas de Laplace")
        self.resize(600, 750)
        self.setMinimumSize(500, 600)
        
        # CSS puro para el diseño. Estilo limpio con paleta gris slate (#0f172a) y verde esmeralda (#10b981)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                color: #0f172a;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #10b981;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                color: #334155;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
            QPushButton#btn_ir {
                background-color: #10b981;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 12px;
                border: none;
            }
            QPushButton#btn_ir:hover {
                background-color: #059669;
            }
            QPushButton#btn_info {
                background-color: #0f172a;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 45px;
                max-width: 45px;
                border: none;
            }
            QPushButton#btn_info:hover {
                background-color: #1e293b;
            }
            QListWidget {
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                background-color: #ffffff;
                color: #0f172a;
                padding: 5px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f1f5f9;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
            }
        """)

        # Layout principal vertical (todo se apila hacia abajo)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(30, 25, 30, 25)

        # Layout horizontal para meter el campo de texto y el botón "!?" pegados en la misma línea
        input_line_layout = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Ej. t**2 * exp(-3*t) o sin(2*t)")
        self.entry.returnPressed.connect(self.calcular)  # Si das Enter en el teclado, calcula directo
        input_line_layout.addWidget(self.entry)

        self.btn_info = QPushButton("!?")
        self.btn_info.setObjectName("btn_info")  # ID para asignarle su estilo CSS específico
        self.btn_info.setCursor(Qt.CursorShape.PointingHandCursor)  # Cursor de manita al pasar encima
        self.btn_info.clicked.connect(self.mostrar_ejemplos)
        input_line_layout.addWidget(self.btn_info)
        main_layout.addLayout(input_line_layout)  # Metemos la línea al contenedor principal

        # Teclado en pantalla: Fila 1
        pad_layout_1 = QHBoxLayout()
        botones_1 = [
            ('t\u207f', 't**n'), ('s', 's'), ('e\u02e3', 'exp('), 
            ('sin', 'sin('), ('cos', 'cos('), ('/', '/')
        ]
        for txt, val in botones_1:
            btn = QPushButton(txt)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # El truco del lambda guarda el valor string específico de cada botón para meterlo al input
            btn.clicked.connect(lambda checked, v=val: self.insertar(v))
            pad_layout_1.addWidget(btn)
        main_layout.addLayout(pad_layout_1)

        # Teclado en pantalla: Fila 2
        pad_layout_2 = QHBoxLayout()
        botones_2 = [
            ('sinh', 'sinh('), ('cosh', 'cosh('), ('\u03c0', 'pi'),
            (sp.Symbol('alpha').name, 'a'), ('+', '+'), ('-', '-'), ('*', '*'), ('(', '('), (')', ')')
        ]
        for txt, val in botones_2:
            btn = QPushButton(txt)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=val: self.insertar(v))
            pad_layout_2.addWidget(btn)
        main_layout.addLayout(pad_layout_2)

        # Botón principal de ejecución
        self.btn_ir = QPushButton("Calcular")
        self.btn_ir.setObjectName("btn_ir")
        self.btn_ir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ir.clicked.connect(self.calcular)
        
        # Efecto visual de sombra para darle profundidad al botón de calcular
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(0, 2)
        self.btn_ir.setGraphicsEffect(shadow)
        main_layout.addWidget(self.btn_ir)

        # Etiquetas de texto fijas (UI)
        self.lbl_res = QLabel("Procedimiento y Solución:")
        self.lbl_res.setStyleSheet("font-size: 14px; font-weight: bold; color: #334155; margin-top: 5px;")
        main_layout.addWidget(self.lbl_res)

        # El motor web embebido para poder mostrar LaTeX e imágenes dinámicas sin romper el diseño
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("border: 2px solid #e2e8f0; border-radius: 8px; background-color: #ffffff;")
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        
        # Efecto de opacidad para la animación de desvanecimiento (Fade In) al calcular
        self.fade_effect = QGraphicsOpacityEffect()
        self.web_view.setGraphicsEffect(self.fade_effect)
        main_layout.addWidget(self.web_view, stretch=1)  # stretch=1 para que ocupe todo el espacio vertical disponible

        self.lbl_historial = QLabel("Historial de Consultas:")
        self.lbl_historial.setStyleSheet("font-size: 14px; font-weight: bold; color: #334155; margin-top: 5px;")
        main_layout.addWidget(self.lbl_historial)
        
        # Lista interactiva para guardar lo que vamos calculando
        self.historial_list = QListWidget()
        self.historial_list.itemClicked.connect(self.cargar_historial)
        main_layout.addWidget(self.historial_list)

        self.setLayout(main_layout)
        self.render_html("<h3>F(s) = </h3>")  # Estado inicial del visor web

    def insertar(self, val):
        # Inserta el texto del botón en la posición actual del cursor y no pierde el foco del teclado
        self.entry.insert(val)
        self.entry.setFocus()

    def cargar_historial(self, item):
        # Recupera el texto del elemento clickeado en el historial y dispara el cálculo automático
        self.entry.setText(item.text())
        self.calcular()

    def mostrar_ejemplos(self):
        # Ventana emergente nativa con los ejemplos estructurados exactamente línea por línea
        msg = QMessageBox(self)
        msg.setWindowTitle("Formatos y Ejemplos de Transformadas")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("<b>Formatos estructurales requeridos para transformadas directas:</b>")
        
        msg.setInformativeText(
            "<b>Constante:</b> 5 o k\n"
            "<b>Potencia:</b> t**3 o t**n\n"
            "<b>Exponencial:</b> exp(2*t) o exp(-a*t)\n"
            "<b>Seno / Coseno:</b> sin(3*t) o cos(k*t)\n"
            "<b>Hiperbólicas:</b> sinh(2*t) o cosh(a*t)\n"
            "<b>Primer Teorema de Traslación:</b> t**2 * exp(-3*t)\n"
            "<b>Linealidad (Combinadas):</b> t**2 + sin(2*t) - 5*exp(t)"
        )
        
        msg.setStyleSheet("""
            QLabel { font-size: 13px; color: #0f172a; min-width: 380px; max-width: 380px; }
            QPushButton { background-color: #0f172a; color: white; padding: 6px 16px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #1e293b; }
        """)
        msg.exec()

    def calcular(self):
        # --- ANIMACIÓN DE CLICK EN EL BOTÓN (REBOTE) ---
        geom = self.btn_ir.geometry()
        anim_presion = QPropertyAnimation(self.btn_ir, b"geometry")
        anim_presion.setDuration(50)
        anim_presion.setStartValue(geom)
        anim_presion.setEndValue(QRect(geom.x() + 4, geom.y() + 2, geom.width() - 8, geom.height() - 4))
        
        anim_rebote = QPropertyAnimation(self.btn_ir, b"geometry")
        anim_rebote.setDuration(150)
        anim_rebote.setStartValue(QRect(geom.x() + 4, geom.y() + 2, geom.width() - 8, geom.height() - 4))
        anim_rebote.setEndValue(geom)
        anim_rebote.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        self.grupo_boton = QSequentialAnimationGroup()
        self.grupo_boton.addAnimation(anim_presion)
        self.grupo_boton.addAnimation(anim_rebote)
        self.grupo_boton.start()
        
        # --- ANIMACIÓN FADE IN PARA EL VISOR WEB ---
        self.anim_fade = QPropertyAnimation(self.fade_effect, b"opacity")
        self.anim_fade.setDuration(250)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        self.anim_fade.start()

        # --- NÚCLEO DE PROCESAMIENTO MATEMÁTICO ---
        entrada_original = self.entry.text().strip()
        if not entrada_original:
            return
            
        # Reemplazo preventivo por si meten notación estándar de potencia '^' en vez de la de Python '**'
        expr_str = entrada_original.replace('^', '**')
        
        # Mapeo explícito de strings a objetos matemáticos de SymPy para evitar que rompa por variables desconocidas
        ctx = {'t': self.t, 's': self.s, 'a': self.a, 'b': self.b, 'n': self.n, 'k': self.k, 'pi': sp.pi,
               'exp': sp.exp, 'sin': sp.sin, 'cos': sp.cos, 'sinh': sp.sinh, 'cosh': sp.cosh}
        
        try:
            # Convierte la cadena de texto limpia en una expresión matemática real ejecutable
            f_input = sp.sympify(expr_str, locals=ctx)
        except Exception:
            self.mostrar_guia_errores()
            return

        try:
            pasos = []
            # Validación estricta: Si contiene la variable 's', asumimos que es una transformada inversa
            es_inversa = 's' in expr_str or any(sym.name == 's' for sym in f_input.free_symbols)

            if es_inversa:
                self.lbl_res.setText("Estado: Operación No Soportada")
                html_inversa = f"""
                <div style='color: #b91c1c; font-weight: bold; font-size: 16px; margin-bottom: 10px;'>
                    La expresión ingresada no corresponde a una Transformada Directa.
                </div>
                <p><b>Tipo de ecuación de frecuencias detectada:</b> Transformada Inversa de Laplace $\\mathcal{{L}}^{{-1}}\\{{{sp.latex(f_input)}\\}}$</p>
                <p style='color: #475569;'>Este resolvedor está configurado únicamente para calcular transformadas directas en el dominio del tiempo $t$.</p>
                """
                self.render_html(html_inversa)
                return
            
            else:
                self.lbl_res.setText("Procedimiento y Solución (Transformada Directa):")
                # Estructuración paso a paso tipo examen. Usamos sp.latex() para formatear las salidas matemáticas puras
                pasos.append(f"<b>Problema:</b> Calcular la Transformada Directa $\\mathcal{{L}}\\{{{sp.latex(f_input)}\\}}$")

                # CASO 1: Constantes o números puros
                if f_input.is_Number or f_input in [self.a, self.b, self.k]:
                    pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{c\\} = \\frac{{c}}{{s}}$")
                    f_out = f_input / self.s
                    pasos.append(f"<b>Sustituyendo:</b> $F(s) = \\frac{{{sp.latex(f_input)}}}{{s}}$")

                # CASO 2: Propiedad de linealidad (sumas y restas de términos independientes)
                elif isinstance(f_input, sp.Add):
                    pasos.append("<b>Propiedad de Linealidad aplicada:</b> $\\mathcal{{L}}\\{f(t) \\pm g(t)\\} = \\mathcal{{L}}\\{f(t)\\} \\pm \\mathcal{{L}}\\{g(t)\\}$")
                    terminos_proc = [f"\\mathcal{{L}}\\{{{sp.latex(term)}\\}}" for term in f_input.args]
                    pasos.append(f"<b>Separando t&eacute;rminos:</b> ${' + '.join(terminos_proc)}$")
                    f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                    pasos.append(f"<b>Resultado directo combinado:</b> $F(s) = {sp.latex(sp.simplify(f_out))}$")

                # CASO 3: Primer teorema de traslación (Multiplicaciones por exponenciales e^(at))
                elif isinstance(f_input, sp.Mul) and any(isinstance(arg, sp.Pow) and arg.base == sp.E or arg.func == sp.exp for arg in f_input.args):
                    pasos.append("<b>Primer Teorema de Traslaci&oacute;n aplicado:</b> $\\mathcal{{L}}\\{e^{{at}} f(t)\\} = \\mathcal{{L}}\\{f(t)\\}|_{{s \\to s - a}}$")
                    # Aislamos el término exponencial del resto de la expresión
                    exp_term = [arg for arg in f_input.args if isinstance(arg, sp.Pow) and arg.base == sp.E or arg.func == sp.exp][0]
                    rest_term = sp.Mul(*[arg for arg in f_input.args if arg != exp_term])
                    
                    exponente = exp_term.args[0] if exp_term.func == sp.exp else exp_term.exp
                    shift = sp.Wild('shift')
                    match = exponente.match(shift * self.t)
                    valor_a = match[shift] if match else exponente / self.t
                    
                    # Resolvemos la función base sin la exponencial y luego aplicamos el desfase (s -> s - a)
                    f_s_sin_exp = sp.laplace_transform(rest_term, self.t, self.s, noconds=True)
                    pasos.append(f"1. Transformada base: $\\mathcal{{L}}\\{{{sp.latex(rest_term)}\\}} = {sp.latex(f_s_sin_exp)}$")
                    pasos.append(f"2. Desplazamiento de frecuencias: $s \\to s - ({sp.latex(valor_a)})$")
                    f_out = f_s_sin_exp.subs(self.s, self.s - valor_a)
                    pasos.append(f"<b>Resultado final:</b> $F(s) = {sp.latex(sp.simplify(f_out))}$")

                # CASO 4: Funciones elementales directas (Seno, Coseno, Potencias solitarias)
                else:
                    if isinstance(f_input, sp.Pow) and f_input.base == self.t:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{t^n\\} = \\frac{{n!}}{{s^{{n+1}}}}$")
                    elif f_input.func == sp.sin:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\sin(kt)\\} = \\frac{{k}}{{s^2 + k^2}}$")
                    elif f_input.func == sp.cos:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\cos(kt)\\} = \\frac{{s}}{{s^2 + k^2}}$")
                    elif f_input.func == sp.sinh:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\sinh(kt)\\} = \\frac{{k}}{{s^2 - k^2}}$")
                    elif f_input.func == sp.cosh:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\cosh(kt)\\} = \\frac{{s}}{{s^2 - k^2}}$")
                    
                    f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                    pasos.append(f"<b>Resultado evaluado:</b> $F(s) = {sp.latex(sp.simplify(f_out))}$")

            # Si la consulta es nueva, la agrega al inicio de la lista del historial
            if entrada_original not in [self.historial_list.item(i).text() for i in range(self.historial_list.count())]:
                self.historial_list.insertItem(0, entrada_original)

            # Convierte el array de pasos en bloques HTML y renderiza
            html_procedimiento = "".join([f"<p style='margin: 8px 0;'>{p}</p>" for p in pasos])
            self.render_html(html_procedimiento)

        except Exception:
            # Captura de errores matemáticos si divergen o no tienen solución analítica directa
            self.render_html("<p style='color: #b91c1c; font-weight: bold;'>La expresión ingresada no posee una solución analítica directa.</p>")

    def mostrar_guia_errores(self):
        # Tabla interactiva en HTML para guiar al usuario si escribe mal la sintaxis de Python
        html_error = """
        <div style='text-align: center; color: #b91c1c; font-weight: bold; margin-bottom: 15px;'>
            Error de sintaxis. Gu&iacute;a de escritura correcta:
        </div>
        <table style='width: 100%; border-collapse: collapse; font-size: 14px;'>
            <tr style='background-color: #0f172a; color: white;'>
                <th style='padding: 8px; border: 1px solid #ddd;'>Operaci&oacute;n</th>
                <th style='padding: 8px; border: 1px solid #ddd;'>Incorrecto</th>
                <th style='padding: 8px; border: 1px solid #ddd;'>Correcto (Python)</th>
            </tr>
            <tr>
                <td style='padding: 8px; border: 1px solid #ddd;'>Potencia ($t^2$)</td>
                <td style='padding: 8px; border: 1px solid #ddd; color: #b91c1c;'>t2 o t^2</td>
                <td style='padding: 8px; border: 1px solid #ddd; color: #10b981; font-weight: bold;'>t**2</td>
            </tr>
            <tr style='background-color: #f8fafc;'>
                <td style='padding: 8px; border: 1px solid #ddd;'>Multiplicaci&oacute;n ($2t$)</td>
                <td style='padding: 8px; border: 1px solid #ddd; color: #b91c1c;'>2t</td>
                <td style='padding: 8px; border: 1px solid #ddd; color: #10b981; font-weight: bold;'>2*t</td>
            </tr>
            <tr>
                <td style='padding: 8px; border: 1px solid #ddd;'>Exponencial ($e^{-3t}$)</td>
                <td style='padding: 8px; border: 1px solid #ddd; color: #b91c1c;'>e^(-3t)</td>
                <td style='padding: 8px; border: 1px solid #ddd; color: #10b981; font-weight: bold;'>exp(-3*t)</td>
            </tr>
            <tr style='background-color: #f8fafc;'>
                <td style='padding: 8px; border: 1px solid #ddd;'>Seno ($\\sin(2t)$)</td>
                <td style='padding: 8px; border: 1px solid #ddd; color: #b91c1c;'>sin2t</td>
                <td style='padding: 8px; border: 1px solid #ddd; color: #10b981; font-weight: bold;'>sin(2*t)</td>
            </tr>
        </table>
        """
        self.render_html(html_error)

    def render_html(self, contenido):
        # Inyección de MathJax v2.7.7 mediante CDN externo garantizando renderizado matemático homogéneo y libre de bugs
        html = f"""
        <html>
        <head>
            <script type="text/x-mathjax-config">
                MathJax.Hub.Config({{
                    messageStyle: "none",
                    tex2jax: {{
                        inlineMath: [ ['$','$'], ["\\\\(","\\\\)"] ],
                        displayMath: [ ['$$','$$'], ["\\\\[","\\\\]"] ],
                        processEscapes: true
                    }}
                }});
            </script>
            <script type="text/javascript" async
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
            <style>
                #MathJax_ProcessMessage {{ display: none !important; }}
                body {{
                    margin: 15px;
                    background-color: #ffffff;
                    font-family: 'Segoe UI', sans-serif;
                    color: #0f172a;
                    font-size: 15px;
                    line-height: 1.6;
                }}
                b {{
                    color: #334155;
                }}
            </style>
        </head>
        <body>
            {contenido}
        </body>
        </html>
        """
        self.web_view.setHtml(html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = SymbolabPremium()
    calc.show()
    sys.exit(app.exec())