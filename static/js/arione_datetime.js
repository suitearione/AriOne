/* ============================================================
   🕒 ARIONE – BIBLIOTECA DE DATA E HORA GLOBAL
   ------------------------------------------------------------
   ▪️ Função: Atualiza e formata a data e hora no padrão pt-BR.
   ▪️ Uso: Incluída em qualquer tela do sistema AriOne.
   ▪️ Chamada: chamarAriOneDataHora('idDoElemento');
   ▪️ Atualiza automaticamente a cada minuto.
   ============================================================ */

function chamarAriOneDataHora(elementId) {
    const atualizarDataHora = () => {
        const agora = new Date();
        const opcoes = { 
            weekday: 'long', 
            day: '2-digit', 
            month: 'long', 
            year: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit'
        };
        document.getElementById(elementId).textContent = 
            agora.toLocaleDateString('pt-BR', opcoes);
    };
    atualizarDataHora();
    setInterval(atualizarDataHora, 60000); // atualiza a cada 1 min
}
