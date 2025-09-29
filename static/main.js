// Genera la tabla de inputs para la matriz
document.getElementById('generate').onclick = function() {
  const n = parseInt(document.getElementById('size').value);
  const warningDiv = document.getElementById('input-warning');
  warningDiv.textContent = '';
  const matrixInput = document.getElementById('matrix-input');
  if (isNaN(n)||n<2||n>200) {
    warningDiv.textContent = 'n debe estar entre 2 y 200.';
    matrixInput.innerHTML = '';
    return;
  }
  if (n > 20) {
    warningDiv.textContent = '⚠️ Generar una matriz con n mayor a 20 puede tardar varios segundos.';
  }
  matrixInput.innerHTML = '<div style="color:#1e40af;font-weight:600;margin:12px;">Generando matriz...</div>';
  setTimeout(() => {
    const table = document.createElement('table');
    table.className = 'matrix-table';
    const tbody = document.createElement('tbody');
    for (let i = 0; i < n; i++) {
      const tr = document.createElement('tr');
      for (let j = 0; j < n; j++) {
        const td = document.createElement('td');
        const input = document.createElement('input');
        input.type = 'number';
        input.step = 'any';
        input.id = `a_${i}_${j}`;
        input.value = i === j ? 1 : 0;
        td.appendChild(input);
        tr.appendChild(td);
      }
      const tdB = document.createElement('td');
      const inputB = document.createElement('input');
      inputB.type = 'number';
      inputB.step = 'any';
      inputB.id = `b_${i}`;
      inputB.value = 0;
      tdB.appendChild(inputB);
      tr.appendChild(tdB);
      tbody.appendChild(tr);
    }
    // Header row
    const trHead = document.createElement('tr');
    for (let j = 0; j < n; j++) {
      const th = document.createElement('th');
      th.textContent = `A${j+1}`;
      trHead.appendChild(th);
    }
    const thB = document.createElement('th');
    thB.textContent = 'b';
    trHead.appendChild(thB);
    tbody.appendChild(trHead);
    table.appendChild(tbody);
    matrixInput.innerHTML = '';
    matrixInput.appendChild(table);
    matrixInput.style.overflow = 'auto';
    table.style.maxHeight = '480px';
    table.style.maxWidth = '100%';
    table.style.overflow = 'auto';
  }, 50);
}

document.getElementById('solve').onclick = async function() {
  const n = parseInt(document.getElementById('size').value);
  let A = [], b = [];
  for (let i=0; i<n; i++) {
    let fila = [];
    for (let j=0; j<n; j++) {
      let el = document.getElementById(`a_${i}_${j}`);
      if (!el) return;
      let val = parseFloat(el.value);
      if (isNaN(val)) return;
      fila.push(val);
    }
    A.push(fila);
    let bi = parseFloat(document.getElementById(`b_${i}`).value);
    if (isNaN(bi)) return;
    b.push(bi);
  }
  let stepsDiv = document.getElementById('steps');
  let solDiv = document.getElementById('solution');
  stepsDiv.innerHTML = '<div style="color:#1e40af;">Resolviendo...</div>';
  solDiv.innerHTML = '';
  try {
    const metodo = document.getElementById('method').value;
    let resp = await fetch('/api/solve', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({A, b, metodo})
    });
    let data = await resp.json();
    stepsDiv.innerHTML = '';
    (data.pasos||[]).forEach((p,i) => {
      let pasoHtml = `<div class="paso-block"><div class="paso-titulo"><b>Paso ${i+1}:</b> ${p.descripcion}</div>`;
      if (p.matriz) {
        pasoHtml += '<div class="paso-matriz"><table class="matrix-table">';
        p.matriz.forEach(fila => {
          pasoHtml += '<tr>' + fila.map(val => `<td>${val}</td>`).join('') + '</tr>';
        });
        pasoHtml += '</table></div>';
      }
      if (p.vector) {
        pasoHtml += '<div class="paso-vector">[' + p.vector.join(', ') + ']</div>';
      }
      // Iteration-style entries may use 'values' and 'errors'
      if (p.values) {
        pasoHtml += '<div class="paso-values">Valores: [' + p.values.join(', ') + ']</div>';
      }
      if (p.errors) {
        pasoHtml += '<div class="paso-errors">Errores: [' + p.errors.join(', ') + ']</div>';
      }
      if (p.max_diff) {
        pasoHtml += '<div class="paso-maxdiff">Max diff: ' + p.max_diff + '</div>';
      }
      if (p.sustitucion) {
        pasoHtml += `<div class="paso-sustitucion" style="color:#0a7b83;margin:4px 0 0 8px;">${p.sustitucion}</div>`;
      }
      if (p.formulas) {
        pasoHtml += '<div class="paso-formulas" style="margin:4px 0 0 8px;">';
        p.formulas.forEach(f=>{
          pasoHtml += `<div style="font-family:monospace;font-size:0.98em;">${f}</div>`;
        });
        pasoHtml += '</div>';
      }
      if (p.L || p.U) {
        if (p.L) {
          pasoHtml += '<div class="paso-matriz"><b>L:</b><table class="matrix-table">';
          p.L.forEach(fila => {
            pasoHtml += '<tr>' + fila.map(val => `<td>${val}</td>`).join('') + '</tr>';
          });
          pasoHtml += '</table></div>';
        }
        if (p.U) {
          pasoHtml += '<div class="paso-matriz"><b>U:</b><table class="matrix-table">';
          p.U.forEach(fila => {
            pasoHtml += '<tr>' + fila.map(val => `<td>${val}</td>`).join('') + '</tr>';
          });
          pasoHtml += '</table></div>';
        }
      }
      pasoHtml += '</div>';
      stepsDiv.innerHTML += pasoHtml;
    });
      // Si la respuesta incluye una 'tabla' (Jacobi / Gauss-Seidel), renderizarla como tabla
      const tablaPaso = (data.pasos||[]).find(p => p.tabla);
      if (tablaPaso && Array.isArray(tablaPaso.tabla)) {
        // construir tabla de iteraciones: columnas = Iter, x1..xn, Errores (por variable), MaxDiff
        const filas = tablaPaso.tabla;
        let tbl = '<b>Tabla de iteraciones:</b><br><div style="overflow:auto"><table class="matrix-table"><thead><tr><th>iter</th>';
        // intentar obtener número de variables buscando la primera fila con 'values'
        const firstValues = filas.find(r => Array.isArray(r.values));
        const varsCount = firstValues ? firstValues.values.length : data.n;
        for (let i=0;i<varsCount;i++) tbl += `<th>x${i+1}</th>`;
        // agregar columnas de errores (mostramos como columna única 'errores' y max_diff)
        tbl += '<th>errores</th><th>max_diff</th></tr></thead><tbody>';
        filas.forEach(r=>{
          // r puede venir en varias formas; normalizar
          const iter = r.iter !== undefined ? r.iter : (r.descripcion || '');
          const values = Array.isArray(r.values) ? r.values : (r.vector ? r.vector : Array(varsCount).fill(''));
          const errors = Array.isArray(r.errors) ? r.errors : [];
          const maxd = r.max_diff !== undefined ? r.max_diff : '';
          tbl += '<tr>';
          tbl += `<td>${iter}</td>`;
          for (let k=0;k<varsCount;k++) tbl += `<td>${values[k] !== undefined ? values[k] : ''}</td>`;
          tbl += `<td>${errors.length? errors.join(', ') : ''}</td>`;
          tbl += `<td>${maxd}</td>`;
          tbl += '</tr>';
        });
        tbl += '</tbody></table></div>';
        solDiv.innerHTML = tbl;
      } else {
        // comportamiento por defecto: mostrar solución vectorial (cuando exista)
        let solHtml = '<b>Solución:</b><br><table class="matrix-table"><tr>';
        for (let i=0; i<data.n; i++) solHtml += `<th>x${i+1}</th>`;
        solHtml += '</tr><tr>';
        (data.solucion||[]).forEach(v=>{solHtml+=`<td>${v}</td>`;});
        solHtml += '</tr></table>';
        solDiv.innerHTML = solHtml;
      }
  } catch(e) {
    stepsDiv.innerHTML = '<span style="color:#d32f2f;">Error de conexión</span>';
  }
}


document.getElementById('clear').onclick = function() {
  document.getElementById('matrix-input').innerHTML = '';
  document.getElementById('steps').innerHTML = '';
  document.getElementById('solution').innerHTML = '';
  document.getElementById('input-warning').textContent = '';
};
