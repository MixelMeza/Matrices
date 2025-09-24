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
    let resp = await fetch('/api/solve', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({A, b})
    });
    let data = await resp.json();
    stepsDiv.innerHTML = '';
    (data.pasos||[]).forEach((p,i) => {
      let pasoHtml = `<div><b>Paso ${i+1}:</b> ${p.descripcion}`;
      if (p.matriz) pasoHtml += '<br>' + p.matriz.map(fila => fila.join(' | ')).join('<br>');
      pasoHtml += '</div><hr>';
      stepsDiv.innerHTML += pasoHtml;
    });
    let solHtml = '<b>Solución:</b><br><table class="matrix-table"><tr>';
    for (let i=0; i<data.n; i++) solHtml += `<th>x${i+1}</th>`;
    solHtml += '</tr><tr>';
    (data.solucion||[]).forEach(v=>{solHtml+=`<td>${v}</td>`;});
    solHtml += '</tr></table>';
    solDiv.innerHTML = solHtml;
  } catch(e) {
    stepsDiv.innerHTML = '<span style="color:#d32f2f;">Error de conexión</span>';
  }
}

document.getElementById('clear').onclick = function() {
  document.getElementById('matrix-input').innerHTML = '';
  document.getElementById('steps').innerHTML = '';
  document.getElementById('solution').innerHTML = '';
  document.getElementById('input-warning').textContent = '';
}
