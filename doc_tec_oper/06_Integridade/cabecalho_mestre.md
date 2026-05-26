# Padronização de Botões de Ação do Cabeçalho Mestre AriOne

## Referência: Formulário de Contas a Receber/Pagar
Este formulário está configurado corretamente e deve servir como modelo para padronização.

## Especificações Visuais e de Design (Baseado em PAAv1.md)

### Iconografia e Sincronia
- **Ícone Principal**: Deve ser RIGOROSAMENTE IDÊNTICO ao ícone utilizado na Sidebar do respectivo módulo
- **Unidade Visual**: Esta sincronia é fundamental para a orientação espacial imediata do usuário dentro da plataforma

### Anatomia do Título Principal
- **Cor**: Deve utilizar o HEX exato da Cor Original do módulo
- **Fonte**: Uso obrigatório de `font-weight: 800` e `text-transform: uppercase` (MAIÚSCULA)
- **Objetivo**: Criar uma conexão direta e instantânea com o botão de navegação

### Anatomia do Subtítulo (Título Menor)
- **Cor**: Branco Sólido (#FFFFFF) com `opacity: 1`
- **Fonte**: Uso obrigatório de `font-weight: 700` e `text-transform: uppercase` (MAIÚSCULA)
- **Legibilidade**: Proibido o uso de opacidades parciais (0.6, 0.8) sobre o fundo roxo, para evitar o efeito visual "rosado". O subtítulo deve ser 100% nítido

### Comportamento e Gradiente
- **Fundo**: Gradiente linear institucional (`#7A255F` a `#a63282`)
- **Botões de Ação**: Alinhados à direita, mantendo o estilo minimalista e funcional
- **Ocultação por Permissão (Shield)**: Botões de ação (Novo, Salvar, Clonar) devem ser ocultados automaticamente se o perfil logado não possuir permissão de escrita/edição para o módulo
- **Subtítulo Dinâmico (Breadcrumbs)**: O caminho de navegação (ex: Home > Vendas > Pedidos) deve ser preciso e refletir a hierarquia real do sistema, servindo como guia de localização para o usuário

### Arquitetura de Ações e Dropdown
Para manter a interface minimalista ("Quiet Luxury") e evitar poluição visual, as ações do cabeçalho devem seguir rigorosamente a seguinte divisão:

- **Ações Primárias e de Visualização (Exibidas na Raiz)**:
  1. Pesquisar (Lupa)
  2. Filtros (Sliders)
  3. Ver Lista (Lista)
  4. Clonar (Cópia)

- **Menu de Ações Auxiliares (Agrupadas no Dropdown `...`)**:
  Devem estar obrigatoriamente dentro do menu dropdown:
  1. Exportar Dados (`fa-file-export`)
  2. Importar Dados (`fa-file-import`)
  3. Imprimir / Gerar PDF (`fa-print`)
  4. Enviar por E-mail (`fa-envelope`)
  5. Enviar por WhatsApp (`fa-whatsapp`)

- **Ações de Confirmação (High Contrast)**:
  1. Novo Registro (`+`)
  2. Salvar (Obrigatório o uso EXCLUSIVO do ícone de disquete `fa-save`, sem a palavra "Salvar", mantendo o padrão 34x34px)
  3. Fechar (`X`)

### Padronização de Largura (Tamanhos do Cabeçalho)
Para garantir harmonia visual e proporção perfeita entre o cabeçalho e o formulário que ele controla, o `cabecalho_mestre_arione` suporta três tamanhos padronizados através do parâmetro `tamanho`:

- **Grande (`tamanho='grande'`, Padrão)**: Largura de `100% (Expansivo)`. Destinado a formulários de página inteira e cadastros complexos (ex: Cadastro de Empresa, Gestão de Funcionários HCM, Orçamentos, Pedidos), garantindo alinhamento perfeito com os cards em telas amplas
- **Médio (`tamanho='medio'`)**: Largura máxima de `1000px`. Destinado a formulários intermediários e cadastros auxiliares de macro/micro estrutura (ex: Setores, Departamentos, Cargos)
- **Pequeno (`tamanho='pequeno'`)**: Largura máxima de `700px`. Destinado a formulários compactos, modais de atalho e cadastros rápidos (ex: Sócios, Investidores, Centro de Custos)

## Configuração Padrão do Macro `cabecalho_mestre_arione`

### Parâmetros Obrigatórios
```jinja2
{{ cabecalho_mestre_arione(
    titulo='Título do Módulo',
    subtitulo='Módulo > Submódulo > Funcionalidade',
    icone='fa-icone-especifico',
    cor_tema='#COR_TEMA',
    entidade='[nome_da_entidade]',
    func_fechar='voltarParaGrid[Modulo]()',
    form_id='form-[modulo]',
    onclick_novo='resetForm[Modulo]()',
    onclick_save='salvar[Entidade]()',
    onclick_search='focarPesquisa[Entidade]()',
    onclick_filter='abrirModalFiltrosAvancados()',
    onclick_list='alternarVisaoFormLista()',
    onclick_clonar='clonar[Entidade]Ativo()',
    onclick_export='exportar[Entidade]CSV()',
    onclick_import='abrirModalImportacao[Formato]()',
    onclick_print='imprimirRelatorio[Entidade]()',
    onclick_email='enviar[Entidade]Email()',
    onclick_whatsapp='enviar[Entidade]WhatsApp()',
    status='Status do Sistema',
    ajuda='Descrição breve da funcionalidade do módulo',
    tamanho='medio'
) }}
```

## Funções JavaScript Padrão

### 0. `arioneInit[Entidade]Sync()`
Deve ser chamada no `DOMContentLoaded` do módulo para ativar a mudança de cor automática.
```javascript
function arioneInit[Entidade]Sync() {
    arioneSyncSaveButton('form-[modulo]', 'btn-salvar-[entidade]');
}
```

### 1. `voltarParaGrid[Modulo]()`
```javascript
function voltarParaGrid[Modulo]() {
    if (typeof fecharModalGlobal === 'function') fecharModalGlobal();
    if (typeof fecharModal[Modulo] === 'function') fecharModal[Modulo]();
    if (!window.location.search.includes('aba=[modulo]')) { 
        window.location.href = "{{ url_for('[rota].abas', aba='[modulo]') }}"; 
    }
}
```

### 2. `resetForm[Modulo]()`
```javascript
function resetForm[Modulo]() {
    const form = document.getElementById('form-[modulo]');
    if (form) {
        form.reset();
        const idInput = form.querySelector('input[name="id"]');
        if (idInput) idInput.value = '';
        // Resetar campos específicos do módulo
        const primeiroCampo = form.querySelector('input:not([readonly]):not([type="hidden"])');
        if (primeiroCampo) primeiroCampo.focus();
        if (typeof arioneToast === 'function') arioneToast('✨ Formulário limpo para novo cadastro!', 'success');
    }
}
```

### 3. `salvar[Entidade]()`
```javascript
async function salvar[Entidade]() {
    const form = document.getElementById('form-[modulo]');
    const btn = document.getElementById('btn-salvar-[entidade]'); // DEVE COMBINAR COM O PARÂMETRO 'entidade' DO MACRO
    let ok = true;
    const camposFaltantes = [];

    // Validação frontend
    form.querySelectorAll('[required]').forEach(el => {
        el.classList.remove('error');
        if (!el.value.trim()) { 
            el.classList.add('error'); 
            ok = false;
            const label = el.closest('.fe-group')?.querySelector('label')?.textContent?.trim() || el.name;
            camposFaltantes.push(label);
        }
    });
    if (!ok) {
        const mensagem = `Campos obrigatórios pendentes: ${camposFaltantes.join(', ')}`;
        arioneToast(mensagem, 'warning');
        const primeiro = form.querySelector('.error');
        if (primeiro) primeiro.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }

    // Desativa botão para prevenir duplo-click
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';

    try {
        const response = await fetch(window.location.pathname + window.location.search, {
            method: 'POST',
            body: new FormData(form)
        });
        
        const result = await response.json();
        if (result.ok) {
            arioneToast('[Entidade] salva com sucesso!', 'success');
            setTimeout(() => {
                voltarParaGrid[Modulo]();
            }, 1000);
        } else {
            arioneToast(result.msg || 'Erro ao salvar. Verifique os dados.', 'danger');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-save"></i> Salvar [Entidade]';
        }
    } catch (e) {
        arioneToast('Erro crítico na persistência', 'danger');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-save"></i> Salvar [Entidade]';
    }
}
```

### 4. `focarPesquisa[Entidade]()`
```javascript
function focarPesquisa[Entidade]() {
    const input = document.getElementById('filtro-[entidade]');
    if (input) {
        input.focus();
        if (typeof arioneToast === 'function') arioneToast('🔍 Campo de pesquisa ativado', 'info');
    }
}
```

### 5. `abrirModalFiltrosAvancados()`
```javascript
function abrirModalFiltrosAvancados() {
    const modal = document.getElementById('modal-filtros-avancados');
    if (modal) {
        modal.classList.add('ativo');
        if (typeof arioneToast === 'function') arioneToast('🎛️ Filtros avançados abertos', 'info');
    } else {
        if (typeof arioneToast === 'function') arioneToast('⚠️ Módulo de filtros em desenvolvimento', 'warning');
    }
}
```

### 6. `alternarVisaoFormLista()`
```javascript
function alternarVisaoFormLista() {
    const form = document.getElementById('form-[modulo]');
    const lista = document.getElementById('lista-[entidade]');
    
    if (!form || !lista) {
        arioneToast("Nenhum container localizado", "warning");
        return;
    }
    
    if (form.style.display === 'none') {
        form.style.display = 'block';
        lista.style.display = 'none';
        arioneToast("Visualizando Formulário", "info");
    } else {
        form.style.display = 'none';
        lista.style.display = 'block';
        arioneToast("Visualizando Lista de Registros", "info");
    }
}
```

### 7. `clonar[Entidade]Ativo()`
```javascript
function clonar[Entidade]Ativo() {
    const form = document.getElementById('form-[modulo]');
    const idInput = form.querySelector('[name="id"]');
    
    if (!idInput || (idInput.value === 'new' || idInput.value === '0' || !idInput.value)) {
        if (typeof arioneToast === 'function') arioneToast("Apenas registros salvos podem ser clonados.", "info");
        return;
    }
    
    if (!confirm("🛡️ AriOne: Deseja clonar este registro para criar um novo item idêntico?")) return;
    
    // Zera o ID para forçar novo insert
    idInput.value = 'new';
    
    // Adiciona prefixo CÓPIA - ao campo de descrição/nome
    const campoDescricao = form.querySelector('[name="descricao"]') || form.querySelector('[name="nome"]') || form.querySelector('[name="razao_social"]');
    if (campoDescricao) {
        const valorAtual = campoDescricao.value.trim();
        if (!valorAtual.startsWith('CÓPIA - ')) {
            campoDescricao.value = 'CÓPIA - ' + valorAtual;
        }
    }
    
    // Limpa campos de unicidade
    const campoUnico = form.querySelector('[name="[campo_unico]"]');
    if (campoUnico) {
        campoUnico.value = '';
        campoUnico.placeholder = "DIGITE NOVO [CAMPO ÚNICO]";
        campoUnico.style.border = "2px solid var(--pri)";
        setTimeout(() => campoUnico.focus(), 100);
    }
    
    if (typeof arioneToast === 'function') {
        arioneToast("✅ Modo Clonagem Ativado! Prefixo CÓPIA - adicionado. Ajuste o [campo único] e salve como novo.", "success");
    }
}
```

### 8. `exportar[Entidade]CSV()`
```javascript
function exportar[Entidade]CSV() {
    const tabela = document.getElementById('tabela-[entidade]');
    if (!tabela) {
        if (typeof arioneToast === 'function') arioneToast('⚠️ Tabela não encontrada para exportação', 'warning');
        return;
    }
    
    let csv = [];
    const linhas = tabela.querySelectorAll('tr');
    
    linhas.forEach(linha => {
        const celulas = linha.querySelectorAll('td, th');
        const dados = [];
        celulas.forEach(celula => dados.push(celula.textContent.trim()));
        csv.push(dados.join(','));
    });
    
    const arquivoCSV = csv.join('\n');
    const blob = new Blob([arquivoCSV], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '[entidade]_export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
    
    if (typeof arioneToast === 'function') arioneToast('📦 Arquivo CSV exportado com sucesso!', 'success');
}
```

### 9. `abrirModalImportacao[Formato]()`
```javascript
function abrirModalImportacao[Formato]() {
    const modal = document.getElementById('modal-importacao-[formato]');
    if (modal) {
        modal.classList.add('ativo');
        if (typeof arioneToast === 'function') arioneToast('📥 Modal de importação aberto', 'info');
    } else {
        if (typeof arioneToast === 'function') arioneToast('⚠️ Módulo de importação em desenvolvimento', 'warning');
    }
}
```

### 10. `imprimirRelatorio[Entidade]()`
```javascript
function imprimirRelatorio[Entidade]() {
    if (typeof arioneToast === 'function') arioneToast('🖨️ Preparando relatório para impressão...', 'info');
    window.print();
}
```

### 11. `enviar[Entidade]Email()`
```javascript
function enviar[Entidade]Email() {
    const [campo] = document.querySelector('input[name="[campo]"]')?.value;
    const [identificador] = document.querySelector('input[name="[identificador]"]')?.value || '[ENTIDADE]';
    
    if (![campo]) {
        if (typeof arioneToast === 'function') arioneToast('⚠️ Informe o [campo] primeiro.', 'warning');
        return;
    }
    
    const subject = encodeURIComponent(`Contato AriOne: ${[identificador]}`);
    const body = encodeURIComponent(`Olá equipe da ${[identificador]},\n\nGostaríamos de entrar em contato referente às operações cadastradas no sistema AriOne.\n\nAtenciosamente,\nGestão AriOne`);
    window.open(`mailto:${[campo]}?subject=${subject}&body=${body}`, '_blank');
    if (typeof arioneToast === 'function') arioneToast(`📧 Abrindo cliente de e-mail para ${[campo]}...`, 'success');
}
```

### 12. `enviar[Entidade]WhatsApp()`
```javascript
function enviar[Entidade]WhatsApp() {
    let [campo] = document.querySelector('input[name="[campo]"]')?.value;
    const [identificador] = document.querySelector('input[name="[identificador]"]')?.value || '[ENTIDADE]';
    
    if (![campo]) {
        if (typeof arioneToast === 'function') arioneToast('⚠️ Informe o [campo] primeiro.', 'warning');
        return;
    }
    
    [campo] = [campo].replace(/\D/g, '');
    if ([campo].length < 10) {
        if (typeof arioneToast === 'function') arioneToast('⚠️ Número inválido.', 'warning');
        return;
    }
    if ([campo].length === 10 || [campo].length === 11) { [campo] = '55' + [campo]; }
    
    const text = encodeURIComponent(`Olá equipe da ${[identificador]}, entramos em contato através do sistema AriOne.`);
    window.open(`https://api.whatsapp.com/send?phone=${[campo]}&text=${text}`, '_blank');
    if (typeof arioneToast === 'function') arioneToast(`💬 Abrindo WhatsApp Web para ${[campo]}...`, 'success');
}
```

## Exemplo de Aplicação: Formulário de Empresa

### Configuração Atual (Precisa ser ajustada)
```jinja2
{{ cabecalho_mestre_arione(
    titulo='Cadastro de Empresa',
    subtitulo='Cadastros > Empresa > Unidade de Negócio',
    icone='fa-building',
    cor_tema='#7A255F',
    func_fechar="window.location.href='" ~ url_for('cadastros.abas', aba='empresa') ~ "'",
    form_id='form-empresa-mestre',
    onclick_novo='limparFormEmpresa()',
    onclick_save='submeterEmpresa()',
    onclick_search='focusSearchMaster()',
    onclick_filter='abrirModalFiltrosAvancados()',
    onclick_list="window.location.href='" ~ url_for('cadastros.abas', aba='empresa') ~ "'",
    onclick_clonar="arioneClonarRegistro('form-empresa-mestre')",
    onclick_export='exportarMaster()',
    onclick_import='importXMLMaster()',
    onclick_print='imprimirMaster()',
    onclick_email='arioneEnviarEmail()',
    onclick_whatsapp='arioneEnviarWhatsApp()',
    status='Ativo',
    ajuda='Gerencie os dados mestres da unidade, incluindo identificação, contatos, endereços e informações fiscais.',
    tamanho='grande'
) }}
```

### Configuração Padronizada (Sugerida)
```jinja2
{{ cabecalho_mestre_arione(
    titulo='Cadastro de Empresa',
    subtitulo='Cadastros > Empresa > Unidade de Negócio',
    icone='fa-building',
    cor_tema='#7A255F',
    func_fechar='voltarParaGridEmpresa()',
    form_id='form-empresa-mestre',
    onclick_novo='resetFormEmpresa()',
    onclick_save='salvarEmpresa()',
    onclick_search='focarPesquisaEmpresa()',
    onclick_filter='abrirModalFiltrosAvancados()',
    onclick_list='alternarVisaoFormLista()',
    onclick_clonar='clonarEmpresaAtivo()',
    onclick_export='exportarEmpresasCSV()',
    onclick_import='abrirModalImportacaoXML()',
    onclick_print='imprimirRelatorioEmpresa()',
    onclick_email='enviarEmpresaEmail()',
    onclick_whatsapp='enviarEmpresaWhatsApp()',
    status='Ativo',
    ajuda='Gerencie os dados mestres da unidade, incluindo identificação, contatos, endereços e informações fiscais.',
    tamanho='grande'
) }}
```

## Checklist de Padronização

Para cada novo formulário que usar o cabeçalho mestre:

- [ ] Usar nomes de funções seguindo o padrão: `acao[Entidade]()`
- [ ] Implementar todas as 12 funções JavaScript padrão
- [ ] Usar `voltarParaGrid[Modulo]()` em vez de URL direta
- [ ] Usar `alternarVisaoFormLista()` em vez de URL direta para lista
- [ ] Implementar validação frontend com nomes dos campos faltantes
- [ ] Adicionar feedback visual com arioneToast em todas as ações
- [ ] Usar nomes específicos para export/import (ex: `exportarEmpresasCSV`)
- [ ] Manter consistência nos nomes de parâmetros do macro

## Módulos que Precisam de Padronização

1. **Empresa** - Precisa ajustar nomes de funções e implementar funções faltantes
2. **Outros módulos** - Verificar e ajustar conforme necessário

## Notas Importantes

- A função `abrirModalFiltrosAvancados()` pode ser compartilhada entre módulos se usar IDs específicos
- A função `alternarVisaoFormLista()` requer que existam containers de formulário e lista
- Funções de export/import devem ser específicas para cada tipo de dado
- Sempre usar arioneToast para feedback visual ao usuário
- Validar campos obrigatórios antes de submeter formulário
