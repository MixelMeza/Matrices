// Convierte un número decimal a fracción (máximo denominador 1000)
function decimalAFraccion(x) {
  if (Math.abs(x) < 1e-12) return '0';
  if (Number.isInteger(x)) return x.toString();
  let signo = x < 0 ? '-' : '';
  x = Math.abs(x);
  let denominador = 1;
  while (Math.abs(x * denominador - Math.round(x * denominador)) > 1e-8 && denominador < 1000) {
    denominador++;
  }
  let numerador = Math.round(x * denominador);
  // Simplificar
  function gcd(a, b) { return b ? gcd(b, a % b) : a; }
  let g = gcd(numerador, denominador);
  numerador /= g;
  denominador /= g;
  return `${signo}${numerador}/${denominador}`;
}
// =====================
// Interfaz y lógica principal con API REST
// =====================
function nombresVariables(n) {
  if (n <= 4) return ['x', 'y', 'z', 'w'].slice(0, n);
  return Array.from({length: n}, (_, i) => `x${i+1}`);
}
function mostrarMatriz(matriz) {
  let html = '<table class="matrix-table">';
  matriz.forEach(fila => {
    html += '<tr>' + fila.map(x => `<td>${x ?? ''}</td>`).join('') + '</tr>';
  });
  html += '</table>';
  return html;
}

function formateaNumero(x, modo='normal') {
  if (modo==='fraccion') {
    if (typeof x === 'string') return x;
    return decimalAFraccion(x);
  }
  if (typeof x === 'string') return x;
  if (Math.abs(x) < 1e-12) return '0';
  if (Number.isInteger(x)) return x.toString();
  let str = x.toFixed(6);
  // Elimina ceros innecesarios
  str = str.replace(/\.0+$/, '');
  str = str.replace(/(\.[0-9]*[1-9])0+$/, '$1');
  return str;
}
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
document.getElementById('solve').onclick = async function() {
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
  let pivoteo = (method==='gauss'||method==='gauss-jordan') ? true : undefined;
  let payload = {A, b, metodo: method, pivoteo};
  try {
    let resp = await fetch('http://localhost:5000/api/solve', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    let data = await resp.json();
    if (!resp.ok) {
      errorDiv.textContent = data.error || 'Error desconocido.';
      return;
    }
    // Mostrar pasos
    let stepsDiv = document.getElementById('steps');
    stepsDiv.innerHTML = '';
    (data.pasos||[]).forEach((p,i) => {
      let pasoHtml = `<div><b>Paso ${i+1}:</b> ${p.descripcion}`;
      if (p.matriz_aumentada) pasoHtml += mostrarMatriz(p.matriz_aumentada);
      // Si hay vector b, mostrarlo en fracciones
      if (p.b) pasoHtml += `<br><b>b:</b> [${p.b.map(x=>formateaNumero(x,'fraccion')).join(', ')}]`;
      pasoHtml += '</div><hr>';
      stepsDiv.innerHTML += pasoHtml;
    });
    // Mostrar solución
    let solDiv = document.getElementById('solution');
    let vars = nombresVariables(data.n||n);
    let solHtml = '<table class="matrix-table"><tr>';
  vars.forEach(v=>{solHtml+=`<th>${v}</th>`;});
  solHtml+='</tr><tr>';
  (data.solucion?.vector||[]).forEach(v=>{solHtml+=`<td>${formateaNumero(v,'fraccion')}</td>`;});
  solHtml+='</tr></table>';
  solDiv.innerHTML = '<b>Solución:</b><br>'+solHtml;
    // Exportar pasos
    let exportBtn = document.getElementById('export');
    exportBtn.style.display = (data.pasos?.length>0)?'inline-block':'none';
    exportBtn.onclick = function() {
      let texto = (data.pasos||[]).map((p,i)=>`Paso ${i+1}: ${p.descripcion}${p.matriz_aumentada?`\n${p.matriz_aumentada.map(f=>f.join(' ')).join('\n')}`:''}`).join('\n\n');
      let blob = new Blob([texto],{type:'text/plain'});
      let url = URL.createObjectURL(blob);
      let a = document.createElement('a');
      a.href = url;
      a.download = 'pasos_sistema.txt';
      a.click();
      URL.revokeObjectURL(url);
    };
  } catch(e) {
    errorDiv.textContent = 'Error de conexión con el servidor.';
  }
};
document.getElementById('clear').onclick = function() {
  document.getElementById('matrix-input').innerHTML = '';
  document.getElementById('steps').innerHTML = '';
  document.getElementById('solution').innerHTML = '';
  document.getElementById('error').textContent = '';
  document.getElementById('export').style.display = 'none';
};
