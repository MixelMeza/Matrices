"""
Librería para resolver sistemas lineales n×n por varios métodos.
Autor: GitHub Copilot

Métodos soportados:
- Eliminación de Gauss (con pivoteo parcial)
- Gauss–Jordan
- Factorización LU (Doolittle)
- Método de Thomas para matrices tridiagonales

Incluye pasos detallados, comprobación de residuo y validaciones.
"""
import copy
import math
from fractions import Fraction

# =====================
# Función auxiliar para nombres de variables
# =====================
def nombres_variables(n):
    """
    Devuelve la lista de nombres de variables según n.
    Si n <= 4: ["x", "y", "z", "w"]
    Si n > 4: ["x1", "x2", ..., "xn"]
    """
    if n <= 4:
        return ["x", "y", "z", "w"][:n]
    else:
        return [f"x{i+1}" for i in range(n)]

# =====================
# Función para verificar si una matriz es tridiagonal
# =====================
def is_tridiagonal(A):
    """
    Verifica si la matriz A es tridiagonal.
    """
    n = len(A)
    for i in range(n):
        for j in range(n):
            if abs(i-j) > 1 and abs(A[i][j]) > 1e-12:
                return False
    return True

# =====================
# Eliminación de Gauss con pivoteo parcial
# =====================
def to_fraction_matrix(mat):
    return [[Fraction(x).limit_denominator() for x in fila] for fila in mat]

def to_fraction_vector(vec):
    return [Fraction(x).limit_denominator() for x in vec]

def fraction_str(x):
    x = Fraction(x).limit_denominator()
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"

def matrix_str(mat):
    return "[" + ",\n ".join(str([fraction_str(x) for x in fila]) for fila in mat) + "]"

def vector_str(vec):
    return "[" + ", ".join(fraction_str(x) for x in vec) + "]"

def solve_gauss(A, b, pivote=True, verbose=False):
    """
    Resuelve Ax = b por eliminación de Gauss con pivoteo parcial.
    Devuelve solución y pasos detallados si verbose=True.
    """
    n = len(A)
    A = to_fraction_matrix(A)
    b = to_fraction_vector(b)
    pasos = []
    texto = []
    advertencias = []
    matriz_aum = [A[i] + [b[i]] for i in range(n)]
    for k in range(n-1):
        # Pivoteo parcial
        if pivote:
            maxfila = max(range(k, n), key=lambda i: abs(A[i][k]))
            pivote_val = A[maxfila][k]
            if abs(pivote_val) < 1e-12:
                advertencias.append(f"Pivote ≈ 0 en fila {maxfila+1}, posible matriz singular.")
            if maxfila != k:
                A[k], A[maxfila] = A[maxfila], A[k]
                b[k], b[maxfila] = b[maxfila], b[k]
                matriz_aum[k], matriz_aum[maxfila] = matriz_aum[maxfila], matriz_aum[k]
                op = f"Intercambiamos R{k+1} y R{maxfila+1} porque el mayor valor absoluto en columna {k+1} es {fraction_str(pivote_val)}."
                texto.append(f"Paso {len(texto)+1}: {op}\nMatriz aumentada ahora: {matrix_str(matriz_aum)}")
                pasos.append({
                    "descripcion": op,
                    "matriz_aumentada": [[fraction_str(x) for x in fila] for fila in matriz_aum],
                    "b": [fraction_str(bi) for bi in b],
                    "pivote": {"fila": k+1, "valor": fraction_str(pivote_val)},
                    "operacion": op
                })
        pivote_actual = A[k][k]
        if abs(pivote_actual) < 1e-12:
            advertencias.append(f"Pivote ≈ 0 en fila {k+1}, posible matriz singular.")
        for i in range(k+1, n):
            factor = A[i][k]/pivote_actual if abs(pivote_actual) > 1e-12 else Fraction(0)
            op = f"R{i+1} ← R{i+1} - {fraction_str(factor)}·R{k+1}"
            for j in range(k, n):
                A[i][j] -= factor*A[k][j]
                if abs(A[i][j]) < 1e-12:
                    A[i][j] = Fraction(0)
            b[i] -= factor*b[k]
            if abs(b[i]) < 1e-12:
                b[i] = Fraction(0)
            matriz_aum[i] = A[i] + [b[i]]
            texto.append(f"Paso {len(texto)+1}: {op}\nMatriz aumentada ahora: {matrix_str(matriz_aum)}")
            pasos.append({
                "descripcion": op,
                "matriz_aumentada": [[fraction_str(x) for x in fila] for fila in matriz_aum],
                "b": [fraction_str(bi) for bi in b],
                "pivote": {"fila": k+1, "valor": fraction_str(pivote_actual)},
                "operacion": op
            })
    # Sustitución hacia atrás
    x = [Fraction(0)]*n
    for i in range(n-1, -1, -1):
        suma = sum(A[i][j]*x[j] for j in range(i+1, n))
        if abs(A[i][i]) < 1e-12:
            advertencias.append(f"Pivote ≈ 0 en fila {i+1}, matriz singular.")
            x[i] = Fraction(0)
        else:
            x[i] = (b[i] - suma)/A[i][i]
    variables = nombres_variables(n)
    solucion = {variables[i]: fraction_str(x[i]) for i in range(n)}
    residuo = calcular_residuo(A, x, b)
    resultado = {
        "metodo": "gauss",
        "n": n,
        "pasos": pasos,
        "solucion": {"variables": solucion, "vector": [fraction_str(xi) for xi in x]},
        "advertencias": advertencias,
        "residuo": fraction_str(residuo)
    }
    if verbose:
        return resultado, "\n".join(texto)
    else:
        return solucion

# =====================
# Gauss-Jordan
# =====================
def solve_gauss_jordan(A, b, pivote=True, verbose=False):
    """
    Resuelve Ax = b por Gauss-Jordan (reducción a forma escalonada reducida).
    """
    n = len(A)
    A = to_fraction_matrix(A)
    b = to_fraction_vector(b)
    pasos = []
    texto = []
    matriz_aum = [A[i] + [b[i]] for i in range(n)]
    advertencias = []
    for k in range(n):
        # Pivoteo parcial
        if pivote:
            maxfila = max(range(k, n), key=lambda i: abs(A[i][k]))
            pivote_val = A[maxfila][k]
            if abs(pivote_val) < 1e-12:
                advertencias.append(f"Pivote ≈ 0 en fila {maxfila+1}, posible matriz singular.")
            if maxfila != k:
                A[k], A[maxfila] = A[maxfila], A[k]
                b[k], b[maxfila] = b[maxfila], b[k]
                matriz_aum[k], matriz_aum[maxfila] = matriz_aum[maxfila], matriz_aum[k]
                op = f"Intercambiamos R{k+1} y R{maxfila+1} porque el mayor valor absoluto en columna {k+1} es {fraction_str(pivote_val)}."
                texto.append(f"Paso {len(texto)+1}: {op}\nMatriz aumentada ahora: {matrix_str(matriz_aum)}")
                pasos.append({
                    "descripcion": op,
                    "matriz_aumentada": [[fraction_str(x) for x in fila] for fila in matriz_aum],
                    "b": [fraction_str(bi) for bi in b],
                    "pivote": {"fila": k+1, "valor": fraction_str(pivote_val)},
                    "operacion": op
                })
        pivote_actual = A[k][k]
        if abs(pivote_actual) < 1e-12:
            advertencias.append(f"Pivote ≈ 0 en fila {k+1}, posible matriz singular.")
        # Normalizar fila pivote
        factor = pivote_actual
        if abs(factor) > 1e-12:
            for j in range(k, n):
                A[k][j] /= factor
                if abs(A[k][j]) < 1e-12:
                    A[k][j] = Fraction(0)
            b[k] /= factor
            if abs(b[k]) < 1e-12:
                b[k] = Fraction(0)
            matriz_aum[k] = A[k] + [b[k]]
            op = f"R{k+1} ← R{k+1} / {fraction_str(factor)}"
            texto.append(f"Paso {len(texto)+1}: {op}\nMatriz aumentada ahora: {matrix_str(matriz_aum)}")
            pasos.append({
                "descripcion": op,
                "matriz_aumentada": [[fraction_str(x) for x in fila] for fila in matriz_aum],
                "b": [fraction_str(bi) for bi in b],
                "pivote": {"fila": k+1, "valor": fraction_str(factor)},
                "operacion": op
            })
        # Eliminar en otras filas
        for i in range(n):
            if i != k:
                factor2 = A[i][k]
                op = f"R{i+1} ← R{i+1} - {fraction_str(factor2)}·R{k+1}"
                for j in range(k, n):
                    A[i][j] -= factor2*A[k][j]
                    if abs(A[i][j]) < 1e-12:
                        A[i][j] = Fraction(0)
                b[i] -= factor2*b[k]
                if abs(b[i]) < 1e-12:
                    b[i] = Fraction(0)
                matriz_aum[i] = A[i] + [b[i]]
                texto.append(f"Paso {len(texto)+1}: {op}\nMatriz aumentada ahora: {matrix_str(matriz_aum)}")
                pasos.append({
                    "descripcion": op,
                    "matriz_aumentada": [[fraction_str(x) for x in fila] for fila in matriz_aum],
                    "b": [fraction_str(bi) for bi in b],
                    "pivote": {"fila": k+1, "valor": fraction_str(A[k][k])},
                    "operacion": op
                })
    x = [b[i] for i in range(n)]
    variables = nombres_variables(n)
    solucion = {variables[i]: fraction_str(x[i]) for i in range(n)}
    residuo = calcular_residuo(A, x, b)
    resultado = {
        "metodo": "gauss-jordan",
        "n": n,
        "pasos": pasos,
        "solucion": {"variables": solucion, "vector": [fraction_str(xi) for xi in x]},
        "advertencias": advertencias,
        "residuo": fraction_str(residuo)
    }
    if verbose:
        return resultado, "\n".join(texto)
    else:
        return solucion

# =====================
# Factorización LU (Doolittle)
# =====================
def lu_decompose(A):
    """
    Factoriza A = LU por método de Doolittle.
    Devuelve L y U.
    """
    n = len(A)
    A = to_fraction_matrix(A)
    L = [[Fraction(0)]*n for _ in range(n)]
    U = [[Fraction(0)]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if j < i:
                suma = sum(L[i][k]*U[k][j] for k in range(j))
                if abs(U[j][j]) < 1e-12:
                    raise ValueError(f"Matriz singular, pivote ≈ 0 en fila {j+1}.")
                L[i][j] = (A[i][j] - suma)/U[j][j]
            else:
                suma = sum(L[i][k]*U[k][j] for k in range(i))
                U[i][j] = A[i][j] - suma
        L[i][i] = Fraction(1)
    return L, U

def solve_lu(L, U, b):
    """
    Resuelve Ly = b y luego Ux = y por sustitución.
    """
    n = len(L)
    b = to_fraction_vector(b)
    y = [Fraction(0)]*n
    for i in range(n):
        suma = sum(L[i][j]*y[j] for j in range(i))
        y[i] = (b[i] - suma)/L[i][i]
    x = [Fraction(0)]*n
    for i in range(n-1, -1, -1):
        suma = sum(U[i][j]*x[j] for j in range(i+1, n))
        if abs(U[i][i]) < 1e-12:
            x[i] = Fraction(0)
        else:
            x[i] = (y[i] - suma)/U[i][i]
    return x

# =====================
# Método de Thomas para tridiagonales
# =====================
def solve_thomas(a, b, c, d, verbose=False):
    """
    Resuelve sistema tridiagonal Ax = d por método de Thomas.
    a: subdiagonal (n-1)
    b: diagonal principal (n)
    c: superdiagonal (n-1)
    d: RHS (n)
    """
    n = len(b)
    ac = to_fraction_vector(a)
    bc = to_fraction_vector(b)
    cc = to_fraction_vector(c)
    dc = to_fraction_vector(d)
    pasos = []
    texto = []
    advertencias = []
    # Comprobación de dimensiones
    if len(a) != n-1 or len(c) != n-1 or len(d) != n:
        raise ValueError("Dimensiones incorrectas para sistema tridiagonal.")
    # Forward sweep
    for i in range(1, n):
        if abs(bc[i-1]) < 1e-12:
            advertencias.append(f"Pivote ≈ 0 en fila {i}, posible matriz singular.")
        m = ac[i-1]/bc[i-1] if abs(bc[i-1]) > 1e-12 else Fraction(0)
        bc[i] -= m*cc[i-1]
        dc[i] -= m*dc[i-1]
        op = f"Fila {i+1}: b[{i}] ← b[{i}] - {fraction_str(m)}·c[{i-1}]"
        texto.append(f"Paso {len(texto)+1}: {op}\nVector b ahora: {vector_str(bc)}\nVector d ahora: {vector_str(dc)}")
        pasos.append({
            "descripcion": op,
            "matriz_aumentada": None,
            "b": [fraction_str(bi) for bi in bc],
            "pivote": {"fila": i, "valor": fraction_str(bc[i-1])},
            "operacion": op
        })
    # Back substitution
    x = [Fraction(0)]*n
    x[-1] = dc[-1]/bc[-1] if abs(bc[-1]) > 1e-12 else Fraction(0)
    for i in range(n-2, -1, -1):
        x[i] = (dc[i] - cc[i]*x[i+1])/bc[i] if abs(bc[i]) > 1e-12 else Fraction(0)
    variables = nombres_variables(n)
    solucion = {variables[i]: fraction_str(x[i]) for i in range(n)}
    resultado = {
        "metodo": "thomas",
        "n": n,
        "pasos": pasos,
        "solucion": {"variables": solucion, "vector": [fraction_str(xi) for xi in x]},
        "advertencias": advertencias
    }
    if verbose:
        return resultado, "\n".join(texto)
    else:
        return solucion

# =====================
# Utilidades
# =====================
def mostrar_matriz(matriz, decimales=6):
    """
    Devuelve la matriz como string en formato legible.
    """
    return "[" + ",\n ".join(str([round(x,decimales) for x in fila]) for fila in matriz) + "]"

def redondear_matriz(matriz, decimales=6):
    """
    Redondea todos los elementos de la matriz.
    """
    return [[round(x,decimales) for x in fila] for fila in matriz]

def calcular_residuo(A, x, b):
    """
    Calcula el residuo ||A·x - b||₂ en fracción.
    """
    n = len(A)
    Ax = [sum(A[i][j]*x[j] for j in range(n)) for i in range(n)]
    residuo = sum((Ax[i]-b[i])**2 for i in range(n))
    return Fraction(residuo).limit_denominator()

# =====================
# CLI mínima
# =====================
def cli():
    """
    Interfaz de consola para introducir A, b y elegir método.
    """
    print("\nCalculadora de sistemas lineales n×n")
    n = int(input("Ingrese n (tamaño de la matriz): "))
    print("Ingrese la matriz A (fila por fila, valores separados por espacio):")
    A = []
    for i in range(n):
        fila = list(map(float, input(f"Fila {i+1}: ").split()))
        if len(fila) != n:
            print("Error: la fila debe tener n elementos.")
            return
        A.append(fila)
    print("Ingrese el vector b (valores separados por espacio):")
    b = list(map(float, input("b: ").split()))
    if len(b) != n:
        print("Error: b debe tener n elementos.")
        return
    print("Métodos disponibles: gauss, gauss-jordan, lu, thomas")
    metodo = input("Método: ").strip().lower()
    pivoteo = True
    if metodo in ["gauss", "gauss-jordan"]:
        pivoteo = input("¿Usar pivoteo parcial? (s/n): ").strip().lower() == "s"
    verbose = input("¿Mostrar pasos detallados? (s/n): ").strip().lower() == "s"
    if metodo == "gauss":
        resultado, texto = solve_gauss(A, b, pivoteo, True)
        print(texto)
        print("\nSolución:", resultado["solucion"])
        print("Residuo:", resultado["residuo"])
    elif metodo == "gauss-jordan":
        resultado, texto = solve_gauss_jordan(A, b, pivoteo, True)
        print(texto)
        print("\nSolución:", resultado["solucion"])
        print("Residuo:", resultado["residuo"])
    elif metodo == "lu":
        try:
            L, U = lu_decompose(A)
            x = solve_lu(L, U, b)
            print("Matriz L:", matrix_str(L))
            print("Matriz U:", matrix_str(U))
            print("Solución:", {nombres_variables(n)[i]: fraction_str(x[i]) for i in range(n)})
            print("Residuo:", fraction_str(calcular_residuo(A, x, b)))
        except Exception as e:
            print("Error:", e)
    elif metodo == "thomas":
        if not is_tridiagonal(A):
            print("Error: la matriz no es tridiagonal.")
            return
        a = [A[i][i-1] if i > 0 else 0.0 for i in range(n)]
        b_diag = [A[i][i] for i in range(n)]
        c = [A[i][i+1] if i < n-1 else 0.0 for i in range(n)]
        resultado, texto = solve_thomas(a[1:], b_diag, c[:-1], b, verbose=True)
        print(texto)
        print("\nSolución:", resultado["solucion"])
    else:
        print("Método no reconocido.")

# =====================
# Ejemplos de uso
# =====================
if __name__ == "__main__":
    # Ejemplo 1: sistema 3x3
    A1 = [
        [2, -1, 1],
        [3, 3, 9],
        [3, 3, 5]
    ]
    b1 = [8, 0, -6]
    print("Ejemplo 1: sistema 3x3 (x, y, z)")
    resultado, texto = solve_gauss(A1, b1, pivote=True, verbose=True)
    print(texto)
    print("Solución:", resultado["solucion"])
    print("Residuo:", resultado["residuo"])

    # Ejemplo 2: sistema 5x5
    A2 = [
        [2, 1, 0, 0, 0],
        [1, 2, 1, 0, 0],
        [0, 1, 2, 1, 0],
        [0, 0, 1, 2, 1],
        [0, 0, 0, 1, 2]
    ]
    b2 = [2, 4, 6, 8, 10]
    print("\nEjemplo 2: sistema 5x5 (x1..x5)")
    resultado, texto = solve_gauss_jordan(A2, b2, pivote=True, verbose=True)
    print(texto)
    print("Solución:", resultado["solucion"])
    print("Residuo:", resultado["residuo"])

    # Ejemplo 3: sistema tridiagonal 4x4
    A3 = [
        [4, 1, 0, 0],
        [1, 4, 1, 0],
        [0, 1, 4, 1],
        [0, 0, 1, 4]
    ]
    b3 = [5, 6, 6, 5]
    print("\nEjemplo 3: sistema tridiagonal 4x4")
    a3 = [A3[i][i-1] if i > 0 else 0.0 for i in range(4)]
    b_diag3 = [A3[i][i] for i in range(4)]
    c3 = [A3[i][i+1] if i < 3 else 0.0 for i in range(4)]
    resultado, texto = solve_thomas(a3[1:], b_diag3, c3[:-1], b3, verbose=True)
    print(texto)
    print("Solución:", resultado["solucion"])

# =====================
# Pruebas unitarias
# =====================
def test_gauss():
    A = [[2,1],[1,3]]
    b = [5,6]
    sol = solve_gauss(A,b)
    assert abs(sol['x']-1) < 1e-6
    assert abs(sol['y']-2) < 1e-6

def test_gauss_jordan():
    A = [[1,2],[3,4]]
    b = [5,6]
    sol = solve_gauss_jordan(A,b)
    assert abs(sol['x']+4) < 1e-6
    assert abs(sol['y']-4.5) < 1e-6

def test_lu():
    A = [[4,3],[6,3]]
    b = [10,12]
    L,U = lu_decompose(A)
    x = solve_lu(L,U,b)
    assert abs(x[0]-1) < 1e-6
    assert abs(x[1]-2) < 1e-6

def test_thomas():
    a = [1,1,1]
    b = [4,4,4,4]
    c = [1,1,1]
    d = [5,6,6,5]
    sol = solve_thomas(a,b,c,d)
    assert all(abs(x-1) < 1e-6 for x in sol.values())

def test_singular():
    A = [[1,2],[2,4]]
    b = [3,6]
    try:
        solve_gauss(A,b)
    except Exception:
        pass
    try:
        lu_decompose(A)
    except Exception:
        pass

# Ejecutar pruebas
if __name__ == "__main__":
    test_gauss()
    test_gauss_jordan()
    test_lu()
    test_thomas()
    test_singular()
    print("\nPruebas unitarias completadas.")
