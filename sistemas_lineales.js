// =====================
// Utilidades
// =====================
function nombresVariables(n) {
  if (n <= 4) return ['x', 'y', 'z', 'w'].slice(0, n);
  return Array.from({length: n}, (_, i) => `x${i+1}`);
}
function mostrarMatriz(matriz) {
  let html = '<table class="matrix-table">';
  matriz.forEach(fila => {
    html += '<tr>' + fila.map(x => `<td>${Math.abs(x)<1e-12?0:x.toFixed(6)}</td>`).join('') + '</tr>';
  });
  html += '</table>';
  return html;
}
function isTridiagonal(A) {
  let n = A.length;
  for (let i=0; i<n; i++) {
    for (let j=0; j<n; j++) {
      if (Math.abs(i-j)>1 && Math.abs(A[i][j])>1e-12) return false;
    }
  }
  return true;
}
// =====================
// Métodos de resolución
// =====================
function solveGauss(A, b, pivote=true) {
  let n = A.length;
  A = A.map(row => row.slice());
  b = b.slice();
  let pasos = [];
  for (let k=0; k<n-1; k++) {
    // Pivoteo parcial
    if (pivote) {
      let maxfila = k;
      for (let i=k+1; i<n; i++) if (Math.abs(A[i][k])>Math.abs(A[maxfila][k])) maxfila=i;
      let pivoteVal = A[maxfila][k];
      if (Math.abs(pivoteVal)<1e-12) pasos.push({descripcion:`Pivote ≈ 0 en fila ${maxfila+1}, posible matriz singular.`, matriz: A.map((r,i)=>r.concat([b[i]]))});
      if (maxfila!==k) {
        [A[k],A[maxfila]]=[A[maxfila],A[k]];
        [b[k],b[maxfila]]=[b[maxfila],b[k]];
        pasos.push({descripcion:`Intercambiamos R${k+1} y R${maxfila+1} porque el mayor valor absoluto en columna ${k+1} es ${pivoteVal.toFixed(6)}.`, matriz:A.map((r,i)=>r.concat([b[i]]))});
      }
    }
    let pivoteActual = A[k][k];
    if (Math.abs(pivoteActual)<1e-12) pasos.push({descripcion:`Pivote ≈ 0 en fila ${k+1}, posible matriz singular.`, matriz:A.map((r,i)=>r.concat([b[i]]))});
    for (let i=k+1; i<n; i++) {
      let factor = Math.abs(pivoteActual)>1e-12 ? A[i][k]/pivoteActual : 0.0;
      for (let j=k; j<n; j++) {
        A[i][j] -= factor*A[k][j];
        if (Math.abs(A[i][j])<1e-12) A[i][j]=0.0;
      }
      b[i] -= factor*b[k];
      if (Math.abs(b[i])<1e-12) b[i]=0.0;
      pasos.push({descripcion:`R${i+1} ← R${i+1} - ${factor.toFixed(6)}·R${k+1}`, matriz:A.map((r,idx)=>r.concat([b[idx]]))});
    }
  }
  // Sustitución hacia atrás
  let x = Array(n).fill(0);
  for (let i=n-1; i>=0; i--) {
    let suma = 0;
    for (let j=i+1; j<n; j++) suma += A[i][j]*x[j];
    x[i] = Math.abs(A[i][i])<1e-12 ? 0.0 : (b[i]-suma)/A[i][i];
  }
  return {pasos, x};
}
function solveGaussJordan(A, b, pivote=true) {
  let n = A.length;
  A = A.map(row => row.slice());
  b = b.slice();
  let pasos = [];
  for (let k=0; k<n; k++) {
    // Pivoteo parcial
    if (pivote) {
      let maxfila = k;
      for (let i=k+1; i<n; i++) if (Math.abs(A[i][k])>Math.abs(A[maxfila][k])) maxfila=i;
      let pivoteVal = A[maxfila][k];
      if (Math.abs(pivoteVal)<1e-12) pasos.push({descripcion:`Pivote ≈ 0 en fila ${maxfila+1}, posible matriz singular.`, matriz:A.map((r,i)=>r.concat([b[i]]))});
      if (maxfila!==k) {
        [A[k],A[maxfila]]=[A[maxfila],A[k]];
        [b[k],b[maxfila]]=[b[maxfila],b[k]];
        pasos.push({descripcion:`Intercambiamos R${k+1} y R${maxfila+1} porque el mayor valor absoluto en columna ${k+1} es ${pivoteVal.toFixed(6)}.`, matriz:A.map((r,i)=>r.concat([b[i]]))});
      }
    }
    let pivoteActual = A[k][k];
    if (Math.abs(pivoteActual)<1e-12) pasos.push({descripcion:`Pivote ≈ 0 en fila ${k+1}, posible matriz singular.`, matriz:A.map((r,i)=>r.concat([b[i]]))});
    // Normalizar fila pivote
    let factor = pivoteActual;
    if (Math.abs(factor)>1e-12) {
      for (let j=k; j<n; j++) {
        A[k][j] /= factor;
        if (Math.abs(A[k][j])<1e-12) A[k][j]=0.0;
      }
      b[k] /= factor;
      if (Math.abs(b[k])<1e-12) b[k]=0.0;
      pasos.push({descripcion:`R${k+1} ← R${k+1} / ${factor.toFixed(6)}`, matriz:A.map((r,i)=>r.concat([b[i]]))});
    }
    // Eliminar en otras filas
    for (let i=0; i<n; i++) {
      if (i!==k) {
        let factor2 = A[i][k];
        for (let j=k; j<n; j++) {
          A[i][j] -= factor2*A[k][j];
          if (Math.abs(A[i][j])<1e-12) A[i][j]=0.0;
        }
        b[i] -= factor2*b[k];
        if (Math.abs(b[i])<1e-12) b[i]=0.0;
        pasos.push({descripcion:`R${i+1} ← R${i+1} - ${factor2.toFixed(6)}·R${k+1}`, matriz:A.map((r,idx)=>r.concat([b[idx]]))});
      }
    }
  }
  let x = b.map(v=>v);
  return {pasos, x};
}
function luDecompose(A) {
  let n = A.length;
  let L = Array(n).fill(0).map(()=>Array(n).fill(0));
  let U = Array(n).fill(0).map(()=>Array(n).fill(0));
  for (let i=0; i<n; i++) {
    for (let j=0; j<n; j++) {
      if (j<i) {
        let suma = 0;
        for (let k=0; k<j; k++) suma += L[i][k]*U[k][j];
        if (Math.abs(U[j][j])<1e-12) throw Error(`Matriz singular, pivote ≈ 0 en fila ${j+1}.`);
        L[i][j] = (A[i][j]-suma)/U[j][j];
      } else {
        let suma = 0;
        for (let k=0; k<i; k++) suma += L[i][k]*U[k][j];
        U[i][j] = A[i][j]-suma;
      }
    }
    L[i][i]=1.0;
  }
  return {L,U};
}
function solveLU(L,U,b) {
  let n = L.length;
  let y = Array(n).fill(0);
  for (let i=0; i<n; i++) {
    let suma = 0;
    for (let j=0; j<i; j++) suma += L[i][j]*y[j];
    y[i] = (b[i]-suma)/L[i][i];
  }
  let x = Array(n).fill(0);
  for (let i=n-1; i>=0; i--) {
    let suma = 0;
    for (let j=i+1; j<n; j++) suma += U[i][j]*x[j];
    x[i] = Math.abs(U[i][i])<1e-12 ? 0.0 : (y[i]-suma)/U[i][i];
  }
  return x;
}
function solveThomas(a,b,c,d) {
  let n = b.length;
  let ac = a.slice(), bc = b.slice(), cc = c.slice(), dc = d.slice();
  let pasos = [];
  for (let i=1; i<n; i++) {
    let m = Math.abs(bc[i-1])>1e-12 ? ac[i-1]/bc[i-1] : 0.0;
    bc[i] -= m*cc[i-1];
    dc[i] -= m*dc[i-1];
    pasos.push({descripcion:`Fila ${i+1}: b[${i}] ← b[${i}] - ${m.toFixed(6)}·c[${i-1}]`, matriz:null, b:bc.slice(), d:dc.slice()});
  }
  let x = Array(n).fill(0);
  x[n-1] = Math.abs(bc[n-1])>1e-12 ? dc[n-1]/bc[n-1] : 0.0;
  for (let i=n-2; i>=0; i--) {
    x[i] = Math.abs(bc[i])>1e-12 ? (dc[i]-cc[i]*x[i+1])/bc[i] : 0.0;
  }
  return {pasos,x};
}
// =====================
// Interfaz y lógica principal
// =====================
document.getElementById('generate').onclick = function() {
  let n = parseInt(document.getElementById('size').value);
  if (isNaN(n)||n<2||n>10) return;
  let html = '<table class="matrix-table">';
  for (let i=0; i<n; i++) {
    html += '<tr>';
    for (let j=0; j<n; j++) {
      html += `<td><input type="number" step="any" id="a_${i}_${j}" value="${i===j?1:0}"></td>`;
    }
    html += `<td><input type="number" step="any" id="b_${i}" value="0"></td>`;
    html += '</tr>';
  }
  html += '<tr>';
  for (let j=0; j<n; j++) html += `<th>A${j+1}</th>`;
  html += '<th>b</th></tr>';
  html += '</table>';
  document.getElementById('matrix-input').innerHTML = html;
};
document.getElementById('solve').onclick = function() {
  let n = parseInt(document.getElementById('size').value);
  let A = [], b = [];
  let errorDiv = document.getElementById('error');
  errorDiv.textContent = '';
  for (let i=0; i<n; i++) {
    let fila = [];
    for (let j=0; j<n; j++) {
      let val = parseFloat(document.getElementById(`a_${i}_${j}`).value);
      if (isNaN(val)) {
        errorDiv.textContent = 'Todos los coeficientes deben ser números.';
        return;
      }
      fila.push(val);
    }
    A.push(fila);
    let bi = parseFloat(document.getElementById(`b_${i}`).value);
    if (isNaN(bi)) {
      errorDiv.textContent = 'Todos los valores de b deben ser números.';
      return;
    }
    b.push(bi);
  }
  let method = document.getElementById('method').value;
  let pasos = [], x = [];
  try {
    if (method==='gauss') {
      let res = solveGauss(A,b,true);
      pasos = res.pasos; x = res.x;
    } else if (method==='gauss-jordan') {
      let res = solveGaussJordan(A,b,true);
      pasos = res.pasos; x = res.x;
    } else if (method==='lu') {
      let {L,U} = luDecompose(A);
      x = solveLU(L,U,b);
      pasos = [{descripcion:'Factorización LU completada.', matriz:null},{descripcion:'Sustitución hacia adelante y atrás.', matriz:null}];
    } else if (method==='thomas') {
      if (!isTridiagonal(A)) {
        errorDiv.textContent = 'Error: la matriz no es tridiagonal.';
        return;
      }
      let a = Array(n-1).fill(0).map((_,i)=>A[i+1][i]);
      let b_diag = Array(n).fill(0).map((_,i)=>A[i][i]);
      let c = Array(n-1).fill(0).map((_,i)=>A[i][i+1]);
      let res = solveThomas(a,b_diag,c,b);
      pasos = res.pasos; x = res.x;
    }
  } catch(e) {
    errorDiv.textContent = 'Error: '+e.message;
    return;
  }
  // Mostrar pasos
  let stepsDiv = document.getElementById('steps');
  stepsDiv.innerHTML = '';
  pasos.forEach((p,i) => {
    let pasoHtml = `<div><b>Paso ${i+1}:</b> ${p.descripcion}`;
    if (p.matriz) pasoHtml += mostrarMatriz(p.matriz);
    if (p.b && p.d) pasoHtml += `<br>b: [${p.b.map(x=>x.toFixed(6)).join(', ')}], d: [${p.d.map(x=>x.toFixed(6)).join(', ')}]`;
    pasoHtml += '</div><hr>';
    stepsDiv.innerHTML += pasoHtml;
  });
  // Mostrar solución
  let solDiv = document.getElementById('solution');
  let vars = nombresVariables(n);
  let solHtml = '<table class="matrix-table"><tr>';
  vars.forEach(v=>{solHtml+=`<th>${v}</th>`;});
  solHtml+='</tr><tr>';
  x.forEach(v=>{solHtml+=`<td>${Math.abs(v)<1e-12?0:v.toFixed(6)}</td>`;});
  solHtml+='</tr></table>';
  solDiv.innerHTML = '<b>Solución:</b><br>'+solHtml;
  // Exportar pasos
  let exportBtn = document.getElementById('export');
  exportBtn.style.display = pasos.length>0?'inline-block':'none';
  exportBtn.onclick = function() {
    let texto = pasos.map((p,i)=>`Paso ${i+1}: ${p.descripcion}${p.matriz?`\n${p.matriz.map(f=>f.join(' ')).join('\n')}`:''}`).join('\n\n');
    let blob = new Blob([texto],{type:'text/plain'});
    let url = URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    a.download = 'pasos_sistema.txt';
    a.click();
    URL.revokeObjectURL(url);
  };
};
document.getElementById('clear').onclick = function() {
  document.getElementById('matrix-input').innerHTML = '';
  document.getElementById('steps').innerHTML = '';
  document.getElementById('solution').innerHTML = '';
  document.getElementById('error').textContent = '';
  document.getElementById('export').style.display = 'none';
};
