from flask import Flask, render_template, request, jsonify
from fractions import Fraction
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/solve', methods=['POST'])
def solve():
    data = request.get_json()
    A = data.get('A')
    b = data.get('b')
    n = len(A)
    pasos = []
    # Gauss simple con fracciones
    A = [[Fraction(x).limit_denominator(1000) for x in fila] for fila in A]
    b = [Fraction(x).limit_denominator(1000) for x in b]
    for k in range(n-1):
        for i in range(k+1, n):
            if abs(A[k][k]) < 1e-12:
                pasos.append({'descripcion': f'Pivote cero en fila {k+1}', 'matriz': None})
                continue
            factor = A[i][k] / A[k][k]
            for j in range(k, n):
                A[i][j] -= factor * A[k][j]
            b[i] -= factor * b[k]
            pasos.append({'descripcion': f'R{i+1} ← R{i+1} - ({factor})·R{k+1}', 'matriz': [[str(A[ii][jj]) for jj in range(n)] + [str(b[ii])] for ii in range(n)]})
    x = [Fraction(0)] * n
    for i in range(n-1, -1, -1):
        suma = sum(A[i][j]*x[j] for j in range(i+1, n))
        x[i] = (b[i] - suma) / (A[i][i] if abs(A[i][i]) > 1e-12 else 1)
    solucion = [str(xi) for xi in x]
    return jsonify({'pasos': pasos, 'solucion': solucion, 'n': n})

if __name__ == '__main__':
    app.run(debug=True)
