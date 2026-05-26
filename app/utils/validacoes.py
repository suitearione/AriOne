# ============================================================  # 🟪 ARIONEDEV – MÓDULO: Validações
# 📂 Local: /AriOneDEV/utils/validacoes.py                      # 🌐 Utilidades reutilizáveis
# ============================================================  # ⚙️ Padrão: comentários à direita

import re  # 🧩 Regex para limpar e checar padrões

# ============================================================ # 
# Rotina para validar o CNPJ # 
# ============================================================ # 


def validar_cnpj_completo(
        cnpj: str) -> bool:  # 🔎 Valida CNPJ (com dígitos verificadores)
    cnpj = re.sub(r'\D', '', cnpj)  # 🧹 Mantém só números
    if len(cnpj) != 14:  # ⛔ Tamanho inválido
        return False  # ↩️
    if cnpj == cnpj[0] * 14:  # ⛔ Sequência repetida (111..., 000...)
        return False  # ↩️

    def calc_digito(parcial: str) -> str:  # 🧮 Calcula 1 dígito verificador
        pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]  # ⚖️ Pesos oficiais
        soma = 0  # ➕ Acumulador
        for i, ch in enumerate(parcial):  # 🔁 Percorre dígitos
            peso = pesos[i + (len(pesos) -
                              len(parcial))]  # 🎯 Peso alinhado ao tamanho
            soma += int(ch) * peso  # ➗ Produto acumulado
        resto = soma % 11  # 🔻 Resto mod 11
        return '0' if resto < 2 else str(11 - resto)  # 🧠 Regra do DV

    dv1 = calc_digito(cnpj[:12])  # 📍 Primeiro DV com 12 dígitos
    dv2 = calc_digito(cnpj[:12] + dv1)  # 📍 Segundo DV com 13 dígitos
    return cnpj[-2:] == dv1 + dv2  # ✅ Confere DVs finais (True/False)


# =============================== FIM =========================  # 📦 Pronto para importar em qualquer cadastro
