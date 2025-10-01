import math
from fractions import Fraction
def cholesky(A, b):
    n = len(A)
    pasos = []
    A = [[Fraction(x).limit_denominator(1000) for x in fila] for fila in A]
    b = [Fraction(x).limit_denominator(1000) for x in b]
    # Validar simetría
    for i in range(n):
        for j in range(n):
            if A[i][j] != A[j][i]:
                raise Exception('La matriz no es simétrica: Cholesky solo aplica a matrices simétricas definidas positivas.')
    L = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    # Factorización L
    for i in range(n):
        for j in range(i+1):
            suma = sum(L[i][k]*L[j][k] for k in range(j))
            if i == j:
                val = A[i][i] - suma
                if val < 0:
                    raise Exception('La matriz no es definida positiva: Cholesky solo aplica a matrices simétricas definidas positivas.')
                L[i][j] = Fraction(math.sqrt(float(val))).limit_denominator(1000)
            else:
                L[i][j] = (A[i][j] - suma) / L[j][j]
        pasos.append({'descripcion': f'Construcción de L, fila {i+1}', 'matriz': [[str(L[ii][jj]) for jj in range(n)] for ii in range(n)]})
    # Ly = b (sustitución hacia adelante)
    y = [Fraction(0)] * n
    for i in range(n):
        y[i] = (b[i] - sum(L[i][j]*y[j] for j in range(i))) / L[i][i]
        pasos.append({'descripcion': f'Sustitución hacia adelante: y{i+1} = {y[i]}', 'sustitucion': f'y{i+1} = {y[i]}'})
    # L^T x = y (sustitución hacia atrás)
    x = [Fraction(0)] * n
    for i in range(n-1, -1, -1):
        x[i] = (y[i] - sum(L[j][i]*x[j] for j in range(i+1, n))) / L[i][i]
        pasos.append({'descripcion': f'Sustitución hacia atrás: x{i+1} = {x[i]}', 'sustitucion': f'x{i+1} = {x[i]}'})
    # Calcular la solución exacta con Gauss para mostrarla al final
    _, solucion_gauss = gauss([[float(xx) for xx in fila] for fila in A], [float(bb) for bb in b])
    return pasos, solucion_gauss

def jacobi(A, b, max_iter=100, tol=1e-4):
    n = len(A)
    pasos = []
    A = [[float(x) for x in fila] for fila in A]
    b = [float(x) for x in b]
    x = [0.0]*n
    # Tabla de iteraciones: guardamos la evolución de las variables en cada iteración
    tabla = []
    tabla.append({'iter': 0, 'values': [f'{v:.12f}' for v in x], 'note': 'Inicial'})
    for it in range(1, max_iter+1):
        x_new = [0.0]*n
        for i in range(n):
            s = sum(A[i][j]*x[j] for j in range(n) if j != i)
            x_new[i] = (b[i] - s) / A[i][i]
        # calcular error por variable y máximo cambio para esta iteración
        errors = [abs((x_new[i] - x[i]) / x_new[i]) if x_new[i] != 0 else 0.0 for i in range(n)]
        max_diff = max(errors) if errors else 0.0

        # registrar en pasos y en la tabla (ambos contienen la misma info por iteración)
        iter_entry = {
            'descripcion': f'Iteración {it}',
            'iter': it,
            'values': [f'{v:.12f}' for v in x_new],
            'errors': [f'{e:.8f}' for e in errors],
            'max_diff': f'{max_diff:.8f}'
        }
        pasos.append(iter_entry)
        tabla.append(iter_entry.copy())

        # actualizar el vector para la siguiente iteración
        x = x_new

        # criterio de convergencia: todos los errores por variable < tol (estricto)
        if all(e < tol for e in errors):
            pasos.append({'descripcion': f'Convergió en {it} iteraciones (no se muestra la solución aquí)'} )
            pasos.append({'descripcion': 'Tabla de iteraciones', 'tabla': tabla})
            # Devolvemos pasos y la tabla (la UI usará la tabla para mostrar iteraciones)
            return pasos, tabla
    pasos.append({'descripcion': f'No convergió tras {max_iter} iteraciones'})
    pasos.append({'descripcion': 'Tabla de iteraciones', 'tabla': tabla})
    return pasos, tabla
def gauss_seidel(A, b, max_iter=100, tol=1e-4):
    n = len(A)
    pasos = []
    A = [[float(x) for x in fila] for fila in A]
    b = [float(x) for x in b]
    x = [0.0]*n
    # Tabla de iteraciones para Gauss-Seidel (valores se actualizan en cada paso)
    tabla = []
    tabla.append({'iter': 0, 'values': [f'{v:.12f}' for v in x], 'note': 'Inicial'})
    for it in range(1, max_iter+1):
        x_old = x.copy()
        for i in range(n):
            s1 = sum(A[i][j]*x[j] for j in range(i))
            s2 = sum(A[i][j]*x_old[j] for j in range(i+1, n))
            # aquí x[j] ya contiene los valores más recientes para j < i (Gauss-Seidel)
            x[i] = (b[i] - s1 - s2) / A[i][i]
        # error por variable y máximo cambio
        errors = [abs(x[i] - x_old[i]) for i in range(n)]
        max_diff = max(errors) if errors else 0.0

        # registrar en pasos y tabla
        iter_entry = {
            'descripcion': f'Iteración {it}',
            'iter': it,
            'values': [f'{v:.12f}' for v in x],
            'errors': [f'{e:.8f}' for e in errors],
            'max_diff': f'{max_diff:.8f}'
        }
        pasos.append(iter_entry)
        tabla.append(iter_entry.copy())

        # criterio de convergencia: todos los errores por variable < tol (estricto)
        if all(e < tol for e in errors):
            pasos.append({'descripcion': f'Convergió en {it} iteraciones (no se muestra la solución aquí)'})
            pasos.append({'descripcion': 'Tabla de iteraciones', 'tabla': tabla})
            return pasos, tabla

    pasos.append({'descripcion': f'No convergió tras {max_iter} iteraciones'})
    pasos.append({'descripcion': 'Tabla de iteraciones', 'tabla': tabla})
    return pasos, tabla
from flask import Flask, render_template, request, jsonify
from fractions import Fraction
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


def gauss(A, b):
    n = len(A)
    pasos = []
    A = [[Fraction(x).limit_denominator(1000) for x in fila] for fila in A]
    b = [Fraction(x).limit_denominator(1000) for x in b]
    # Eliminación hacia adelante
    for k in range(n-1):
        for i in range(k+1, n):
            if abs(A[k][k]) < 1e-12:
                pasos.append({'descripcion': f'Pivote cero en fila {k+1}', 'matriz': None})
                continue
            factor = A[i][k] / A[k][k]
            for j in range(k, n):
                A[i][j] -= factor * A[k][j]
            b[i] -= factor * b[k]
            pasos.append({
                'descripcion': f'Eliminación: R{i+1} ← R{i+1} - ({factor})·R{k+1}',
                'matriz': [[str(A[ii][jj]) for jj in range(n)] + [str(b[ii])] for ii in range(n)]
            })
    # Sustitución hacia atrás
    x = [Fraction(0)] * n
    for i in range(n-1, -1, -1):
        suma = sum(A[i][j]*x[j] for j in range(i+1, n))
        x[i] = (b[i] - suma) / (A[i][i] if abs(A[i][i]) > 1e-12 else 1)
        pasos.append({
            'descripcion': f'Sustitución hacia atrás: x{i+1} = ({b[i]} - {suma}) / {A[i][i]} = {x[i]}',
            'sustitucion': f'x{i+1} = {x[i]}'
        })
        solucion = [str(xi) for xi in x]
    return pasos, solucion

def gauss_jordan(A, b):
    n = len(A)
    pasos = []
    A = [[Fraction(x).limit_denominator(1000) for x in fila] for fila in A]
    b = [Fraction(x).limit_denominator(1000) for x in b]
    for k in range(n):
        if abs(A[k][k]) < 1e-12:
            pasos.append({'descripcion': f'Pivote cero en fila {k+1}', 'matriz': None})
            continue
        piv = A[k][k]
        for j in range(k, n):
            A[k][j] /= piv
        b[k] /= piv
        pasos.append({
            'descripcion': f'Normalización: R{k+1} ← R{k+1} / ({piv})',
            'matriz': [[str(A[ii][jj]) for jj in range(n)] + [str(b[ii])] for ii in range(n)]
        })
        for i in range(n):
            if i != k:
                factor = A[i][k]
                for j in range(k, n):
                    A[i][j] -= factor * A[k][j]
                b[i] -= factor * b[k]
                pasos.append({
                    'descripcion': f'Eliminación: R{i+1} ← R{i+1} - ({factor})·R{k+1}',
                    'matriz': [[str(A[ii][jj]) for jj in range(n)] + [str(b[ii])] for ii in range(n)]
                })
    x = [str(b[i]) for i in range(n)]
    pasos.append({'descripcion': 'Solución final', 'vector': x})
    return pasos, x

def lu(A, b):
    n = len(A)
    pasos = []
    A = [[Fraction(x).limit_denominator(1000) for x in fila] for fila in A]
    b = [Fraction(x).limit_denominator(1000) for x in b]
    L = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    U = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    # Factorización
    for i in range(n):
        for j in range(i, n):
            U[i][j] = A[i][j] - sum(L[i][k]*U[k][j] for k in range(i))
        for j in range(i, n):
            if i == j:
                L[i][i] = 1
            else:
                L[j][i] = (A[j][i] - sum(L[j][k]*U[k][i] for k in range(i))) / U[i][i]
        pasos.append({'descripcion': f'Construcción de L y U, fila {i+1}', 'L': [[str(L[ii][jj]) for jj in range(n)] for ii in range(n)], 'U': [[str(U[ii][jj]) for jj in range(n)] for ii in range(n)]})
    pasos.append({'descripcion': 'Matriz L final', 'matriz': [[str(L[ii][jj]) for jj in range(n)] for ii in range(n)]})
    pasos.append({'descripcion': 'Matriz U final', 'matriz': [[str(U[ii][jj]) for jj in range(n)] for ii in range(n)]})
    # Ly = b (sustitución hacia adelante)
    y = [Fraction(0)] * n
    for i in range(n):
        y[i] = b[i] - sum(L[i][j]*y[j] for j in range(i))
        pasos.append({'descripcion': f'Sustitución hacia adelante: y{i+1} = {y[i]}', 'sustitucion': f'y{i+1} = {y[i]}'})
    # Ux = y (sustitución hacia atrás)
    x = [Fraction(0)] * n
    for i in range(n-1, -1, -1):
        x[i] = (y[i] - sum(U[i][j]*x[j] for j in range(i+1, n))) / U[i][i]
        pasos.append({'descripcion': f'Sustitución hacia atrás: x{i+1} = {x[i]}', 'sustitucion': f'x{i+1} = {x[i]}'})
    return pasos, [str(xi) for xi in x]

@app.route('/api/solve', methods=['POST'])
def solve():
    data = request.get_json()
    A = data.get('A')
    b = data.get('b')
    metodo = data.get('metodo', 'gauss')
    n = len(A)
    if metodo == 'gauss':
        pasos, solucion = gauss(A, b)
    elif metodo == 'gauss-jordan':
        pasos, solucion = gauss_jordan(A, b)
    elif metodo == 'lu':
        pasos, solucion = lu(A, b)
    elif metodo == 'cholesky':
        pasos, solucion = cholesky(A, b)
    elif metodo == 'jacobi':
        pasos, solucion = jacobi(A, b)
    elif metodo == 'gauss-seidel':
        pasos, solucion = gauss_seidel(A, b)
    else:
        return jsonify({'error': 'Método no soportado'}), 400
    return jsonify({'pasos': pasos, 'solucion': solucion, 'n': n})

if __name__ == '__main__':
    app.run(debug=True)
