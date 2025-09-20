"""
API REST para resolver sistemas lineales n×n
Backend en Flask que expone los métodos: Gauss, Gauss-Jordan, LU, Thomas
"""
from flask import Flask, request, jsonify
from sistemas_lineales import solve_gauss, solve_gauss_jordan, lu_decompose, solve_lu, solve_thomas, is_tridiagonal, nombres_variables, fraction_str
from fractions import Fraction
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/solve', methods=['POST'])
def solve():
    data = request.get_json()
    metodo = data.get('metodo')
    A = data.get('A')
    b = data.get('b')
    pivoteo = data.get('pivoteo', True)
    verbose = True
    try:
        if metodo == 'gauss':
            resultado, _ = solve_gauss(A, b, pivoteo, verbose=True)
        elif metodo == 'gauss-jordan':
            resultado, _ = solve_gauss_jordan(A, b, pivoteo, verbose=True)
        elif metodo == 'lu':
            L, U = lu_decompose(A)
            pasos = []
            n = len(A)
            # Paso 1: mostrar L y U
            pasos.append({
                "descripcion": "Matriz L obtenida:",
                "matriz_aumentada": [[fraction_str(x) for x in fila] for fila in L],
                "b": None,
                "pivote": None,
                "operacion": "L"
            })
            pasos.append({
                "descripcion": "Matriz U obtenida:",
                "matriz_aumentada": [[fraction_str(x) for x in fila] for fila in U],
                "b": None,
                "pivote": None,
                "operacion": "U"
            })
            # Paso 2: sustitución hacia adelante (Ly=b)
            b_frac = [Fraction(x).limit_denominator() for x in b]
            y = [Fraction(0)]*n
            for i in range(n):
                suma = sum(L[i][j]*y[j] for j in range(i))
                y[i] = (b_frac[i] - suma)/L[i][i]
                pasos.append({
                    "descripcion": f"Sustitución hacia adelante: y[{i+1}] = ({fraction_str(b_frac[i])} - {fraction_str(suma)}) / {fraction_str(L[i][i])}",
                    "matriz_aumentada": None,
                    "b": [fraction_str(val) for val in y],
                    "pivote": {"fila": i+1, "valor": fraction_str(L[i][i])},
                    "operacion": f"y[{i+1}]"
                })
            # Paso 3: sustitución hacia atrás (Ux=y)
            x = [Fraction(0)]*n
            for i in range(n-1, -1, -1):
                suma = sum(U[i][j]*x[j] for j in range(i+1, n))
                x[i] = (y[i] - suma)/U[i][i] if abs(U[i][i]) > 1e-12 else Fraction(0)
                pasos.append({
                    "descripcion": f"Sustitución hacia atrás: x[{i+1}] = ({fraction_str(y[i])} - {fraction_str(suma)}) / {fraction_str(U[i][i])}",
                    "matriz_aumentada": None,
                    "b": [fraction_str(val) for val in x],
                    "pivote": {"fila": i+1, "valor": fraction_str(U[i][i])},
                    "operacion": f"x[{i+1}]"
                })
            variables = nombres_variables(n)
            solucion = {variables[i]: fraction_str(x[i]) for i in range(n)}
            resultado = {
                "metodo": "lu",
                "n": n,
                "pasos": pasos,
                "solucion": {"variables": solucion, "vector": [fraction_str(xi) for xi in x]},
                "advertencias": [],
                "residuo": None
            }
        elif metodo == 'thomas':
            if not is_tridiagonal(A):
                return jsonify({"error": "La matriz no es tridiagonal."}), 400
            n = len(A)
            a = [A[i][i-1] if i > 0 else 0.0 for i in range(n)][1:]
            b_diag = [A[i][i] for i in range(n)]
            c = [A[i][i+1] if i < n-1 else 0.0 for i in range(n)][:-1]
            resultado, _ = solve_thomas(a, b_diag, c, b, verbose=True)
        else:
            return jsonify({"error": "Método no reconocido."}), 400
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
