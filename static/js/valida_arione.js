/* ANOTAÇÃO DE BLOCO: Objeto Central de Validação AriOne (Regra 8) */
const ArioneValidador = {

    /* ANOTAÇÃO DE LINHA: Busca endereço por CEP (Regra 13) */
    busca_CEP: function(valor) {
        const cep = valor.replace(/\D/g, '');
        if (cep.length === 8) {
            fetch(`https://viacep.com.br/ws/${cep}/json/`)
                .then(res => res.json())
                .then(dados => {
                    if (!dados.erro) {
                        // Preenche os campos pelos IDs mapeados no HTML
                        document.getElementById('logradouro').value = dados.logradouro || '';
                        document.getElementById('bairro').value = dados.bairro || '';
                        document.getElementById('localidade').value = dados.localidade || '';
                        document.getElementById('uf').value = dados.uf || '';
                        document.getElementById('numero').focus();
                    }
                });
        }
    },

    /* ANOTAÇÃO DE LINHA: Validador de CNPJ (Regra 13) */
    validador_CNPJ: function(cnpj) {
        cnpj = cnpj.replace(/[^\d]+/g, '');
        if (cnpj.length !== 14 || /^(\d)\1{13}$/.test(cnpj)) return false;
        let tamanho = cnpj.length - 2, numeros = cnpj.substring(0, tamanho), digitos = cnpj.substring(tamanho);
        let soma = 0, pos = tamanho - 7;
        for (let i = tamanho; i >= 1; i--) { soma += numeros.charAt(tamanho - i) * pos--; if (pos < 2) pos = 9; }
        let resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
        if (resultado != digitos.charAt(0)) return false;
        tamanho++; numeros = cnpj.substring(0, tamanho); soma = 0; pos = tamanho - 7;
        for (let i = tamanho; i >= 1; i--) { soma += numeros.charAt(tamanho - i) * pos--; if (pos < 2) pos = 9; }
        resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
        return resultado == digitos.charAt(1);
    },

   /* ANOTAÇÃO DE LINHA: Validador de E-mail Rigoroso (Regra 13) */
validador_Email: function(email) {
    // Esta regex exige: texto + @ + texto + . + (extensão de 2 a 4 letras)
    // Aceita também o formato composto como .com.br
    const re = /^[^\s@]+@[^\s@]+\.(com|com\.br|net|org|gov|edu|me)$/i;
    return re.test(email.toLowerCase());
},

    /* ANOTAÇÃO DE LINHA: Máscara de Telefone Dinâmica (Regra 8) */
    mascara_Telefone: function(input) {
        let v = input.value.replace(/\D/g, '');
        if (v.length > 11) v = v.slice(0, 11);
        if (v.length > 10) {
            input.value = v.replace(/^(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (v.length > 5) {
            input.value = v.replace(/^(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        } else if (v.length > 2) {
            input.value = v.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
        } else {
            input.value = v.replace(/^(\d*)/, '($1$1');
        }
    },

    /* ANOTAÇÃO DE LINHA: Formata Telefone para WhatsApp (Regra 8) */
    /* Remove caracteres não numéricos e adiciona prefixo 55 se necessário */
    /* Retorno: apenas números (ex: 5585999999999) */
    formatarWhatsApp: function(telefone) {
        if (!telefone) return null;
        // Remove todos os caracteres não numéricos
        let numeros = telefone.replace(/\D/g, '');
        // Se não tiver prefixo 55, adiciona
        if (!numeros.startsWith('55')) {
            numeros = '55' + numeros;
        }
        return numeros;
    }
};

/* ANOTAÇÃO DE LINHA: Função de Compartilhamento (Independente de Usuário) */
function compartilharRegistro() {
    const nome = document.getElementsByName('nome_fantasia')[0].value || "Empresa";
    const cnpj = document.getElementById('cnpj').value;
    
    if(!cnpj) {
        alert("⚠️ Por favor, selecione ou preencha uma empresa para compartilhar.");
        return;
    }

    const mensagem = `*AriOne - Ficha Institucional*%0A*Empresa:* ${nome}%0A*CNPJ:* ${cnpj}`;
    window.open(`https://api.whatsapp.com/send?text=${mensagem}`, '_blank');
}