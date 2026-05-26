// AriOne Product Engine (v1.2) - Master Orchestrator
// ══════════════════════════════════════════════════════════════════════════════

// 🛡️ PROTEÇÃO DE INICIALIZAÇÃO MASTER
window.selectedCoresGrade = window.selectedCoresGrade || [];
window.selectedAtributosGrade = window.selectedAtributosGrade || [];
window.existingData = window.existingData || {};
window.composicaoData = window.composicaoData || {};

/**
 * 🚀 INICIALIZADOR GLOBAL DE UI (ANTI-TRAVAMENTO)
 */
document.addEventListener('click', (e) => {
    const tabBtn = e.target.closest('.fp-tab');
    if (tabBtn) {
        const tabId = tabBtn.dataset.tab;
        if (!tabId) return;
        document.querySelectorAll('.fp-tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.fp-tab-panel').forEach(p => p.classList.remove('active'));
        tabBtn.classList.add('active');
        const panel = document.getElementById('tab-' + tabId);
        if (panel) panel.classList.add('active');
        if (typeof window.positionExpandBadge === 'function') window.positionExpandBadge(tabBtn);
    }
    const expandBtn = e.target.closest('#badge-expandir');
    if (expandBtn) window.toggleIdentificacao(true);
});

// ════ FUNÇÕES DE RENDERIZAÇÃO DE INTERFACE (CHIPS) ════

window.renderCoresChips = function() {
    const wrap = document.getElementById('lista-cores-selecionadas');
    if (!wrap) return;
    const cores = window.selectedCoresGrade || [];
    wrap.innerHTML = cores.map((c, i) => `
        <div class="fp-selection-item active chip-cor" style="border-left: 3px solid ${c.hex || '#CBD5E0'};">
            <span>${c.nome}</span>
            <i class="fas fa-times" onclick="window.removerCorGrade(${i})"></i>
        </div>
    `).join('');
    window.updateGradeSummary();
    window.forceRenderMatrix();
};

window.renderAtributosChips = function() {
    const wrap = document.getElementById('lista-atributos-selecionados');
    if (!wrap) return;
    const attrs = window.selectedAtributosGrade || [];
    wrap.innerHTML = attrs.map((a, i) => `
        <div class="fp-selection-item active chip-atributo" style="border-left: 3px solid #F39C12;">
            <span>${a.nome}</span>
            <i class="fas fa-times" onclick="window.removerAtributoGrade(${i})"></i>
        </div>
    `).join('');
    window.updateGradeSummary();
    window.forceRenderMatrix();
};

window.removerCorGrade = function(index) {
    if (window.selectedCoresGrade) {
        window.selectedCoresGrade.splice(index, 1);
        window.renderCoresChips();
    }
};

window.removerAtributoGrade = function(index) {
    if (window.selectedAtributosGrade) {
        window.selectedAtributosGrade.splice(index, 1);
        window.renderAtributosChips();
    }
};

window.adicionarCorGradePorSelecao = function() {
    const sel = document.getElementById('sel-cores-catalogo');
    if(!sel || !sel.value) return;
    const nome = sel.value, hex = sel.options[sel.selectedIndex].dataset.hex;
    if(window.selectedCoresGrade.find(c => c.nome === nome)) return;
    window.selectedCoresGrade.push({ nome, hex });
    window.renderCoresChips();
    sel.value = '';
};

window.adicionarAtributoGrade = function() {
    const sel = document.getElementById('sel-atributo-catalogo');
    if(!sel || !sel.value) return;
    const nome = sel.value;
    if(window.selectedAtributosGrade.find(a => a.nome === nome)) return;
    window.selectedAtributosGrade.push({ nome });
    window.renderAtributosChips();
    sel.value = '';
};

window.alternarGrade = function(tipo) {
    const bUnico = document.getElementById('bloco-unico'), bGrade = document.getElementById('bloco-grade');
    if (tipo === 'grade') {
        if(bUnico) bUnico.style.display = 'none';
        if(bGrade) bGrade.style.display = 'block';
        window.forceRenderMatrix();
    } else {
        if(bUnico) bUnico.style.display = 'block';
        if(bGrade) bGrade.style.display = 'none';
    }
};

window.getSigla = function(str, len) {
    if(!str) return "";
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-zA-Z0-9]/g, "").substring(0, len).toUpperCase();
};

window.gerarSKU = function(c, t, a) {
    const skuPai = document.getElementsByName('referencia')[0]?.value || 'REF';
    const cor = window.getSigla(c, 3), tam = t.replace(/\s+/g, '').toUpperCase();
    return `${skuPai}.${cor}.${tam}`;
};

window.forceRenderMatrix = function(force = false) {
    const wrap = document.getElementById('matrix-body');
    if (!wrap) return;

    const cores = window.selectedCoresGrade || [], attrs = window.selectedAtributosGrade || [];
    const tams = Array.from(document.querySelectorAll('[name="grade_tamanhos"]:checked')).map(t => t.value);

    if (cores.length === 0 || tams.length === 0) {
        wrap.innerHTML = '<tr><td colspan="5" style="padding:40px; text-align:center; color:#94a3b8;"><i class="fas fa-info-circle"></i> SELECIONE AO MENOS UMA COR E UM TAMANHO PARA VER A GRADE.</td></tr>';
        return;
    }

    let html = '';
    cores.forEach(c => {
        tams.forEach(t => {
            if (attrs.length > 0) {
                attrs.forEach(a => { html += window.renderRow(c.nome, t, a.nome, force); });
            } else {
                html += window.renderRow(c.nome, t, null, force);
            }
        });
    });
    wrap.innerHTML = html;
    window.collectMatrixData();
};

window.renderRow = function(c, t, a, force = false) {
    const key = `${c}|${t}|${a || ''}`, val = (window.existingData && window.existingData[key]) ? window.existingData[key] : {};
    const skuAuto = (force || !val.sku) ? window.gerarSKU(c, t, a) : val.sku;
    const nomePai = document.getElementById('campo-descricao')?.value || '';
    const isOverride = val.is_override === true || val.is_override === 'true';
    const precoBase = document.getElementById('preco_varejo')?.value || '0,00';
    const precoFinal = isOverride ? (val.preco || precoBase) : precoBase;
    const lockIcon = isOverride ? '<i class="fas fa-lock" style="color:#e53e3e;"></i>' : '<i class="fas fa-lock-open" style="color:#27AE60; opacity:0.5;"></i>';
    const labelVariacao = a ? `<strong>${c}</strong> / ${t} (${a})` : `<strong>${c}</strong> / ${t}`;
    const displayLabel = `${c} / ${t}${a ? ' / '+a : ''}`, safeLabel = displayLabel.replace(/'/g, "\\'").replace(/"/g, "&quot;");

    return `<tr class="matrix-row" data-key="${key}" onclick="window.ativarModoEngenharia('${key}', '${safeLabel}')" style="cursor:pointer;">
      <td><input class="fp-input sku-input" name="mat_sku_${key}" type="text" value="${skuAuto}" style="width:100%; height:26px; font-size:10px; font-weight:400; font-family:'Roboto Mono',monospace;" onclick="event.stopPropagation()"></td>
      <td style="font-size:10px; color:#1e293b;">${nomePai} — ${labelVariacao}</td>
      <td><input class="fp-input" name="mat_estoque_${key}" type="number" value="${val.estoque || ''}" style="width:100%; text-align:center; height:26px; font-size:10px;" onclick="event.stopPropagation()"></td>
      <td style="position:relative; display:flex; align-items:center; gap:5px;" onclick="event.stopPropagation()">
        <label style="cursor:pointer;"><input type="checkbox" name="mat_override_${key}" class="mat-override-check" ${isOverride ? 'checked' : ''} onchange="window.togglePriceOverride(this, '${key}')" style="display:none;"><span class="lock-status">${lockIcon}</span></label>
        <input class="fp-input fp-mask-money mat-preco-input" name="mat_preco_${key}" type="text" value="${precoFinal}" ${!isOverride ? 'readonly style="background:#f8fafc; border:none;"' : ''} style="width:100%; text-align:right; height:26px; font-size:10px;">
      </td>
      <td style="text-align:center; color:var(--pri); font-size:14px;"><i class="fas fa-tools"></i></td>
    </tr>`;
};

window.togglePriceOverride = function(cb, key) {
    const row = cb.closest('tr'), input = row.querySelector('.mat-preco-input'), lockSpan = row.querySelector('.lock-status'), precoBase = document.getElementById('preco_varejo')?.value || '0,00';
    if (cb.checked) {
        input.removeAttribute('readonly'); input.style.background = '#fff'; input.style.border = '1px solid #27AE60'; lockSpan.innerHTML = '<i class="fas fa-lock" style="color:#e53e3e;"></i>';
    } else {
        input.setAttribute('readonly', true); input.style.background = '#f8fafc'; input.style.border = 'none'; input.value = precoBase; lockSpan.innerHTML = '<i class="fas fa-lock-open" style="color:#27AE60; opacity:0.5;"></i>';
    }
    window.collectMatrixData();
};

window.ativarModoEngenharia = function(key, label) {
    const tabComp = document.querySelector('.fp-tab[data-tab="composicao"]');
    if (tabComp && tabComp.style.display !== 'none') {
        tabComp.click();
        if (typeof window.switchComposicaoSize === 'function') window.switchComposicaoSize(label);
    } else if (typeof arioneToast === 'function') {
        arioneToast("Habilite 'Possui Composição' para editar a engenharia.", "info");
    }
};

window.toggleComposicaoTab = function(visible) {
    const btn = document.getElementById('btn-tab-composicao'), wrapMov = document.getElementById('wrap-mov-composicao');
    if (btn) btn.style.display = visible ? 'flex' : 'none';
    if (wrapMov) wrapMov.style.display = visible ? 'flex' : 'none';
};

window.updateGradeSummary = function() {
    const cores = window.selectedCoresGrade ? window.selectedCoresGrade.length : 0, tams = document.querySelectorAll('[name="grade_tamanhos"]:checked').length, attrs = window.selectedAtributosGrade ? window.selectedAtributosGrade.length : 0;
    const badge = document.getElementById('badge-estoque'); if (badge) badge.innerText = (cores > 0 || tams > 0) ? `${cores}C / ${tams}T` : '';
    const total = cores * tams * (attrs || 1), vBadge = document.getElementById('badge-variacoes');
    if (vBadge) vBadge.innerHTML = `<i class="fas fa-calculator"></i> ${total} Variações`;
};

window.collectMatrixData = function() {
    const data = {}; let totalEstoque = 0;
    document.querySelectorAll('.matrix-row').forEach(row => {
        const key = row.dataset.key, sku = row.querySelector('.sku-input').value, est = parseFloat(row.querySelector('input[name^="mat_estoque_"]').value) || 0, preco = row.querySelector('.mat-preco-input').value, override = row.querySelector('.mat-override-check').checked;
        totalEstoque += est;
        data[key] = { sku, estoque: est, preco, is_override: override };
    });
    const hidden = document.getElementById('matrix_json_hidden'); if(hidden) hidden.value = JSON.stringify(data);
    const paiEstoque = document.getElementsByName('estoque_atual')[0];
    if (paiEstoque && document.querySelector('[name="tipo_estoque"]:checked')?.value === 'grade') {
        paiEstoque.value = totalEstoque.toFixed(2).replace('.', ',');
        paiEstoque.setAttribute('readonly', true);
    }
};

window.validarTrocaTamanho = function() { window.updateGradeSummary(); window.forceRenderMatrix(); };
window.carregarGradeModelo = function(id) {
    fetch(`/cadastros/catalogos/grades/${id}/json`).then(r => r.json()).then(data => {
        const container = document.getElementById('chips-tamanhos');
        data.itens.forEach(item => {
            const val = item.toUpperCase();
            let existing = container.querySelector(`input[value="${val}"]`);
            if (existing) { existing.checked = true; } 
            else {
                const label = document.createElement('label'); label.className = 'fp-chip-master';
                label.innerHTML = `<input type="checkbox" name="grade_tamanhos" value="${val}" onchange="window.validarTrocaTamanho(this)" checked style="display:none;"><span class="chip-content" style="padding:4px 10px; border-radius:6px; border:1px solid #7A255F; color:#7A255F; font-size:10px; font-weight:800;">${item}</span>`;
                container.appendChild(label);
            }
        });
        window.updateGradeSummary(); window.forceRenderMatrix();
    });
};

window.switchComposicaoSize = function(size) { 
    window.currentSizeComp = size;
    const label = document.getElementById('comp-label-selecionado');
    if (label) label.innerHTML = `<i class="fas fa-check-circle" style="color:#27AE60;"></i> Selecionado: <span style="color:var(--pri); font-weight:700;">${size}</span>`;
    const acoes = document.getElementById('acoes-composicao');
    if (acoes) { acoes.style.opacity = '1'; acoes.style.pointerEvents = 'auto'; acoes.style.filter = 'none'; }
    window.renderComposicaoTable();
};

window.renderComposicaoTable = function() {
    const wrap = document.getElementById('tabela-composicao-corpo'); if (!wrap) return;
    const data = (window.composicaoData && window.composicaoData[window.currentSizeComp]) || [];
    if (data.length === 0) { wrap.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px;">Nenhum item.</td></tr>'; return; }
    wrap.innerHTML = data.map((item, i) => `<tr><td style="font-weight:700; color:var(--pri); font-size:11px;">${item.tipo.toUpperCase()}</td><td>${item.nome}</td><td style="text-align:center;">${item.qtd} ${item.unidade}</td><td style="text-align:right;">R$ ${item.custo}</td><td style="text-align:center;"><button type="button" onclick="window.removerItemComposicao(${i})" style="color:#e53e3e; background:none; border:none; cursor:pointer;"><i class="fas fa-trash"></i></button></td></tr>`).join('');
};
