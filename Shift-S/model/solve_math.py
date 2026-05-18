import sympy as sp
from view.utilidades_html import generar_html, GUIA_ERRORES_HTML

class SolverLaplace:
    def __init__(self):
        self.t = sp.symbols('t', positive=True)
        self.s = sp.symbols('s', positive=True)
        self.a, self.b, self.k, self.n = sp.symbols('a b k n', real=True)
        self.ctx = {
            't': self.t, 's': self.s, 'a': self.a, 'b': self.b, 'n': self.n, 'k': self.k, 'pi': sp.pi,
            'exp': sp.exp, 'sin': sp.sin, 'cos': sp.cos, 'sinh': sp.sinh, 'cosh': sp.cosh
        }

    def procesar_expresion(self, expr_str):
        expr_str = expr_str.replace('^', '**')
        
        if '=' in expr_str:
            return self.resolver_edo(expr_str)
        
        try:
            f_input = sp.sympify(expr_str, locals=self.ctx)

            simbolos_permitidos = {self.t, self.s, self.a, self.b, self.k, self.n}
            if not f_input.free_symbols.issubset(simbolos_permitidos):
                return "error_sintaxis", generar_html(GUIA_ERRORES_HTML)
        except Exception:
            return "error_sintaxis", generar_html(GUIA_ERRORES_HTML)

        es_inversa = self.s in getattr(f_input, 'free_symbols', [])

        if es_inversa:
            html_inversa = f"""
            <div style='color: #b91c1c; font-weight: bold; font-size: 16px; margin-bottom: 10px;'>
                La expresión ingresada no corresponde a una Transformada Directa.
            </div>
            <p><b>Tipo de ecuación de frecuencias detectada:</b> Transformada Inversa de Laplace $\\mathcal{{L}}^{{-1}}\\{{{sp.latex(f_input)}\\}}$</p>
            <p style='color: #475569;'>Este resolvedor está configurado únicamente para calcular transformadas directas en el dominio del tiempo $t$.</p>
            """
            return "inversa", generar_html(html_inversa)

        try:
            pasos = []
            pasos.append(f"<b>Problema:</b> Calcular la Transformada Directa $\\mathcal{{L}}\\{{{sp.latex(f_input)}\\}}$")
            
            # CASO 1: Constantes o Literales
            if f_input.is_Number or f_input in [self.a, self.b, self.k]:
                pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{c\\} = \\frac{{c}}{{s}}$")
                f_out = f_input / self.s
                pasos.append(f"<b>Sustituyendo:</b> $F(s) = \\frac{{{sp.latex(f_input)}}}{{s}}$")

            # CASO 2: Propiedad de linealidad (sumas y restas)
            elif isinstance(f_input, sp.Add):
                pasos.append("<b>Propiedad de Linealidad aplicada:</b> $\\mathcal{{L}}\\{f(t) \\pm g(t)\\} = \\mathcal{{L}}\\{f(t)\\} \\pm \\mathcal{{L}}\\{g(t)\\}$")
                terminos_proc = [f"\\mathcal{{L}}\\{{{sp.latex(term)}\\}}" for term in f_input.args]
                pasos.append(f"<b>Separando t&eacute;rminos:</b> ${' + '.join(terminos_proc)}$")
                
                f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                if f_out.has(sp.LaplaceTransform):
                    raise ValueError("Sin solución analítica")
                
                f_out_simp = sp.simplify(f_out)
                latex_original = sp.latex(f_out)
                latex_simplificado = sp.latex(f_out_simp)
                
                pasos.append(f"<b>Resultado directo combinado:</b> $F(s) = {latex_original}$")
                if latex_original != latex_simplificado:
                    pasos.append(f"<b>Simplificaci&oacute;n algebraica (Denominador com&uacute;n):</b> $F(s) = {latex_simplificado}$")
            
            # CASO 3: Primer Teorema de Traslación
            elif isinstance(f_input, sp.Mul) and any(isinstance(arg, sp.Pow) and arg.base == sp.E or arg.func == sp.exp for arg in f_input.args):
                pasos.append("<b>Primer Teorema de Traslaci&oacute;n aplicado:</b> $\\mathcal{{L}}\\{e^{{at}} f(t)\\} = \\mathcal{{L}}\\{f(t)\\}|_{{s \\to s - a}}$")
                exp_term = [arg for arg in f_input.args if isinstance(arg, sp.Pow) and arg.base == sp.E or arg.func == sp.exp][0]
                rest_term = sp.Mul(*[arg for arg in f_input.args if arg != exp_term])
                
                exponente = exp_term.args[0] if exp_term.func == sp.exp else exp_term.exp
                shift = sp.Wild('shift')
                match = exponente.match(shift * self.t)
                valor_a = match[shift] if match else exponente / self.t
                
                f_s_sin_exp = sp.laplace_transform(rest_term, self.t, self.s, noconds=True)
                pasos.append(f"1. Transformada base: $\\mathcal{{L}}\\{{{sp.latex(rest_term)}\\}} = {sp.latex(f_s_sin_exp)}$")
                pasos.append(f"2. Desplazamiento de frecuencias: $s \\to s - ({sp.latex(valor_a)})$")
                f_out = f_s_sin_exp.subs(self.s, self.s - valor_a)
                pasos.append(f"<b>Resultado final:</b> $F(s) = {sp.latex(sp.simplify(f_out))}$")

            # CASO 4: Funciones elementales directas
            else:
                if isinstance(f_input, sp.Pow) and f_input.base == self.t:
                    pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{t^n\\} = \\frac{{n!}}{{s^{{n+1}}}}$")
                    if f_input.exp == self.n:
                        f_out_latex = "\\frac{n!}{s^{n+1}}"
                    else:
                        f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                        f_out_latex = sp.latex(sp.simplify(f_out))
                    pasos.append(f"<b>Resultado evaluado:</b> $F(s) = {f_out_latex}$")
                else:
                    if f_input.func == sp.sin:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\sin(kt)\\} = \\frac{{k}}{{s^2 + k^2}}$")
                    elif f_input.func == sp.cos:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\cos(kt)\\} = \\frac{{s}}{{s^2 + k^2}}$")
                    elif f_input.func == sp.sinh:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\sinh(kt)\\} = \\frac{{k}}{{s^2 - k^2}}$")
                    elif f_input.func == sp.cosh:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\cosh(kt)\\} = \\frac{{s}}{{s^2 - k^2}}$")
                        
                    f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                    pasos.append(f"<b>Resultado evaluado:</b> $F(s) = {sp.latex(sp.simplify(f_out))}$")

            html_procedimiento = "".join([f"<p style='margin: 8px 0;'>{p}</p>" for p in pasos])
            return "directa", generar_html(html_procedimiento)

        except Exception:
            return "error_matematico", generar_html("<p style='color: #b91c1c; font-weight: bold;'>La expresión ingresada no posee una solución analítica directa.</p>")

    def resolver_edo(self, expr_str):
        try:
            # Estandarizar la entrada
            expr_str = expr_str.replace('y(t)', 'y')
            
            # --- EXTRACCIÓN DINÁMICA DE CONDICIONES INICIALES (HASTA ORDEN 9) ---
            partes = expr_str.split(';')
            edo_principal = partes[0]
            
            y0, y1, y2, y3, y4, y5, y6, y7, y8, y9 = [0]*10
            for condicion in partes[1:]:
                condicion_limpia = condicion.strip().replace(' ', '')
                if "y'''''''''(0)=" in condicion_limpia: y9 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
                elif "y''''''''(0)=" in condicion_limpia: y8 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
                elif "y'''''''(0)=" in condicion_limpia: y7 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
                elif "y''''''(0)=" in condicion_limpia: y6 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
                elif "y'''''(0)=" in condicion_limpia: y5 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
                elif "y''''(0)=" in condicion_limpia: y4 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
                elif "y'''(0)=" in condicion_limpia: y3 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
                elif "y''(0)=" in condicion_limpia: y2 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
                elif "y'(0)=" in condicion_limpia: y1 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
                elif "y(0)=" in condicion_limpia: y0 = sp.sympify(condicion_limpia.split('=')[1], locals=self.ctx)
            
            lhs_txt, rhs_txt = edo_principal.split('=')
            
            # Reemplazo estricto de mayor a menor orden (de 10 a 1)
            lhs_prepared = lhs_txt.replace("y''''''''''", "y_dec_prime") \
                                  .replace("y'''''''''", "y_non_prime") \
                                  .replace("y''''''''", "y_oct_prime") \
                                  .replace("y'''''''", "y_sept_prime") \
                                  .replace("y''''''", "y_sext_prime") \
                                  .replace("y'''''", "y_quint_prime") \
                                  .replace("y''''", "y_quad_prime") \
                                  .replace("y'''", "y_triple_prime") \
                                  .replace("y''", "y_double_prime") \
                                  .replace("y'", "y_prime")
            
            ctx_edo = self.ctx.copy()
            ctx_edo.update({
                'y_dec_prime': sp.symbols('y_dec_prime'),
                'y_non_prime': sp.symbols('y_non_prime'),
                'y_oct_prime': sp.symbols('y_oct_prime'),
                'y_sept_prime': sp.symbols('y_sept_prime'),
                'y_sext_prime': sp.symbols('y_sext_prime'),
                'y_quint_prime': sp.symbols('y_quint_prime'),
                'y_quad_prime': sp.symbols('y_quad_prime'),
                'y_triple_prime': sp.symbols('y_triple_prime'),
                'y_double_prime': sp.symbols('y_double_prime'),
                'y_prime': sp.symbols('y_prime'),
                'y': sp.symbols('y')
            })
            
            lhs_expr = sp.sympify(lhs_prepared, locals=ctx_edo)
            rhs_expr = sp.sympify(rhs_txt, locals=ctx_edo)
            
            Y = sp.symbols('Y')
            s = self.s
            
            # --- SUSTITUCIÓN DE TEOREMAS (HASTA ORDEN 10) ---
            rhs_laplace = sp.laplace_transform(rhs_expr, self.t, s, noconds=True)
            lhs_laplace = lhs_expr.subs({
                ctx_edo['y_dec_prime']: s**10*Y - s**9*y0 - s**8*y1 - s**7*y2 - s**6*y3 - s**5*y4 - s**4*y5 - s**3*y6 - s**2*y7 - s*y8 - y9,
                ctx_edo['y_non_prime']: s**9*Y - s**8*y0 - s**7*y1 - s**6*y2 - s**5*y3 - s**4*y4 - s**3*y5 - s**2*y6 - s*y7 - y8,
                ctx_edo['y_oct_prime']: s**8*Y - s**7*y0 - s**6*y1 - s**5*y2 - s**4*y3 - s**3*y4 - s**2*y5 - s*y6 - y7,
                ctx_edo['y_sept_prime']: s**7*Y - s**6*y0 - s**5*y1 - s**4*y2 - s**3*y3 - s**2*y4 - s*y5 - y6,
                ctx_edo['y_sext_prime']: s**6*Y - s**5*y0 - s**4*y1 - s**3*y2 - s**2*y3 - s*y4 - y5,
                ctx_edo['y_quint_prime']: s**5*Y - s**4*y0 - s**3*y1 - s**2*y2 - s*y3 - y4,
                ctx_edo['y_quad_prime']: s**4*Y - s**3*y0 - s**2*y1 - s*y2 - y3,
                ctx_edo['y_triple_prime']: s**3*Y - s**2*y0 - s*y1 - y2,
                ctx_edo['y_double_prime']: s**2*Y - s*y0 - y1,
                ctx_edo['y_prime']: s*Y - y0,
                ctx_edo['y']: Y
            })
            
            # Despejar algebraicamente Y(s)
            eq_laplace = sp.Eq(lhs_laplace, rhs_laplace)
            Y_sol = sp.solve(eq_laplace, Y)[0]
            Y_fracciones = sp.apart(Y_sol, s)
            
            # Solución temporal
            y_t = sp.inverse_laplace_transform(Y_sol, s, self.t)
            y_t_expandido = sp.expand(y_t)
            
            # --- CONSTRUCCIÓN DEL REPORTE DETALLADO ---
            pasos = []
            pasos.append(f"<div style='color: #10b981; font-weight: bold; font-size: 16px; margin-bottom: 10px;'>Modelado de Ecuaci&oacute;n Diferencial Detectado</div>")
            
            # Convertir visualmente las comillas exageradas a notación formal y^(n)
            lhs_visual = lhs_txt.replace('*', '') \
                                .replace("y''''''''''", "y^{(10)}") \
                                .replace("y'''''''''", "y^{(9)}") \
                                .replace("y''''''''", "y^{(8)}") \
                                .replace("y'''''''", "y^{(7)}") \
                                .replace("y''''''", "y^{(6)}") \
                                .replace("y'''''", "y^{(5)}") \
                                .replace("y''''", "y^{(4)}")
            pasos.append(f"<b>EDO Planteada:</b> ${lhs_visual} = {sp.latex(rhs_expr)}$")
            
            # Formateo visual dinámico de las condiciones iniciales (resumido si son demasiadas)
            ci_texto = f"$y(0) = {sp.latex(y0)}, \\quad y'(0) = {sp.latex(y1)}"
            if "y''''''''''" in lhs_txt or "y'''''''''(0)=" in expr_str: ci_texto += f", \\dots, \\quad y^{(9)}(0) = {sp.latex(y9)}$"
            elif "y'''''''''" in lhs_txt or "y''''''''(0)=" in expr_str: ci_texto += f", \\dots, \\quad y^{(8)}(0) = {sp.latex(y8)}$"
            elif "y''''''''" in lhs_txt or "y'''''''(0)=" in expr_str: ci_texto += f", \\dots, \\quad y^{(7)}(0) = {sp.latex(y7)}$"
            elif "y'''''''" in lhs_txt or "y''''''(0)=" in expr_str: ci_texto += f", \\dots, \\quad y^{(6)}(0) = {sp.latex(y6)}$"
            elif "y''''''" in lhs_txt or "y'''''(0)=" in expr_str: ci_texto += f", \\dots, \\quad y^{(5)}(0) = {sp.latex(y5)}$"
            elif "y'''''" in lhs_txt or "y''''(0)=" in expr_str: ci_texto += f", \\dots, \\quad y^{(4)}(0) = {sp.latex(y4)}$"
            elif "y''''" in lhs_txt or "y'''(0)=" in expr_str: ci_texto += f", \\quad y''(0) = {sp.latex(y2)}, \\quad y'''(0) = {sp.latex(y3)}$"
            elif "y'''" in lhs_txt or "y''(0)=" in expr_str: ci_texto += f", \\quad y''(0) = {sp.latex(y2)}$"
            else: ci_texto += "$"
            
            pasos.append(f"<b>Condiciones Iniciales Aplicadas:</b> {ci_texto}")
            
            pasos.append("<b>1. Aplicando la Transformada de Laplace:</b>")
            pasos.append(f"&bull; $\\mathcal{{L}}\\{{{lhs_visual}\\}} = \\mathcal{{L}}\\{{{sp.latex(rhs_expr)}\\}}$")
            pasos.append("&nbsp;&nbsp;&nbsp;&nbsp;<i>Sustituyendo teoremas de derivaci&oacute;n:</i>")
            pasos.append("&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{y\\} = Y(s)$")
            if "y'" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y'\\}} = sY(s) - {sp.latex(y0)}$")
            if "y''" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y''\\}} = s^2Y(s) - {sp.latex(y0 * s)} - {sp.latex(y1)}$")
            if "y'''" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y'''\\}} = s^3Y(s) - {sp.latex(y0 * s**2)} - {sp.latex(y1 * s)} - {sp.latex(y2)}$")
            if "y''''" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y^{{(4)}}\\}} = s^4Y(s) - \\dots - {sp.latex(y3)}$")
            if "y'''''" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y^{{(5)}}\\}} = s^5Y(s) - \\dots - {sp.latex(y4)}$")
            if "y''''''" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y^{{(6)}}\\}} = s^6Y(s) - \\dots - {sp.latex(y5)}$")
            if "y'''''''" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y^{{(7)}}\\}} = s^7Y(s) - \\dots - {sp.latex(y6)}$")
            if "y''''''''" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y^{{(8)}}\\}} = s^8Y(s) - \\dots - {sp.latex(y7)}$")
            if "y'''''''''" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y^{{(9)}}\\}} = s^9Y(s) - \\dots - {sp.latex(y8)}$")
            if "y''''''''''" in lhs_txt: pasos.append(f"&nbsp;&nbsp;&nbsp;&nbsp;&bull; $\\mathcal{{L}}\\{{y^{{(10)}}\\}} = s^{{10}}Y(s) - \\dots - {sp.latex(y9)}$")

            pasos.append(f"&bull; Expresi&oacute;n algebraica combinada: ${sp.latex(lhs_laplace)} = {sp.latex(rhs_laplace)}$")
            pasos.append(f"<b>2. Despejando simb&oacute;licamente $Y(s)$:</b>")
            pasos.append(f"&bull; $Y(s) = {sp.latex(Y_sol)}$")

            # --- PASO 3: ANALIZADOR DINÁMICO DE LOS 4 CASOS DE FRACCIONES PARCIALES ---
            if Y_fracciones != Y_sol:
                pasos.append("<b>3. Expansi&oacute;n en Fracciones Parciales:</b>")
                try:
                    terminos = Y_fracciones.args if Y_fracciones.is_Add else [Y_fracciones]
                    alfabeto = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
                    idx_letra = 0
                    
                    frac_genericas = []
                    constantes = []
                    
                    for termino in terminos:
                        num, den = termino.as_numer_denom()
                        
                        if den.is_Pow and den.exp.is_Integer: base = den.base
                        else: base = den
                            
                        grado_base = sp.degree(base, s)
                        
                        if grado_base == 1:
                            letra = alfabeto[idx_letra]
                            idx_letra += 1
                            frac_genericas.append(f"\\frac{{{letra}}}{{{sp.latex(den)}}}")
                            constantes.append(f"{letra} = {sp.latex(num)}")
                            
                        elif grado_base == 2:
                            letra1 = alfabeto[idx_letra]
                            letra2 = alfabeto[idx_letra+1]
                            idx_letra += 2
                            frac_genericas.append(f"\\frac{{{letra1} s + {letra2}}}{{{sp.latex(den)}}}")
                            
                            c1 = num.coeff(s)
                            c0 = num.subs(s, 0)
                            constantes.append(f"{letra1} = {sp.latex(c1)}")
                            constantes.append(f"{letra2} = {sp.latex(c0)}")
                        else:
                            frac_genericas.append(sp.latex(termino))
                            
                    if frac_genericas and constantes:
                        pasos.append(f"&bull; Planteamiento general: $Y(s) = {' + '.join(frac_genericas)}$")
                        pasos.append(f"&bull; Constantes extra&iacute;das: ${', \\quad '.join(constantes)}$")
                        
                except Exception:
                    pass 
                
                pasos.append(f"&bull; Sustituyendo en la expresi&oacute;n: $Y(s) = {sp.latex(Y_fracciones)}$")
                pasos.append("<b>4. Aplicando la Transformada Inversa:</b>")
                pasos.append(f"&bull; $y(t) = \\mathcal{{L}}^{{-1}}\\left\\{{ {sp.latex(Y_fracciones)} \\right\\}}$")
            else:
                pasos.append("<b>3. Aplicando la Transformada Inversa:</b>")
                pasos.append(f"&bull; $y(t) = \\mathcal{{L}}^{{-1}}\\left\\{{ {sp.latex(Y_sol)} \\right\\}}$")
                
            pasos.append(f"<b>Soluci&oacute;n particular del sistema:</b> <span style='color: #0f172a; font-weight: bold;'>$y(t) = {sp.latex(y_t_expandido)}$</span>")
            
            html_procedimiento = "".join([f"<p style='margin: 6px 0;'>{p}</p>" for p in pasos])
            return "directa", generar_html(html_procedimiento)
            
        except Exception:
            return "error_matematico", generar_html("<p style='color: #b91c1c; font-weight: bold;'>Error al resolver la EDO. Verifique la sintaxis.</p>")