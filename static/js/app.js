// ================================
// ABAS DE CADASTRO – CONTROLE UI
// ================================
document.addEventListener("click", function (e) {
    const btn = e.target.closest(".tab-btn");
    if (!btn) return;

    const container = btn.closest(".arione-tabs");
    const tabId = btn.getAttribute("data-tab");

    // Desativa todos os botões
    container.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.remove("active");
    });

    // Oculta todos os conteúdos
    container.querySelectorAll(".tab-content").forEach(c => {
        c.classList.remove("active");
    });

    // Ativa o selecionado
    btn.classList.add("active");
    container.querySelector("#tab-" + tabId).classList.add("active");
});

// ================================
// FUNÇÃO GLOBAL: ALTERNAR VISÃO FORMULÁRIO/LISTA
// ================================
function alternarVisaoFormLista(formId, listId) {
    if (formId && listId) {
        if (typeof window.arioneAlternarVisaoFormLista === 'function') {
            return window.arioneAlternarVisaoFormLista(formId, listId);
        }
    }

    const formCard = document.querySelector('.op-card:nth-child(1)');
    const gridCard = document.querySelector('.op-card:nth-child(2)');
    const btnList = document.querySelector('[onclick="alternarVisaoFormLista()"]');
    
    if (formCard && gridCard) {
        if (formCard.style.display === 'none') {
            formCard.style.display = 'block';
            gridCard.style.display = 'none';
            if (btnList) {
                btnList.innerHTML = '<i class="fas fa-list"></i>';
                btnList.title = 'Ver Lista';
            }
            if (typeof arioneToast === 'function') arioneToast('Visualizando formulário', 'info');
        } else {
            formCard.style.display = 'none';
            gridCard.style.display = 'block';
            if (btnList) {
                btnList.innerHTML = '<i class="fas fa-edit"></i>';
                btnList.title = 'Ver Formulário';
            }
            if (typeof arioneToast === 'function') arioneToast('Visualizando listagem', 'info');
        }
    }
}

// ================================
// FUNÇÕES GLOBAIS: FILTROS DE TABELA
// ================================
function abrirModalFiltrosAvancados(modalId = 'modal-filtros-avancados') {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('ativo');
}

function fecharModalFiltros(modalId = 'modal-filtros-avancados') {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('ativo');
}

function filtrarTabelaGenerico(seletorLinhas, filtroTexto, seletorStatus = null, statusValor = null) {
    const linhas = document.querySelectorAll(seletorLinhas);
    const texto = filtroTexto.toLowerCase();
    
    linhas.forEach(linha => {
        let visivel = true;
        const textoLinha = linha.innerText.toLowerCase();
        
        if (texto && !textoLinha.includes(texto)) visivel = false;
        
        if (seletorStatus && statusValor) {
            const status = linha.querySelector(seletorStatus);
            if (status && status.value !== statusValor) visivel = false;
        }
        
        linha.style.display = visivel ? '' : 'none';
    });
}
