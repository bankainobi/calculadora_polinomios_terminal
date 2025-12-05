import math
import os

# Habilita los códigos de color ANSI en terminales Windows
os.system("") 

# -------------------------------------------------------------------
# 1. CLASE DE COLORES Y SÍMBOLOS
# -------------------------------------------------------------------

class C:
    """Clase para almacenar los códigos de color ANSI."""
    HEADER = '\033[95m'  # Morado/Magenta
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m' # Amarillo
    FAIL = '\033[91m'    # Rojo
    ENDC = '\033[0m'     # Resetear color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# -------------------------------------------------------------------
# 2. FUNCIÓN DE AYUDA PARA SUPERÍNDICES
# -------------------------------------------------------------------

def to_superscript(n):
    """Convierte un número entero en su representación Unicode de superíndice."""
    n_str = str(n)
    superscript_map = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    return "".join(superscript_map.get(digit, '') for digit in n_str)

# -------------------------------------------------------------------
# 3. DEFINICIÓN DE LA CLASE POLYNOMIAL (MODIFICADA Y CORREGIDA)
# -------------------------------------------------------------------

class Polynomial:
    """
    Clase para representar y operar con polinomios.
    Utiliza colores y superíndices para una mejor visualización.
    """

    def __init__(self, coeffs):
        self.coeffs = [float(c) for c in coeffs]
        self._normalize()

    def _normalize(self):
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()
        if not self.coeffs:
            self.coeffs = [0]

    def degree(self):
        if self.coeffs == [0]:
            return -math.inf
        return len(self.coeffs) - 1

    # =================================================================
    # FUNCIÓN __str__ CORREGIDA
    # =================================================================
    def __str__(self):
        """Representación bonita con colores y superíndices. (CORREGIDA)"""
        if self.coeffs == [0]:
            return f"{C.OKCYAN}0{C.ENDC}"

        terms = []
        for power, coeff in reversed(list(enumerate(self.coeffs))):
            if coeff == 0:
                continue

            # --- Signo ---
            sign = ""
            if coeff > 0:
                sign = f" {C.BOLD}+ "
            else:
                sign = f" {C.BOLD}- "
            
            coeff = abs(coeff)

            # --- Coeficiente ---
            coeff_str = ""
            if coeff != 1 or power == 0:
                coeff_str = f"{C.OKCYAN}{coeff:g}{C.ENDC}"

            # --- Potencia (x) ---
            power_str = ""
            if power == 1:
                power_str = f"{C.OKGREEN}x{C.ENDC}"
            elif power > 1:
                power_str = f"{C.OKGREEN}x{to_superscript(power)}{C.ENDC}"

            terms.append(f"{sign}{coeff_str}{power_str}")

        # --- CORRECCIÓN DEL BUG "0" ---
        # Unimos los términos y eliminamos el espacio en blanco INICIAL
        result = "".join(terms).lstrip() 

        # Ahora comprobamos la cadena SIN el espacio inicial
        if result.startswith(f"{C.BOLD}+ "):
            # Quitamos el "+ " (con color) del principio
            return result[len(f"{C.BOLD}+ "):]
        
        if result.startswith(f"{C.BOLD}- "):
            # Quitamos el "- " (con color) y lo re-añadimos sin el espacio
            return f"{C.BOLD}-{C.ENDC}" + result[len(f"{C.BOLD}- "):]
        
        # Fallback en caso de que algo salga mal
        return "Error al formatear" 
    # =================================================================
    # FIN DE LA CORRECCIÓN
    # =================================================================

    def __repr__(self):
        return f"Polynomial({self.coeffs})"

    def __eq__(self, other):
        return self.coeffs == other.coeffs

    def __add__(self, other):
        len1, len2 = len(self.coeffs), len(other.coeffs)
        new_len = max(len1, len2)
        c1 = self.coeffs + [0] * (new_len - len1)
        c2 = other.coeffs + [0] * (new_len - len2)
        result_coeffs = [c1[i] + c2[i] for i in range(new_len)]
        return Polynomial(result_coeffs)

    def __sub__(self, other):
        len1, len2 = len(self.coeffs), len(other.coeffs)
        new_len = max(len1, len2)
        c1 = self.coeffs + [0] * (new_len - len1)
        c2 = other.coeffs + [0] * (new_len - len2)
        result_coeffs = [c1[i] - c2[i] for i in range(new_len)]
        return Polynomial(result_coeffs)

    def __mul__(self, other):
        deg1, deg2 = self.degree(), other.degree()
        if deg1 == -math.inf or deg2 == -math.inf:
            return Polynomial([0])
        result_coeffs = [0] * (deg1 + deg2 + 1)
        for i, coeff1 in enumerate(self.coeffs):
            for j, coeff2 in enumerate(other.coeffs):
                result_coeffs[i + j] += coeff1 * coeff2
        return Polynomial(result_coeffs)

    def __divmod__(self, other):
        if other.coeffs == [0]:
            raise ZeroDivisionError("División por polinomio cero")
        num, den = list(self.coeffs), list(other.coeffs)
        deg_num, deg_den = len(num) - 1, len(den) - 1
        if deg_num < deg_den:
            return Polynomial([0]), Polynomial(num)
        q_coeffs = [0] * (deg_num - deg_den + 1)
        while deg_num >= deg_den and num != [0]:
            d = num[-1] / den[-1]
            pos = deg_num - deg_den
            q_coeffs[pos] = d
            for i, coeff_den in enumerate(den):
                idx = i + pos
                if idx < len(num):
                    num[idx] -= d * coeff_den
            while len(num) > 1 and num[-1] == 0: num.pop()
            if not num: num = [0]
            deg_num = len(num) - 1
        return Polynomial(q_coeffs), Polynomial(num)

    def __truediv__(self, other):
        return self.__divmod__(other)[0]

    def __mod__(self, other):
        return self.__divmod__(other)[1]

# -------------------------------------------------------------------
# 4. FUNCIONES DEL PROGRAMA INTERACTIVO (CON CARACTERES Unicode)
# -------------------------------------------------------------------

def get_polynomial_from_user(prompt_message):
    """Pide al usuario los coeficientes de un polinomio."""
    # Versión con caracteres de caja Unicode
    print(f"\n{C.BOLD}{C.HEADER}╔{'═' * (len(prompt_message) + 2)}╗{C.ENDC}")
    print(f"{C.BOLD}{C.HEADER}║ {prompt_message} ║{C.ENDC}")
    print(f"{C.BOLD}{C.HEADER}╚{'═' * (len(prompt_message) + 2)}╝{C.ENDC}")
    
    print(f"{C.WARNING}IMPORTANTE:{C.ENDC} Del término constante ({C.OKGREEN}x⁰{C.ENDC}) al de mayor grado.")
    print(f"Ejemplo: para '3x² + 2x - 5', escribe: {C.OKCYAN}-5 2 3{C.ENDC}")
    
    while True:
        raw_input = input(f"{C.OKCYAN}Coeficientes {C.BOLD}»{C.ENDC} ")
        if not raw_input:
            print(f"{C.FAIL}Entrada vacía. Inténtalo de nuevo.{C.ENDC}")
            continue
            
        try:
            coeffs = [float(c) for c in raw_input.split()]
            return Polynomial(coeffs)
        except ValueError:
            print(f"{C.FAIL}Error: Asegúrate de introducir solo números separados por espacios.{C.ENDC}")

def show_menu():
    """Muestra el menú de opciones con colores y símbolos."""
    print(f"\n{C.BOLD}--- ¿Qué operación deseas realizar? ---{C.ENDC}")
    print(f" {C.OKBLUE}1.{C.ENDC} Sumar        (P1 {C.BOLD}➕{C.ENDC} P2)")
    print(f" {C.OKBLUE}2.{C.ENDC} Restar       (P1 {C.BOLD}➖{C.ENDC} P2)")
    print(f" {C.OKBLUE}3.{C.ENDC} Multiplicar  (P1 {C.BOLD}✖️{C.ENDC} P2)")
    print(f" {C.OKBLUE}4.{C.ENDC} Dividir      (P1 {C.BOLD}➗{C.ENDC} P2)")
    print(f" {C.WARNING}5.{C.ENDC} Introducir nuevos polinomios 🔁")
    print(f" {C.FAIL}6.{C.ENDC} Salir 🚪")
    
    while True:
        choice = input(f"\n{C.BOLD}Selecciona una opción (1-6) {C.HEADER}»{C.ENDC} ")
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        else:
            print(f"{C.FAIL}Opción no válida. Introduce un número del 1 al 6.{C.ENDC}")

def print_result_box(title, p1, p2, op_symbol, result):
    """Imprime un cuadro de resultado formateado."""
    print(f"\n{C.BOLD}{C.OKGREEN}┌─[ {title} ]{'─' * (32 - len(title))}┐{C.ENDC}")
    print(f"{C.OKGREEN}│{C.ENDC} ({p1}) {C.BOLD}{op_symbol}{C.ENDC} ({p2})")
    print(f"{C.OKGREEN}│{C.ENDC} {C.BOLD}= {result}{C.ENDC}")
    print(f"{C.BOLD}{C.OKGREEN}└{'─' * 38}┘{C.ENDC}")

# -------------------------------------------------------------------
# 5. FUNCIÓN PRINCIPAL (MAIN)
# -------------------------------------------------------------------

def main():
    """Bucle principal de la calculadora de polinomios."""
    print(f"{C.BOLD}{C.HEADER}╔{'═' * 42}╗{C.ENDC}")
    print(f"{C.BOLD}{C.HEADER}║   CALCULADORA DE POLINOMIOS VISUAL   ║{C.ENDC}")
    print(f"{C.BOLD}{C.HEADER}╚{'═' * 42}╝{C.ENDC}")
    
    P1 = get_polynomial_from_user("Introduce el Polinomio 1 (P1)")
    P2 = get_polynomial_from_user("Introduce el Polinomio 2 (P2)")

    while True:
        print("\n" + f"{C.HEADER}╞{'═' * 10} POLINOMIOS ACTUALES {'═' * 11}╡{C.ENDC}")
        print(f"{C.BOLD} P1(x) │ {P1}{C.ENDC}")
        print(f"{C.BOLD} P2(x) │ {P2}{C.ENDC}")
        print(f"{C.HEADER}╞{'═' * 42}╡{C.ENDC}")

        choice = show_menu()

        if choice == '1': # Sumar
            result = P1 + P2
            print_result_box("SUMA", P1, P2, '➕', result)
        
        elif choice == '2': # Restar
            result = P1 - P2
            print_result_box("RESTA", P1, P2, '➖', result)
            
        elif choice == '3': # Multiplicar
            result = P1 * P2
            print_result_box("MULTIPLICACIÓN", P1, P2, '✖️', result)

        elif choice == '4': # Dividir
            print(f"\n{C.BOLD}{C.OKGREEN}┌─[ DIVISIÓN ]{'─' * 26}┐{C.ENDC}")
            try:
                quotient = P1 / P2
                remainder = P1 % P2
                print(f"{C.OKGREEN}│{C.ENDC} ({P1}) {C.BOLD}➗{C.ENDC} ({P2})")
                print(f"{C.OKGREEN}│{C.ENDC} {C.BOLD}Cociente:  {quotient}{C.ENDC}")
                print(f"{C.OKGREEN}│{C.ENDC} {C.BOLD}Resto:     {remainder}{C.ENDC}")
            except ZeroDivisionError:
                print(f"{C.OKGREEN}│{C.ENDC} {C.FAIL}Error: No se puede dividir por el polinomio cero (0).{C.ENDC}")
            print(f"{C.BOLD}{C.OKGREEN}└{'─' * 38}┘{C.ENDC}")
        
        elif choice == '5': # Cambiar polinomios
            P1 = get_polynomial_from_user("Introduce el NUEVO Polinomio 1 (P1)")
            P2 = get_polynomial_from_user("Introduce el NUEVO Polinomio 2 (P2)")
            
        elif choice == '6': # Salir
            print(f"\n{C.OKCYAN}¡Saliendo de la calculadora! ¡Adiós! 👋{C.ENDC}")
            break

# Ejecutar el programa principal
if __name__ == "__main__":
    main()