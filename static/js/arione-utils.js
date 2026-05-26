// =============================================================================
// Arquivo  : static/js/arione-utils.js
// Função   : Utilitários globais do AriOne (máscaras, CEP, toggle PF/PJ)
// Descrição: Funções reutilizáveis para formulários em todo o sistema
// =============================================================================

console.log('✅ AriOne Utils carregado');

// =============================================================================
// 🛡️ AriOne TOAST — Notificação não-intrusiva (Quiet Luxury)
// =============================================================================

window.arioneToast = function(mensagem, tipo = 'info', duracao = 3000) {
    // Busca o container no documento atual ou no parent (se estiver em iFrame)
    let container = document.getElementById('arione-toast-container');
    if (!container && window.parent && window.parent.document) {
        container = window.parent.document.getElementById('arione-toast-container');
    }

    const targetDoc = container ? container.ownerDocument : document;

    if (!container) {
        container = targetDoc.createElement('div');
        container.id = 'arione-toast-container';
        container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 999999 !important; display: flex; flex-direction: column-reverse; gap: 10px; pointer-events: none;';
        targetDoc.body.appendChild(container);
    }

    const toast = targetDoc.createElement('div');
    const cores = {
        'success': '#10B981',
        'danger':  '#EF4444',
        'warning': '#F59E0B',
        'info':    '#3B82F6'
    };
    
    const icon = {
        'success': 'fa-check-circle',
        'danger':  'fa-times-circle',
        'warning': 'fa-exclamation-triangle',
        'info':    'fa-info-circle'
    };

    toast.className = 'arione-toast-item';
    toast.style.cssText = `
        background: #fff;
        color: #1e293b;
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border-left: 5px solid ${cores[tipo] || cores.info};
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 250px;
        transform: translateX(100px);
        opacity: 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        pointer-events: auto;
    `;

    toast.innerHTML = `<i class="fas ${icon[tipo] || icon.info}" style="color: ${cores[tipo] || cores.info}; font-size: 16px;"></i> <span>${mensagem}</span>`;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    });

    setTimeout(() => {
        toast.style.transform = 'translateX(100px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }, duracao);
};

window.arioneConfirm = function(mensagem, btnContexto) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 999999 !important; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(3px); animation: feFadeIn 0.2s ease;';
        
        modal.innerHTML = `
            <div style="background: #fff; border-radius: 16px; width: 90%; max-width: 400px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.25);">
                <div style="background: var(--pri, #7A255F); padding: 15px 20px; color: #fff; font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-shield-alt"></i> AriOne: Confirmação
                </div>
                <div style="padding: 24px; font-size: 14px; color: #1e293b; line-height: 1.5;">
                    ${mensagem}
                </div>
                <div style="padding: 15px 20px; background: #f8fafc; display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #f1f5f9;">
                    <button id="arione-confirm-no" style="background: none; border: 1.5px solid #cbd5e1; color: #64748b; padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 12px; cursor: pointer;">CANCELAR</button>
                    <button id="arione-confirm-yes" style="background: var(--pri, #7A255F); border: none; color: #fff; padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 12px; cursor: pointer;">CONFIRMAR</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('#arione-confirm-no').onclick = function() {
            modal.remove();
            resolve(false);
        };

        modal.querySelector('#arione-confirm-yes').onclick = function() {
            modal.remove();
            resolve(true);
        };
    });
};

window.arionePrompt = function(mensagem, valorPadrao = '') {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 999999 !important; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(3px); animation: feFadeIn 0.2s ease;';
        
        modal.innerHTML = `
            <div style="background: #fff; border-radius: 16px; width: 90%; max-width: 420px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.25); font-family: 'Outfit', sans-serif;">
                <div style="background: var(--pri, #7A255F); padding: 16px 22px; color: #fff; font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-question-circle"></i> AriOne: Entrada de Dados
                </div>
                <div style="padding: 24px; font-size: 14px; color: #1e293b; line-height: 1.5;">
                    <label style="display:block; font-weight:700; color:#334155; margin-bottom:10px;">${mensagem}</label>
                    <input type="text" id="arione-prompt-input" value="${valorPadrao}" style="width: 100%; border: 2px solid #cbd5e1; border-radius: 8px; padding: 12px 16px; font-size: 14px; font-weight: 600; color: #1e293b; outline: none; transition: border 0.2s;" onfocus="this.style.borderColor='var(--pri, #7A255F)'" onblur="this.style.borderColor='#cbd5e1'">
                </div>
                <div style="padding: 16px 22px; background: #f8fafc; display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #f1f5f9;">
                    <button id="arione-prompt-no" style="background: none; border: 1.5px solid #cbd5e1; color: #64748b; padding: 10px 20px; border-radius: 8px; font-weight: 700; font-size: 12px; cursor: pointer;">CANCELAR</button>
                    <button id="arione-prompt-yes" style="background: var(--pri, #7A255F); border: none; color: #fff; padding: 10px 20px; border-radius: 8px; font-weight: 700; font-size: 12px; cursor: pointer; box-shadow: 0 4px 12px rgba(122,37,95,0.2);">CONFIRMAR</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const input = modal.querySelector('#arione-prompt-input');
        setTimeout(() => input.focus(), 100);

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                modal.remove();
                resolve(input.value);
            } else if (e.key === 'Escape') {
                modal.remove();
                resolve(null);
            }
        });

        modal.querySelector('#arione-prompt-no').onclick = function() {
            modal.remove();
            resolve(null);
        };

        modal.querySelector('#arione-prompt-yes').onclick = function() {
            modal.remove();
            resolve(input.value);
        };
    });
};

/**
 * 🛡️ AriOne ALERT — Modal Informativo (Padrão Ouro)
 */
window.arioneAlert = function(titulo, mensagem, tipo = 'info') {
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 999999 !important; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(3px); animation: feFadeIn 0.2s ease;';
    
    const cores = {
        'info': '#3B82F6',
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444'
    };

    const icons = {
        'info': 'fa-info-circle',
        'success': 'fa-check-circle',
        'warning': 'fa-exclamation-triangle',
        'danger': 'fa-times-circle'
    };

    modal.innerHTML = `
        <div style="background: #fff; border-radius: 16px; width: 90%; max-width: 450px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.25);">
            <div style="background: ${cores[tipo] || cores.info}; padding: 15px 20px; color: #fff; font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 10px;">
                <i class="fas ${icons[tipo] || icons.info}"></i> ${titulo}
            </div>
            <div style="padding: 24px; font-size: 14px; color: #1e293b; line-height: 1.6; font-family: 'Outfit', sans-serif;">
                ${mensagem}
            </div>
            <div style="padding: 15px 20px; background: #f8fafc; display: flex; justify-content: flex-end; border-top: 1px solid #f1f5f9;">
                <button id="arione-alert-ok" style="background: ${cores[tipo] || cores.info}; border: none; color: #fff; padding: 10px 24px; border-radius: 8px; font-weight: 700; font-size: 12px; cursor: pointer; box-shadow: 0 4px 10px ${cores[tipo]}44;">ENTENDI</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.querySelector('#arione-alert-ok').onclick = function() { modal.remove(); };
};

// =============================================================================
// GERENCIAMENTO GLOBAL DE MODAL EMPRESA (PARIDADE TOTAL PAAv1)
// =============================================================================
window.abrirModalEmp = async function(tipo, id = null) {
    console.log("🛡️ AriOne Global: abrirModalEmp acionado para", tipo, id);
    const endpointsEmp = {
        socios:       '/cadastros/socios/form?modal=1',
        investidores: '/cadastros/investidores/form?modal=1',
        setores:      '/gestao/cards/setores?modal=1',
        departamentos: '/gestao/cards/departamentos?modal=1',
        cargos:        '/gestao/cards/cargos?modal=1',
        relatorios:    '/cadastros/cards/empresa/relatorios'
    };
    let url = endpointsEmp[tipo];
    if (!url) return;

    if (id) {
        if (url.includes('/form')) {
            url = url.split('/form')[0] + '/form/' + id + '?modal=1';
        } else {
            url += (url.includes('?') ? '&' : '?') + 'id=' + id;
        }
    }

    // Verifica se existe o modal overlay no documento atual ou no parent
    let overlay = document.getElementById('modal-overlay-emp');
    let targetDoc = document;
    if (!overlay && window.parent && window.parent.document) {
        overlay = window.parent.document.getElementById('modal-overlay-emp');
        if (overlay) targetDoc = window.parent.document;
    }

    if (overlay) {
        try {
            const response = await fetch(url);
            const html = await response.text();
            const body = targetDoc.getElementById('modal-body-emp');
            if (body) {
                body.innerHTML = html;
                body.querySelectorAll('script').forEach(script => {
                    const novo = targetDoc.createElement('script');
                    [...script.attributes].forEach(attr => novo.setAttribute(attr.name, attr.value));
                    novo.appendChild(targetDoc.createTextNode(script.innerHTML));
                    script.parentNode.replaceChild(novo, script);
                });
                overlay.classList.add('ativo');
                targetDoc.body.style.overflow = 'hidden';
                return;
            }
        } catch (e) {
            console.error("Erro ao carregar modal empresa via AJAX:", e);
        }
    }

    // Fallback inteligente se estiver em página standalone
    console.warn("⚠️ AriOne: Modal overlay não encontrado. Redirecionando para página standalone.");
    const cleanUrl = url.split('?')[0] + (id ? (url.includes('/form/') ? '' : '?id=' + id) : '');
    window.location.href = cleanUrl;
};

window.fecharModalEmp = function() {
    let overlay = document.getElementById('modal-overlay-emp');
    let targetDoc = document;
    if (!overlay && window.parent && window.parent.document) {
        overlay = window.parent.document.getElementById('modal-overlay-emp');
        if (overlay) targetDoc = window.parent.document;
    }
    if (overlay) {
        overlay.classList.remove('ativo');
        targetDoc.body.style.overflow = '';
    }
};



// =============================================================================
// MODAIS GLOBAIS
// =============================================================================

window.fecharModalGlobal = function() {
    console.log("🛡️ AriOne: Disparando fechamento global...");
    
    // 1. Tenta encontrar o modal no documento atual
    var modal = document.getElementById('arione-modal-global');
    if (modal && modal.style.display !== 'none') {
        modal.style.display = 'none';
        var content = document.getElementById('arione-modal-content');
        if (content) content.innerHTML = '';
        return;
    }

    // 2. Tenta encontrar e fechar no parent ou top (recursivo)
    try {
        var win = window;
        while (win !== win.parent) {
            win = win.parent;
            var pModal = win.document.getElementById('arione-modal-global');
            if (pModal && pModal.style.display !== 'none') {
                pModal.style.display = 'none';
                var pContent = win.document.getElementById('arione-modal-content');
                if (pContent) pContent.innerHTML = '';
                return;
            }
        }
    } catch (e) {
        console.warn("⚠️ AriOne: Erro ao acessar parent window (CORS?).");
    }

    // 3. Fallback: Se não encontrou modal aberto, volta a página ou fecha aba
    if (window.opener) {
        window.close();
    } else {
        window.history.back();
    }
};

window.abrirModalGlobal = function(url, titulo) {
    const modal = document.getElementById('arione-modal-global');
    const content = document.getElementById('arione-modal-content');
    const titleEl = document.getElementById('arione-modal-title');

    if (modal && content) {
        if (titleEl) titleEl.innerText = titulo || 'AriOne Operational';
        modal.style.display = 'flex';
        content.innerHTML = '<div style="flex:1; display:flex; align-items:center; justify-content:center; color:#64748B;"><i class="fas fa-spinner fa-spin fa-2x"></i></div>';

        // 🛡️ AriOne Cache-Buster: Garante que o template refletirá as alterações imediatas
        const cacheBuster = `cb=${new Date().getTime()}`;
        const finalUrl = url.includes('?') ? `${url}&${cacheBuster}` : `${url}?${cacheBuster}`;

        fetch(finalUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(r => r.text())
            .then(html => {
                const base = window.location.origin;
                const htmlComBase = html.replace('</head>', `<base href="${base}/"></head>`);
                
                const iframe = document.createElement('iframe');
                iframe.style.cssText = 'flex:1; width:100%; height:100%; border:none; display:block; border-radius:0 0 16px 16px;';
                iframe.srcdoc = htmlComBase;
                content.innerHTML = '';
                content.appendChild(iframe);
            })
            .catch(err => {
                content.innerHTML = `<div style="padding:20px; color:#EF4444;">Erro ao carregar conteúdo: ${err}</div>`;
            });
    }
};

// =============================================================================
// OPERACIONAL HELPERS
// =============================================================================

window.arioneSalvarDocumento = async function(tipo, btn, forceFormId) {
    if (btn) {
        const formId = forceFormId || btn.closest('.fe-header-mestre')?.getAttribute('data-form-id') || 
                       btn.closest('.fe-header-simples')?.getAttribute('data-form-id');
        
        const form = formId ? document.getElementById(formId) : document.querySelector('form');

        if (!form) {
            console.error(`❌ AriOne: Formulário não localizado para ${tipo}`);
            return;
        }

        // 🛡️ HOOKS DE COLETA (Padrão Produto)
        if (typeof collectMatrixData === 'function') collectMatrixData(false);
        if (typeof collectComposicaoData === 'function') collectComposicaoData();
        // Hook genérico para outros formulários (futuro)
        if (typeof arioneBeforeSave === 'function') arioneBeforeSave(formId);

        // Validação básica
        if (!form.checkValidity()) {
            form.reportValidity();
            arioneToast('⚠️ Preencha os campos obrigatórios', 'warning');
            return;
        }

        // 🛡️ Confirmação Master (Exceto para Auto-Save/Silent)
        const isSilent = btn.id === 'autosave-indicator';
        if (!isSilent) {
            const confirm = await arioneConfirm(`🛡️ Deseja realmente salvar as alterações em ${tipo.replace('_', ' ').toUpperCase()}?`, btn);
            if (!confirm) return;
        }

        btn.disabled = true;
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> SALVANDO...';
        
        try {
            arioneToast(`⏳ Sincronizando ${tipo.replace('_', ' ')}...`, 'info');
            
            const formData = new FormData(form);
            const response = await fetch(form.action || window.location.href, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });

            const result = await response.json();

            if (result.success || response.ok) {
                arioneToast(`🚀 ${tipo.replace('_', ' ')} salvo com sucesso!`, 'success');
                
                // Atualiza ID e Status do Cabeçalho
                if (result.id) {
                    const idInput = form.querySelector('[name="id"]') || form.querySelector('#id') ||
                                    form.querySelector('[name="orcamento_id"]') || form.querySelector('#orcamento_id') ||
                                    form.querySelector('[name="pedido_id"]') || form.querySelector('#pedido_id') ||
                                    form.querySelector('[name="fornecedor_id"]') || form.querySelector('#fornecedor_id');
                    if (idInput) idInput.value = result.id;
                    
                    // Notifica o cabeçalho para mudar de "NOVO" para "EDITANDO"
                    if (window.syncHeaderStatus) window.syncHeaderStatus();
                }

                if (result.redirect) {
                    setTimeout(() => window.location.href = result.redirect, 1000);
                }
            } else {
                throw new Error(result.message || result.error || 'Erro interno no servidor');
            }
            
        } catch (err) {
            console.error("❌ AriOne Save Error:", err);
            arioneToast(`❌ Erro: ${err.message}`, 'danger');
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }
    }
};

window.arioneConverterDocumento = async function(docOrigem, btn) {
    if (confirm(`Deseja converter o orçamento ${docOrigem} em Pedido definitivo?`)) {
        if (btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        try {
            await new Promise(r => setTimeout(r, 1200));
            arioneToast(`🚀 Sucesso! Pedido gerado a partir de ${docOrigem}.`, 'success');
        } finally {
            if (btn) btn.innerHTML = '<i class="fas fa-exchange-alt"></i> Gerar Pedido';
        }
    }
};



window.arioneAdicionarLinhaGrid = function(tableSelector) {
    const table = document.querySelector(tableSelector + ' tbody');
    if (!table) return;
    const row = document.createElement('tr');
    row.innerHTML = `
        <td><input type="text" class="ope-input" placeholder="CÓDIGO..."></td>
        <td><div style="display: flex; gap: 8px; align-items: center;"><input list="lista-produtos" class="ope-input" placeholder="BUSCAR ITEM..."><i class="fas fa-comment-dots" style="color: #94A3B8; cursor: pointer;"></i></div></td>
        <td><input type="number" class="ope-input" value="1"></td>
        <td><input type="text" class="ope-input" style="text-align: right;" placeholder="0,00"></td>
        <td style="text-align:right; font-weight:900;">R$ 0,00</td>
    `;
    table.appendChild(row);
    row.querySelector('input').focus();
};

window.arioneWhatsApp = function(numero, mensagem) {
    const url = `https://api.whatsapp.com/send?phone=${numero}&text=${encodeURIComponent(mensagem)}`;
    window.open(url, '_blank');
};

window.arioneBuscarCEP = function(input) {
    const cep = input.value.replace(/\D/g, '');
    if (cep.length !== 8) return;

    input.style.opacity = '0.5';
    fetch(`https://viacep.com.br/ws/${cep}/json/`)
        .then(res => res.json())
        .then(data => {
            if (!data.erro) {
                // Tenta preencher no formulário atual
                const form = input.closest('form') || document;
                const campos = {
                    'logradouro': ['end_ent_logradouro', 'logradouro', 'rua'],
                    'bairro': ['end_ent_bairro', 'bairro'],
                    'localidade': ['end_ent_cidade', 'cidade', 'municipio'],
                    'uf': ['end_ent_uf', 'uf', 'estado']
                };

                for (let [key, names] of Object.entries(campos)) {
                    for (let name of names) {
                        const el = form.querySelector(`[name*="${name}"]`) || form.querySelector(`input[placeholder*="${name.toUpperCase()}"]`);
                        if (el) {
                            el.value = data[key].toUpperCase();
                            el.classList.add('cep-filled');
                        }
                    }
                }
                arioneToast('📍 Endereço localizado via CEP', 'info');
            } else {
                arioneToast('❌ CEP não encontrado', 'warning');
            }
        })
        .finally(() => {
            input.style.opacity = '1';
        });
};


// =============================================================================
// MÁSCARAS E INICIALIZAÇÃO
// =============================================================================

window.initMascaras = function(ctx) {
    ctx = ctx || document;
    ctx.querySelectorAll('.mask-cnpj').forEach(input => {
        input.addEventListener('input', function(e) {
            let v = e.target.value.replace(/\D/g, '');
            if (v.length <= 14) {
                v = v.replace(/^(\d{2})(\d)/, '$1.$2');
                v = v.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
                v = v.replace(/\.(\d{3})(\d)/, '.$1/$2');
                v = v.replace(/(\d{4})(\d)/, '$1-$2');
                e.target.value = v;
            } else {
                v = v.replace(/^(\d{3})(\d)/, '$1.$2');
                v = v.replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3');
                v = v.replace(/\.(\d{3})(\d)/, '.$1-$2');
                v = v.replace(/(\d{3})-(\d{2})$/, '$1-$2');
                e.target.value = v;
            }
        });
    });
};


// =============================================================================
// 🛡️ AriOne MASTER NAVIGATION (3 PILLARS)
// =============================================================================

window.abrirModalMaster = function(target) {
    console.log("🛡️ AriOne Master Logic: Buscando rota para", target);
    
    const rotas = {
      'revendedores': '/cadastros/revendedores/form',
      'perfis_venda': '/cadastros/perfis-venda/form',
      'tabelas_precos': '/operacoes/cards/vendas/tabelas-precos',
      'unidades': '/cadastros/cards/unidades', 
      'modelos': '/cadastros/produtos/catalogos/modelos',
      'categorias': '/cadastros/cards/categorias', 
      'subcategorias': '/cadastros/cards/subcategorias',
      'marcas': '/cadastros/cards/marcas', 
      'clientes': '/cadastros/clientes/cards/form',
      'produtos': '/cadastros/produtos/cards/form',
      'fornecedores': '/cadastros/fornecedores/cards/form',
      'depositos': '/cadastros/cards/depositos', 
      'cores': '/cadastros/cards/cores',
      'grades': '/cadastros/produtos/catalogos/modelos', 
      'tamanhos': '/cadastros/cards/tamanhos', 
      'atributos': '/cadastros/cards/atributos', 
      'materiaprima': '/cadastros/cards/materiaprima',
      'acessorios': '/cadastros/cards/acessorios',
      'insumos': '/cadastros/cards/insumos',
      'embalagens': '/cadastros/cards/embalagens',
      'servicos': '/cadastros/servicos/cards/form',
      'status': '/sistema/status/form'
    };

    let url = rotas[target] || `/cadastros/${target}/cards/form`;
    if (!url.includes('modal=')) {
        url += (url.includes('?') ? '&' : '?') + 'modal=1';
    }

    // Busca a função nos escopos disponíveis (Local -> Parent -> Top)
    const findFunc = (name) => {
        if (typeof window[name] === 'function') return window[name];
        if (window.parent && typeof window.parent[name] === 'function') return window.parent[name];
        if (window.top && typeof window.top[name] === 'function') return window.top[name];
        return null;
    };

    const funcGlobal = findFunc('abrirModalGlobal') || findFunc('abrirModalCat') || findFunc('abrirModalPess');

    if (funcGlobal) {
        funcGlobal(url);
    } else {
        console.warn("⚠️ AriOne: Função de abertura não encontrada. Abrindo em nova aba.");
        window.open(url, '_blank');
    }
};

document.addEventListener('DOMContentLoaded', function() {
    window.initMascaras(document);
});

// ── SUPORTE AO CABEÇALHO MESTRE ARIONE ──
window.focusSearchMaster = function() {
    const input = document.querySelector('.tool-search-input') || 
                  document.querySelector('input[placeholder*="PESQUISAR"]') ||
                  document.querySelector('input[placeholder*="Buscar"]') ||
                  document.querySelector('input[placeholder*="buscar"]') ||
                  document.querySelector('input[placeholder*="SKU"]') ||
                  document.querySelector('input[type="search"]');
    if (input) {
        input.focus();
        input.style.border = '2px solid var(--pri)';
    }
};

window.showOnlyList = function(formId) {
    // Se existir uma implementação local na página (como no form_produto), ela deve prevalecer.
    // Esta versão global serve apenas como fallback de fechamento.
    const fechar = window.fecharModalGlobal || 
                   (window.parent && window.parent.fecharModalGlobal) ||
                   window.fecharModalVnd || 
                   (window.parent && window.parent.fecharModalVnd);
                   
    if (typeof fechar === 'function') {
        fechar();
    } else {
        window.history.back();
    }
};

window.imprimirMaster = function() {
    arioneToast('🖨️ Gerando visualização de impressão...', 'info');
    setTimeout(() => window.print(), 500);
};

window.arioneImprimirDocumento = function(tipo) {
    arioneToast(`🖨️ Preparando impressão de ${tipo.replace('_', ' ').toUpperCase()}...`, 'info');
    setTimeout(() => window.print(), 500);
};

window.arioneEnviarWhatsApp = function(forceNum) {
    let num = forceNum;
    
    // Tenta encontrar o número no formulário atual automaticamente
    if (!num) {
        const inputNum = document.querySelector('input[name*="whatsapp"]') || 
                         document.querySelector('input[name*="celular"]') || 
                         document.querySelector('input[name*="telefone"]') ||
                         document.querySelector('input[id*="whatsapp"]') ||
                         document.querySelector('input[id*="celular"]');
        if (inputNum && inputNum.value) {
            num = inputNum.value.replace(/\D/g, '');
        }
    }

    const msg = encodeURIComponent(`Olá! Segue o link do documento gerado pelo AriOne: ${window.location.href}`);
    
    if (num) {
        // Se temos o número, abre a conversa direta
        const cleanNum = num.length <= 11 ? `55${num}` : num;
        window.open(`https://api.whatsapp.com/send?phone=${cleanNum}&text=${msg}`, '_blank');
        arioneToast('🚀 Abrindo conversa no WhatsApp...', 'success');
    } else {
        // Se não temos, abre o WhatsApp Web genérico ou pede (dependendo da preferência)
        // O usuário disse "abrir o zap, não é o padrão?", então vamos abrir sem número se nada for achado.
        window.open(`https://web.whatsapp.com/send?text=${msg}`, '_blank');
        arioneToast('🚀 Abrindo WhatsApp Web...', 'info');
    }
};

window.arioneEnviarEmail = function(forceEmail) {
    let email = forceEmail;
    
    // Tenta encontrar o e-mail no formulário atual automaticamente
    if (!email) {
        const inputEmail = document.querySelector('input[name*="email"]') || 
                           document.querySelector('input[id*="email"]');
        if (inputEmail && inputEmail.value) {
            email = inputEmail.value.trim();
        }
    }

    const subject = encodeURIComponent("Documento Enviado via AriOne");
    const body = encodeURIComponent(`Olá!\n\nSegue o link para visualização do documento: ${window.location.href}\n\nAtenciosamente,\nEquipe AriOne.`);
    
    const mailtoUrl = email ? `mailto:${email}?subject=${subject}&body=${body}` : `mailto:?subject=${subject}&body=${body}`;
    
    // Cria um link temporário para evitar bloqueios de popup e forçar nova aba/instância
    const link = document.createElement('a');
    link.href = mailtoUrl;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    setTimeout(() => document.body.removeChild(link), 100);
    
    arioneToast('📧 Abrindo e-mail...', 'info');
};

window.exportarMaster = function() {
    arioneToast('📥 Preparando download dos dados...', 'success');
    // Simulação de download ou redirecionamento para rota de exportação
    setTimeout(() => {
        arioneToast('✅ Download iniciado!', 'success');
    }, 1000);
};

window.importXMLMaster = function() {
    // Cria um input de arquivo temporário para disparar a tela padrão de upload
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.xml,.csv,.json';
    input.onchange = e => {
        const file = e.target.files[0];
        if (file) {
            arioneToast(`📤 Processando arquivo: ${file.name}`, 'info');
            // Aqui entraria a lógica de upload via AJAX para o backend
        }
    };
    input.click();
};

window.arioneResetForm = function(btnOrId) {
    console.log("♻️ AriOne: Iniciando reset profundo de formulário...");
    let form;
    if (typeof btnOrId === 'string') {
        form = document.getElementById(btnOrId);
    } else if (btnOrId instanceof HTMLElement) {
        form = btnOrId.closest('.fe-wrap')?.querySelector('form') || 
               btnOrId.closest('.fp-wrap')?.querySelector('form') || 
               document.getElementById(btnOrId.closest('.fe-header-mestre')?.getAttribute('data-form-id')) ||
               document.querySelector('form');
    } else {
        form = document.querySelector('form');
    }

    if (!form) {
        console.error('❌ AriOne: Formulário não localizado para reset');
        return;
    }

    // 1. Reset nativo (limpa inputs, selects, etc)
    form.reset();

    // 2. Limpeza de IDs ocultos (essencial para virar "NOVO")
    form.querySelectorAll('input[type="hidden"]').forEach(i => {
        // Preserva tokens de segurança
        if (i.name === 'csrf_token' || i.name.includes('csrf') || i.name.includes('grupo_config')) return;
        
        // Zera IDs de registro
        if (i.name === 'id' || i.id === 'id' || i.name.includes('_id') || i.id.includes('_id')) {
            i.value = '';
        }
    });

    // 3. Limpeza forçada de campos de número de documento para engatilhar auto-numeração
    const numInput = form.querySelector('input[name="numero"]') || form.querySelector('#doc_numero');
    if (numInput) {
        numInput.value = '';
    }

    // 4. Re-inicializa parâmetros e numeração automática
    if (typeof carregarParametrosVendas === 'function') {
        console.log("⚡ AriOne: Re-inicializando parâmetros de vendas...");
        carregarParametrosVendas();
    } else if (typeof arioneInitForm === 'function') {
        console.log("⚡ AriOne: Re-inicializando parâmetros globais...");
        arioneInitForm();
    } else {
        if (form.id.includes('orcamento') || form.id.includes('pedido')) {
            fetch('/cadastros/parametros/get?grupo=vendas')
                .then(res => res.json())
                .then(data => {
                    if (numInput && !numInput.value) {
                        const isOrc = form.id.includes('orcamento');
                        const ultKey = isOrc ? 'ult_orcamento' : 'ult_pedido';
                        const prefKey = isOrc ? 'pref_orc' : 'pref_ped';
                        const usarKey = isOrc ? 'usar_sequencia_automatica_orc' : 'usar_sequencia_automatica_ped';
                        
                        const usarAuto = data[usarKey] !== '0';
                        if (usarAuto && data[ultKey]) {
                            const inc = parseInt(data.incremento) || 1;
                            let pref = data[prefKey] || (isOrc ? 'ORV-' : 'PV-');
                            const reiniciarAnual = data.reiniciar_anual === '1';
                            if (reiniciarAnual) {
                                const ano = new Date().getFullYear().toString();
                                if (!pref.includes(ano)) {
                                    pref = pref.replace(/-$/, '') + '-' + ano + '-';
                                }
                            }
                            const proxNum = (parseInt(data[ultKey]) || (isOrc ? 5348 : 8210)) + inc;
                            numInput.value = pref + proxNum;
                        }
                    }
                }).catch(e => console.error(e));
        }
    }

    // 5. Atualiza badges de status se houver
    const statusPill = document.getElementById('header-action-status') || document.querySelector('.fe-badge-status');
    if (statusPill) {
        statusPill.innerHTML = 'NOVO REGISTRO';
        statusPill.style.background = 'rgba(255,255,255,0.3)';
    }

    // 6. Foco no primeiro campo útil
    const firstInput = form.querySelector('input:not([type="hidden"]):not([disabled]):not([readonly])');
    if (firstInput) firstInput.focus();

    arioneToast('✨ Pronto para novo registro', 'success');
};

// ── LÓGICA DE DROPDOWNS (ARIONE GOLDEN STANDARD) ──
window.toggleExtraActions = function(btn) {
    console.log("🎯 AriOne Header: Toggle Extra Actions disparado");
    const menu = btn.nextElementSibling;
    if (!menu) {
        console.warn("⚠️ AriOne Header: Menu suspenso não encontrado");
        return;
    }
    
    const isVisible = menu.style.display === 'block';
    console.log("🔍 Estado atual do menu:", isVisible ? "Visível" : "Oculto");
    
    // Fecha todos os outros menus abertos para evitar sobreposição
    document.querySelectorAll('.fe-dropdown-menu-arione').forEach(m => m.style.display = 'none');
    
    if (!isVisible) {
        menu.style.display = 'block';
        menu.style.zIndex = '999999';
        menu.style.animation = 'feFadeUp 0.3s ease forwards';
    }
};

// Listener global para fechar menus ao clicar fora do componente de cabeçalho
document.addEventListener('click', function(e) {
    if (!e.target.closest('.fe-action-group-glass')) {
        document.querySelectorAll('.fe-dropdown-menu-arione').forEach(m => m.style.display = 'none');
    }
});

// ── LÓGICA DE MODAIS E NAVEGAÇÃO MASTER ──
window.abrirModalMaster = function(target) {
    console.log("🛡️ AriOne Master Logic: Buscando rota para", target);
    
    const rotas = {
      'unidades': '/cadastros/cards/unidades', 
      'modelos': '/cadastros/produtos/catalogos/modelos',
      'categorias': '/cadastros/cards/categorias', 
      'subcategorias': '/cadastros/cards/subcategorias',
      'marcas': '/cadastros/cards/marcas', 
      'fornecedores': '/cadastros/fornecedores/cards/form',
      'depositos': '/cadastros/cards/depositos', 
      'cores': '/cadastros/cards/cores',
      'grades': '/cadastros/produtos/catalogos/modelos', 
      'tamanhos': '/cadastros/cards/tamanhos', 
      'atributos': '/cadastros/cards/atributos', 
      'materiaprima': '/cadastros/cards/materiaprima',
      'acessorios': '/cadastros/cards/acessorios',
      'insumos': '/cadastros/cards/insumos',
      'embalagens': '/cadastros/cards/embalagens',
      'servicos': '/cadastros/servicos/cards/form',
      'status': '/sistema/status/form',
      'tabelas_precos': '/operacoes/cards/vendas/tabelas-precos',
      'perfis_venda': '/cadastros/perfis-venda/form',
      'comercial': '/operacoes/cards/vendas/tabelas-precos',
      'funcionarios': '/cadastros/funcionarios/cards/form',
      'vendedores': '/cadastros/funcionarios/cards/form',
      'transportadoras': '/cadastros/transportadoras/form'
    };

    const url = rotas[target] || `/cadastros/${target}/cards/form`;
    
    const findFunc = (name) => {
        if (typeof window[name] === 'function') return window[name];
        if (window.parent && typeof window.parent[name] === 'function') return window.parent[name];
        if (window.top && typeof window.top[name] === 'function') return window.top[name];
        return null;
    };

    const funcGlobal = findFunc('abrirModalGlobal') || findFunc('abrirModalCat') || findFunc('abrirModalPess');

    if (funcGlobal) {
        funcGlobal(url);
    } else {
        console.warn("⚠️ AriOne: Função de abertura não encontrada. Abrindo em nova aba.");
        window.open(url, '_blank');
    }
};

// ── LÓGICA DE VISUALIZAÇÃO ADAPTATIVA ──
window.toggleFormView = function(id, btn) {
    const target = document.getElementById(id) || document.querySelector('.fe-form-editor-area');
    if (!target) return;
    
    const isVisible = target.style.display !== 'none';
    const icon = btn.querySelector('i');
    
    if (isVisible) {
        target.style.display = 'none';
        if (icon) icon.className = 'fas fa-expand';
        btn.title = "Expandir Formulário";
        btn.style.background = "rgba(255,255,255,0.2)";
    } else {
        target.style.display = 'block';
        if (icon) icon.className = 'fas fa-compress';
        btn.title = "Ocultar Formulário";
        btn.style.background = "rgba(0,0,0,0.1)";
        target.style.animation = 'feFadeUp 0.4s ease forwards';
    }
};

window.showOnlyList = function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const editors = container.querySelectorAll('.fe-form-editor-area');
    editors.forEach(el => el.style.display = 'none');
    
    const list = container.querySelector('.fe-table-zebra') || container.querySelector('table');
    if (list) {
        list.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
};

window.arioneClonarRegistro = function(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Remove o ID para que o sistema entenda como um novo registro ao salvar
    const idInputs = form.querySelectorAll('input[name="id"], input[name*="id_"]');
    idInputs.forEach(i => i.value = '');
    
    // Notifica o usuário
    arioneToast('📋 Registro clonado! Altere os dados e clique em Salvar.', 'info');
    
    // Atualiza status se houver
    if (window.mostrarStatusNovo) window.mostrarStatusNovo();
};

window.arioneAlternarVisualizacao = function(formId, listId) {
    if (!formId || !listId) {
        console.warn("⚠️ AriOne: form_id ou list_id ausentes para arioneAlternarVisualizacao");
        return;
    }
    
    // Fallbacks para IDs comuns se não encontrar o exato
    let form = document.getElementById(formId) || document.getElementById(formId.replace('tamanho-', 'tam-')) || document.getElementById(formId.replace('fornecedor-', 'forn-'));
    let list = document.getElementById(listId) || document.getElementById(listId.replace('tamanho-', 'tam-')) || document.getElementById(listId.replace('fornecedor-', 'forn-'));
    
    if (!form && !list) {
        console.error(`❌ AriOne: Elementos não encontrados para alternar visualização: form (${formId}), list (${listId})`);
        return;
    }
    
    // 💡 Correção: Nunca ocultar a lista principal, pois a barra de pesquisa/filtros geralmente fica dentro dela.
    // Apenas alternamos a visibilidade do formulário para dar mais espaço à lista.
    if (form) {
        if (form.style.display !== 'none') {
            form.style.display = 'none';
            if (typeof arioneToast === 'function') arioneToast('Formulário Oculto. Visualizando Grade.', 'info');
        } else {
            form.style.display = 'block';
            // Se reativou o form, rola suavemente pro form
            form.scrollIntoView({ behavior: 'smooth', block: 'start' });
            return;
        }
    }
    
    if (list) {
        list.style.display = 'block'; // Garante que a lista está visível
        list.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
};

// =============================================================================
// 🔍 PAA §2 — FUNÇÕES GLOBAIS DO CABEÇALHO MESTRE (toggleSearchZone / toggleFilterZone / showOnlyList)
// Fallbacks genéricos. Se a página definir versão local, ela prevalece automaticamente.
// =============================================================================

window.toggleSearchZone = window.toggleSearchZone || function() {
    let zone = document.getElementById('arione-search-zone');
    if (zone) { zone.remove(); return; }

    // Encontra a tabela principal na página
    const table = document.querySelector('.fe-table-listing, .fe-table, .fe-table-zebra, table[id*="tabela"]');
    const listCard = table ? table.closest('.fe-card, .fe-card-body') : null;
    const insertTarget = listCard || document.querySelector('.fe-form-stage-medio, .fe-form-stage, .fp-wrap, .fe-wrap');

    if (!insertTarget) { arioneToast('Zona de pesquisa não disponível neste contexto.', 'warning'); return; }

    zone = document.createElement('div');
    zone.id = 'arione-search-zone';
    zone.style.cssText = 'padding:10px 20px; background:#fff; border-bottom:1px solid #eee; display:flex; align-items:center; gap:10px; animation:feFadeIn 0.2s ease;';
    zone.innerHTML = `<i class="fas fa-search" style="color:var(--pri,#7A255F);"></i>
        <input type="text" id="arione-search-input" placeholder="Pesquisar na listagem..."
            style="flex:1; border:1.5px solid var(--pri,#7A255F); border-radius:8px; padding:8px 14px; font-size:13px; outline:none; font-weight:700;">
        <button onclick="document.getElementById('arione-search-zone').remove()"
            style="background:none; border:none; color:#999; cursor:pointer; font-size:16px;" title="Fechar pesquisa">✕</button>`;

    if (listCard) {
        listCard.insertBefore(zone, listCard.querySelector('.fe-card-body') || listCard.firstChild);
    } else {
        insertTarget.insertBefore(zone, insertTarget.firstChild);
    }

    const input = zone.querySelector('input');
    input.focus();
    input.addEventListener('input', function() {
        const filter = this.value.toLowerCase();
        if (!table) return;
        table.querySelectorAll('tbody tr').forEach(row => {
            row.style.display = row.innerText.toLowerCase().includes(filter) ? '' : 'none';
        });
    });
};

window.toggleFilterZone = window.toggleFilterZone || function() {
    let zone = document.getElementById('arione-filter-zone');
    if (zone) { zone.remove(); return; }

    const table = document.querySelector('.fe-table-listing, .fe-table, .fe-table-zebra, table[id*="tabela"]');
    const listCard = table ? table.closest('.fe-card, .fe-card-body') : null;
    const insertTarget = listCard || document.querySelector('.fe-form-stage-medio, .fe-form-stage, .fp-wrap, .fe-wrap');

    if (!insertTarget) { arioneToast('Zona de filtros não disponível neste contexto.', 'warning'); return; }

    // Coleta colunas da tabela para criar filtros dinâmicos
    const headers = table ? Array.from(table.querySelectorAll('thead th')).slice(1, 4) : [];
    let filtersHTML = headers.map((th, i) => {
        const colName = th.textContent.trim();
        const values = new Set();
        table.querySelectorAll('tbody tr').forEach(row => {
            const cell = row.cells[i + 1];
            if (cell) values.add(cell.textContent.trim());
        });
        const opts = Array.from(values).sort().map(v => `<option value="${v}">${v}</option>`).join('');
        return `<div style="flex:1; min-width:150px;">
            <label style="font-size:10px; font-weight:800; color:#64748b; text-transform:uppercase; margin-bottom:5px; display:block;">${colName}</label>
            <select class="arione-filter-select fe-input" data-col="${i + 1}" style="width:100%;" onchange="window._arioneApplyFilters()">
                <option value="">TODOS</option>${opts}
            </select>
        </div>`;
    }).join('');

    zone = document.createElement('div');
    zone.id = 'arione-filter-zone';
    zone.style.cssText = 'padding:15px 20px; background:#f8fafc; border-bottom:1px solid #e2e8f0; display:flex; flex-wrap:wrap; gap:15px; animation:feFadeIn 0.3s ease;';
    zone.innerHTML = filtersHTML + `<button onclick="document.getElementById('arione-filter-zone').remove()"
        style="background:none; border:none; color:#94a3b8; cursor:pointer; align-self:flex-end; padding-bottom:10px;" title="Fechar Filtros"><i class="fas fa-times"></i></button>`;

    if (listCard) {
        listCard.insertBefore(zone, listCard.querySelector('.fe-card-body') || listCard.firstChild);
    } else {
        insertTarget.insertBefore(zone, insertTarget.firstChild);
    }
};

window._arioneApplyFilters = function() {
    const table = document.querySelector('.fe-table-listing, .fe-table, .fe-table-zebra, table[id*="tabela"]');
    if (!table) return;
    const selects = document.querySelectorAll('.arione-filter-select');
    table.querySelectorAll('tbody tr').forEach(row => {
        let show = true;
        selects.forEach(sel => {
            if (!sel.value) return;
            const colIdx = parseInt(sel.dataset.col);
            const cell = row.cells[colIdx];
            if (cell && cell.textContent.trim() !== sel.value) show = false;
        });
        row.style.display = show ? '' : 'none';
    });
};

window.arioneToggleFilter = function(filterId, btnContext) {
    const filterBar = document.getElementById(filterId);
    if (filterBar) {
        if (typeof jQuery !== 'undefined') {
            $(filterBar).slideToggle(300);
        } else {
            filterBar.style.display = (filterBar.style.display === 'none') ? 'block' : 'none';
        }
    } else {
        console.warn("⚠️ AriOne: Barra de filtros não encontrada:", filterId);
        if (typeof arioneToast === 'function') arioneToast('Filtro avançado não configurado', 'warning');
    }
};

// =============================================================================
// 🏛️ ARIONE MASTER BANKING ENGINE (TABELA FEBRABAN GLOBAL E BRASILAPI)
// =============================================================================

window.TABELA_FEBRABAN_GLOBAL = {
    "001": { nome: "BANCO DO BRASIL S.A.", ispb: "00000000" },
    "003": { nome: "BANCO DA AMAZÔNIA S.A.", ispb: "04902979" },
    "004": { nome: "BANCO DO NORDESTE DO BRASIL S.A.", ispb: "07237373" },
    "021": { nome: "BANESTES S.A. BANCO DO ESTADO DO ESPÍRITO SANTO", ispb: "28127603" },
    "033": { nome: "BANCO SANTANDER (BRASIL) S.A.", ispb: "90400888" },
    "041": { nome: "BANCO DO ESTADO DO RIO GRANDE DO SUL S.A. (BANRISUL)", ispb: "92702067" },
    "047": { nome: "BANCO DO ESTADO DE SERGIPE S.A. (BANESE)", ispb: "13009717" },
    "070": { nome: "BRB - BANCO DE BRASÍLIA S.A.", ispb: "00000208" },
    "077": { nome: "BANCO INTER S.A.", ispb: "00416968" },
    "104": { nome: "CAIXA ECONÔMICA FEDERAL", ispb: "00360305" },
    "212": { nome: "BANCO ORIGINAL S.A.", ispb: "92894922" },
    "237": { nome: "BANCO BRADESCO S.A.", ispb: "60746948" },
    "260": { nome: "NU PAGAMENTOS S.A. (NUBANK)", ispb: "18236120" },
    "336": { nome: "BANCO C6 S.A.", ispb: "31872495" },
    "341": { nome: "ITAÚ UNIBANCO S.A.", ispb: "60701190" },
    "389": { nome: "BANCO MERCANTIL DO BRASIL S.A.", ispb: "17184037" },
    "422": { nome: "BANCO SAFRA S.A.", ispb: "58160789" },
    "623": { nome: "BANCO PAN S.A.", ispb: "59285411" },
    "633": { nome: "BANCO RENDIMENTO S.A.", ispb: "68900810" },
    "652": { nome: "ITAÚ UNIBANCO HOLDING S.A.", ispb: "60872504" },
    "655": { nome: "BANCO VOTORANTIM S.A. (BV)", ispb: "59588111" },
    "739": { nome: "BANCO CETELEM S.A.", ispb: "00558456" },
    "745": { nome: "BANCO CITIBANK S.A.", ispb: "33479023" },
    "748": { nome: "BANCO COOPERATIVO SICREDI S.A.", ispb: "01181521" },
    "756": { nome: "BANCO COOPERATIVO SICOOB S.A.", ispb: "02038232" }
};

document.addEventListener('DOMContentLoaded', function() {
    const dListIds = ['lista-bancos-febraban', 'lista-bancos-febraban-mestre', 'lista-bancos-febraban-cad', 'lista-bancos'];
    
    dListIds.forEach(id => {
        let dl = document.getElementById(id);
        if (!dl) {
            dl = document.createElement('datalist');
            dl.id = id;
            document.body.appendChild(dl);
        }
        
        dl.innerHTML = '';
        Object.entries(window.TABELA_FEBRABAN_GLOBAL).forEach(([cod, b]) => {
            const opt = document.createElement('option');
            opt.value = `${cod} - ${b.nome}`;
            dl.appendChild(opt);
        });
    });

    document.querySelectorAll('input[list*="lista-bancos"], input[name*="banco"]').forEach(input => {
        input.addEventListener('input', async function(e) {
            const val = e.target.value.trim();
            const form = input.closest('form') || document;
            const inpCod = form.querySelector('[name="cod"]') || form.querySelector('[name="codigo_banco"]');
            const inpIspb = form.querySelector('[name="ispb"]');

            if (val.includes(' - ')) {
                const partes = val.split(' - ');
                const cod = partes[0].trim();
                const nome = partes.slice(1).join(' - ').trim();
                if (inpCod) inpCod.value = cod;
                if (inpIspb && window.TABELA_FEBRABAN_GLOBAL[cod]) inpIspb.value = window.TABELA_FEBRABAN_GLOBAL[cod].ispb;
            } else if (val.length === 3 && !isNaN(val)) {
                if (window.TABELA_FEBRABAN_GLOBAL[val]) {
                    const b = window.TABELA_FEBRABAN_GLOBAL[val];
                    input.value = `${val} - ${b.nome}`;
                    if (inpCod) inpCod.value = val;
                    if (inpIspb) inpIspb.value = b.ispb;
                    if (typeof arioneToast === 'function') arioneToast(`Banco localizado: ${b.nome}`, 'success');
                } else {
                    try {
                        const res = await fetch(`https://brasilapi.com.br/api/banks/v1/${val}`);
                        if (res.ok) {
                            const data = await res.json();
                            const nomeBanco = data.name || data.fullName;
                            input.value = `${val} - ${nomeBanco}`;
                            if (inpCod) inpCod.value = val;
                            if (inpIspb && data.ispb) inpIspb.value = data.ispb;
                            if (typeof arioneToast === 'function') arioneToast(`Banco localizado via BrasilAPI: ${nomeBanco}`, 'success');
                        }
                    } catch(err) { console.log('Erro BrasilAPI', err); }
                }
            }
        });
    });
});

// =============================================================================
// 🏛️ FUNÇÕES PADRONIZADAS DOS BOTÕES DE AÇÃO DO CABEÇALHO MESTRE ARI-ONE
// =============================================================================

// Função genérica para voltar para a grid (pode ser sobrescrita em cada formulário)
window.arioneVoltarParaGrid = function(aba) {
    if (typeof fecharModalGlobal === 'function') fecharModalGlobal();
    if (!window.location.search.includes(`aba=${aba}`)) {
        window.location.href = `/financeiro/abas?aba=${aba}`;
    }
};

// Função genérica para atualizar dados (reload da página)
window.arioneAtualizarDados = function() {
    if (typeof arioneToast === 'function') arioneToast('Atualizando dados...', 'info');
    window.location.reload();
};

// Função genérica para salvar (placeholder)
window.arioneSalvar = function(formId) {
    if (typeof arioneToast === 'function') arioneToast('Salvando registro...', 'info');
    const form = document.getElementById(formId);
    if (form) form.submit();
};

// Função genérica para focar pesquisa
window.arioneFocarPesquisa = function(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.focus();
        if (typeof arioneToast === 'function') arioneToast('Campo de pesquisa ativado', 'info');
    } else {
        const termo = prompt("Digite o termo para buscar:");
        if (termo !== null && typeof arioneToast === 'function') {
            arioneToast(`Pesquisando por: ${termo}`, 'info');
        }
    }
};

// Função genérica para abrir filtros
window.arioneAbrirFiltros = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('ativo');
    } else {
        if (typeof arioneToast === 'function') arioneToast('Filtros avançados em desenvolvimento', 'info');
    }
};

// Função genérica para alternar visão formulário/lista
window.arioneAlternarVisaoFormLista = function(formId, listId) {
    if (formId && listId) {
        arioneAlternarVisualizacao(formId, listId);
    } else {
        if (typeof arioneToast === 'function') arioneToast('Alternando visão formulário/lista', 'info');
    }
};

// Função genérica para clonar
window.arioneClonar = function(formId) {
    if (formId) {
        arioneClonarRegistro(formId);
    } else {
        if (typeof arioneToast === 'function') arioneToast('Clonagem indisponível nesta visão', 'info');
    }
};

// Função genérica para exportar CSV
window.arioneExportarCSV = function(tabelaId, nomeArquivo) {
    const tabela = document.getElementById(tabelaId) || document.querySelector('table');
    if (!tabela) {
        if (typeof arioneToast === 'function') arioneToast('Tabela não encontrada para exportação', 'warning');
        return;
    }

    let csv = [];
    const linhas = tabela.querySelectorAll('tr');
    linhas.forEach(linha => {
        let cols = linha.querySelectorAll('th, td');
        let linhaArr = [];
        cols.forEach(col => {
            let texto = col.innerText.replace(/(\r\n|\n|\r)/gm, " ").trim();
            linhaArr.push(`"${texto}"`);
        });
        if (linhaArr.length > 0) csv.push(linhaArr.join(','));
    });

    const csvFile = new Blob([csv.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const downloadLink = document.createElement('a');
    downloadLink.download = nomeArquivo || 'exportacao_arione.csv';
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    if (typeof arioneToast === 'function') arioneToast('Arquivo exportado com sucesso!', 'success');
};

// Função genérica para importar
window.arioneImportar = function() {
    if (typeof arioneToast === 'function') arioneToast('Importação em desenvolvimento', 'info');
};

// Função genérica para imprimir
window.arioneImprimir = function() {
    window.print();
};

// Função genérica para enviar por e-mail
window.arioneEnviarEmail = function(assunto, corpo) {
    const mailtoLink = `mailto:?subject=${encodeURIComponent(assunto || 'Relatório AriOne')}&body=${encodeURIComponent(corpo || '')}`;
    window.location.href = mailtoLink;
    if (typeof arioneToast === 'function') arioneToast('Abrindo cliente de E-mail...', 'info');
};

// Função genérica para enviar por WhatsApp
window.arioneEnviarWhatsApp = function(texto) {
    const whatsappLink = `https://api.whatsapp.com/send?text=${encodeURIComponent(texto || '*AriOne Financeiro*')}`;
    window.open(whatsappLink, '_blank');
    if (typeof arioneToast === 'function') arioneToast('Abrindo WhatsApp Web...', 'info');
};

console.log('✅ Funções padronizadas dos botões de ação carregadas');