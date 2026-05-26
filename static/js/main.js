/* ============================================================
    SCRIPT PRINCIPAL (MAIN.JS)
   ------------------------------------------------------------
   ▪️ Função: centraliza scripts da interface AriOne.
   ▪️ Módulo ativo: Data automática na barra superior.
   ▪️ Local de execução: carregado no final do base.html.
   ============================================================ */

/* ============================================================
   🧩 MÓDULO 01 – DATA AUTOMÁTICA NA BARRA SUPERIOR
   ============================================================ */
document.addEventListener("DOMContentLoaded", function() {
  const dataAtual = new Date();
  const opcoes = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
  const dataFormatada = dataAtual.toLocaleDateString('pt-BR', opcoes);
  const dataElemento = document.getElementById('dataPrincipal');
  if (dataElemento) {
    dataElemento.textContent =
      dataFormatada.charAt(0).toUpperCase() + dataFormatada.slice(1);
  }
});

/* ============================================================
   ⚙️ LOGO DINÂMICA NO MENU LATERAL
   ------------------------------------------------------------
   ▪️ Permite selecionar um arquivo PNG local.
   ▪️ Exibe automaticamente a imagem no topo do menu.
   ============================================================ */

document.addEventListener("DOMContentLoaded", function() {
  const input = document.getElementById('menuLogoInput');
  const preview = document.getElementById('menuLogoPreview');
  const container = document.getElementById('menuLogoContainer');

  if (input && preview && container) {
    preview.addEventListener('click', () => input.click());
    input.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file && file.type === 'image/png') {
        const reader = new FileReader();
        reader.onload = (ev) => (preview.src = ev.target.result);
        reader.readAsDataURL(file);
      }
    });
  }
});

// =======================================================
// ARIONEDEV: Lógica de Relógio em Tempo Real e Locale PT-BR
// =======================================================

// Função para formatar a data e hora em Português do Brasil
function formatarDataHora() {
    const agora = new Date();

    // Configurações de formatação nativa do navegador para PT-BR
    const opcoesData = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    const opcoesHora = { hour: '2-digit', minute: '2-digit' };

    // Formata a data (Ex: segunda-feira, 8 de dezembro de 2025)
    let dataExtenso = agora.toLocaleDateString('pt-BR', opcoesData);

    // Capitaliza a primeira letra do dia da semana para o padrão AriOne
    dataExtenso = dataExtenso.charAt(0).toUpperCase() + dataExtenso.slice(1);

    // Formata a hora (Ex: 12:10)
    const horaSimples = agora.toLocaleTimeString('pt-BR', opcoesHora);

    return `${dataExtenso}, ${horaSimples}`;
}

// Função para atualizar o relógio no HTML
function atualizarRelogio() {
    const elemento = document.getElementById('current-datetime');
    if (elemento) {
        elemento.textContent = formatarDataHora();
    }
}

// 1. Atualiza a hora imediatamente ao carregar a página
atualizarRelogio();

// 2. Define um intervalo para atualizar a cada 1000 milissegundos (1 segundo)
// Isso faz o relógio "ticar" em tempo real
setInterval(atualizarRelogio, 1000); 

// (Mantenha o restante do seu código JavaScript aqui, se houver)