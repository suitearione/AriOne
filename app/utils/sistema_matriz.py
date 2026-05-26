# app/utils/sistema_matriz.py
import os

"""
MOTOR DE AUTO-DESCOBERTA ARIONE (DYNAMIC SOURCE OF TRUTH)
Este módulo escaneia a pasta templates/ para gerar a hierarquia do sistema automaticamente.
"""

def gerar_matriz_automatica():
    # Caminho base dos templates
    base_path = os.path.join(os.getcwd(), 'templates')
    
    # Módulos principais (Pastas na raiz de templates)
    modulos_alvo = [
        "cadastros", "operacoes", "financeiro", "gestao", 
        "fiscal", "patrimonio", "digital", "sistema"
    ]
    
    matriz = {}
    
    for mod in modulos_alvo:
        mod_path = os.path.join(base_path, mod, 'cards')
        if not os.path.exists(mod_path):
            continue
            
        mod_label = mod.upper()
        if mod_label == "OPERACOES": mod_label = "OPERAÇÕES"
        if mod_label == "GESTAO": mod_label = "GESTÃO"
        if mod_label == "PATRIMONIO": mod_label = "PATRIMÔNIO"
            
        matriz[mod_label] = {}
        
        # 1. Escaneia arquivos soltos direto na pasta 'cards' (Categoria Geral do Módulo)
        cards_diretos = []
        for f in os.listdir(mod_path):
            if f.startswith('form_') and f.endswith('.html') and 'gateway' not in f.lower():
                # 🛡️ FILTRO DE INTEGRIDADE: Ignora abas, fragmentos e componentes técnicos
                ignorar = ['_aba', '_base', '_part', '_frag', '_comp', 'rel_']
                if any(x in f.lower() for x in ignorar):
                    continue
                    
                card_name = f.replace('form_', '').replace('.html', '').replace('_', ' ').title()
                # Remove prefixos redundantes (ex: 'Financeiro Receitas' -> 'Receitas')
                card_name = card_name.replace(mod_label.title(), '').strip()
                if card_name not in cards_diretos:
                    cards_diretos.append(card_name)
        
        if cards_diretos:
            matriz[mod_label][mod_label.title()] = sorted(cards_diretos)

        # 2. Escaneia subpastas (Produtos/Categorias)
        try:
            subpastas = [d for d in os.listdir(mod_path) if os.path.isdir(os.path.join(mod_path, d))]
            for sub in subpastas:
                prod_label = sub.replace('_', ' ').title()
                # Ajustes de nomes conhecidos
                if sub == "hcm": prod_label = "Pessoas (HCM)"
                if sub == "catalogos": prod_label = "Catálogos"
                if sub == "parametros": prod_label = "Parâmetros"
                
                sub_path = os.path.join(mod_path, sub)
                
                # Escaneia arquivos dentro da subpasta
                cards_sub = []
                for f in os.listdir(sub_path):
                    if f.startswith('form_') and f.endswith('.html') and 'gateway' not in f.lower():
                        # 🛡️ FILTRO DE INTEGRIDADE: Ignora abas, fragmentos e componentes técnicos
                        ignorar = ['_aba', '_base', '_part', '_frag', '_comp', 'rel_']
                        if any(x in f.lower() for x in ignorar):
                            continue
                            
                        card_name = f.replace('form_', '').replace('.html', '').replace('_', ' ').title()
                        if card_name not in cards_sub:
                            cards_sub.append(card_name)
                
                if cards_sub:
                    matriz[mod_label][prod_label] = sorted(cards_sub)
        except:
            pass
            
    return matriz

# Mantém a variável para compatibilidade, mas agora ela é dinâmica
SISTEMA_MATRIZ = gerar_matriz_automatica()
