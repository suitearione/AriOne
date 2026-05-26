/* =============================================================================
   Arquivo  : static/js/fp-engine.js
   Função   : Lógica do Sistema de Design "Front Product" (FP) - Golden Standard
   ============================================================================= */

console.log('🛡️ AriOne FP-Engine: V3 - Ultra Resiliência');

window.fpAction = function(btn, actionName) {
    // 1. Localiza o container mais próximo
    const wrap = btn.closest('.fp-wrap') || btn.closest('.fe-wrap') || document.querySelector('.modal.show') || document.body;
    
    console.log(`🛡️ Action: ${actionName} em`, wrap);

    // Feedback Visual
    btn.classList.add('fp-btn-clicked');
    setTimeout(() => btn.classList.remove('fp-btn-clicked'), 150);

    try {
        switch(actionName) {
            case 'toggle-form':
                const bodies = wrap.querySelectorAll('.fp-card-body, .fe-card-body, form > .fp-row');
                const isHiding = !btn.classList.contains('active');
                btn.classList.toggle('active');
                bodies.forEach(b => b.style.display = isHiding ? 'none' : 'block');
                const icon = btn.querySelector('i');
                if (icon) icon.className = isHiding ? 'fas fa-eye' : 'fas fa-eye-slash';
                break;

            case 'search':
                const input = wrap.querySelector('input[type="text"]:not([disabled]), input[type="search"]');
                if (input) {
                    input.focus();
                    input.classList.add('fp-highlight');
                    setTimeout(() => input.classList.remove('fp-highlight'), 1500);
                }
                break;

            case 'save':
                const form = wrap.querySelector('form') || wrap.closest('form') || document.querySelector('form');
                if (form) {
                    if (form.checkValidity()) {
                        const i = btn.querySelector('i');
                        if (i) i.className = 'fas fa-spinner fa-spin';
                        form.submit();
                    } else {
                        form.reportValidity();
                    }
                }
                break;

            case 'new':
                const f = wrap.querySelector('form') || document.querySelector('form');
                if (f) {
                    f.reset();
                    f.querySelectorAll('input[type="hidden"]').forEach(h => h.value = '');
                    const first = f.querySelector('input[type="text"]');
                    if (first) first.focus();
                } else {
                    window.location.reload();
                }
                break;

            case 'back':
                // Tenta todos os métodos de fechamento do AriOne
                if (typeof fecharModalCat === 'function') fecharModalCat();
                else if (typeof fecharModal === 'function') fecharModal();
                else {
                    const close = document.querySelector('.modal.show [data-bs-dismiss="modal"], .modal.show .btn-close, #arione-modal-global .btn-close');
                    if (close) close.click();
                    else window.history.back();
                }
                break;

            case 'toggle-list':
                const tables = wrap.querySelectorAll('.fp-table-wrap, table, .fp-card:has(table)');
                tables.forEach(t => {
                    t.style.display = (t.style.display === 'none') ? 'block' : 'none';
                });
                break;

            case 'print':
                window.print();
                break;

            default:
                console.log('🛡️ Recurso Premium:', actionName);
        }
    } catch (err) {
        console.error('🛡️ FP-Engine Error:', err);
    }
};

// Reinicialização para garantir delegação
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.fp-tool-btn') || e.target.closest('.fp-btn-main-novo');
    if (!btn && e.target.tagName === 'BUTTON') return;
    if (btn) {
        const action = btn.getAttribute('data-fp-action');
        if (action && !btn.onclick) {
            window.fpAction(btn, action);
        }
    }
});
