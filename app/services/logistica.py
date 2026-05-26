"""
🚀 AriOne Logistics Service
Gerenciamento de integrações com Correios e Melhor Envio.
"""

import requests
import json
from app.models.sistema.parametro import ParametroSistema

class LogisticaService:
    
    @staticmethod
    def get_hub_config(provider_id):
        """Busca credenciais no Hub de APIs (api_keys.json)"""
        import os
        from flask import current_app
        path = os.path.join(current_app.instance_path, 'api_keys.json')
        if os.path.exists(path):
            try:
                import json
                with open(path, 'r') as f:
                    connections = json.load(f)
                    # Pega a última conexão ativa para o provedor
                    conn = next((c for c in reversed(connections) if c['provider'] == provider_id), None)
                    if conn:
                        return conn.get('data', {})
            except: pass
        return {}

    @staticmethod
    def get_config(provedor):
        """Busca credenciais unificadas (Hub tem prioridade)"""
        hub_data = LogisticaService.get_hub_config(provedor)
        
        if provedor == 'melhorenvio':
            return {
                'token': hub_data.get('token') or ParametroSistema.get_valor('melhorenvio_token'),
                'sandbox': (hub_data.get('sandbox') or ParametroSistema.get_valor('melhorenvio_sandbox', '1')) == '1',
                'cep_origem': hub_data.get('cep_origem') or ParametroSistema.get_valor('cep_origem')
            }
        elif provedor == 'correios':
            return {
                'usuario': hub_data.get('usuario') or ParametroSistema.get_valor('correios_usuario'),
                'codigo_acesso': hub_data.get('senha') or ParametroSistema.get_valor('correios_senha'),
                'cartao_postagem': hub_data.get('cartao') or ParametroSistema.get_valor('correios_cartao'),
                'cep_origem': hub_data.get('cep_origem') or ParametroSistema.get_valor('cep_origem')
            }
        return {}

    @staticmethod
    def simular_frete(cep_destino, peso_kg, volumes=None, qtd=1, altura=None, largura=None, comprimento=None, total_volume=None, max_largura=None, max_comprimento=None):
        """Simulação unificada com inteligência de cubagem Universal"""
        resultados = []
        
        # 📊 AriOne Universal Logic: Baseado no volume real dos produtos
        if total_volume and max_largura and max_comprimento:
            largura_est = float(max_largura)
            comp_est = float(max_comprimento)
            # Altura necessária para o volume total (Safe Column)
            altura_est = float(total_volume) / (largura_est * comp_est)
        elif altura and largura and comprimento:
            # Sobrescrita manual direta
            largura_est = float(largura)
            comp_est = float(comprimento)
            altura_est = float(altura)
        else:
            # Fallback V7 (Moda Master) se não houver dados específicos
            q = float(qtd)
            largura_est = 22 + (q * 0.60)
            comp_est = 22 + (q * 0.35)
            altura_est = (q * 1.5) if q <= 10 else (15 + ((q - 10) * 0.25))
        
        # Garante limites operacionais
        largura_est = max(11, largura_est)
        comp_est = max(16, comp_est)
        altura_est = max(2, altura_est)
        
        config_me = LogisticaService.get_config('melhorenvio')
        if config_me.get('token'):
            try:
                # Limpeza rigorosa do token
                token_limpo = str(config_me.get('token', '')).strip()
                
                url = "https://sandbox.melhorenvio.com.br/api/v2/me/shipment/calculate" if config_me['sandbox'] else "https://melhorenvio.com.br/api/v2/me/shipment/calculate"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token_limpo}",
                    "User-Agent": "AriOne ERP (contato@arione.com.br)"
                }
                payload = {
                    "from": {"postal_code": str(config_me['cep_origem']).replace('-', '')},
                    "to": {"postal_code": str(cep_destino).replace('-', '')},
                    "package": {
                        "weight": float(peso_kg),
                        "width": largura_est, "height": altura_est, "length": comp_est
                    }
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    api_data = response.json()
                    if isinstance(api_data, list):
                        for opt in api_data:
                            if not opt.get('error'):
                                resultados.append({
                                    "id": f"me_{opt.get('id')}",
                                    "servico": f"{opt.get('name')} ({opt.get('company', {}).get('name', 'ME')})".upper(),
                                    "valor": float(opt.get('price', 0)),
                                    "prazo": int(opt.get('delivery_time', 0)),
                                    "provedor": "melhorenvio"
                                })
                    else:
                        print(f"⚠️ Resposta inesperada do Melhor Envio: {api_data}")
                else:
                    msg_erro = f"ERRO {response.status_code}: {response.text[:50]}"
                    print(f"❌ {msg_erro}")
                    resultados.append({
                        "id": "me_debug_error",
                        "servico": f"⚠️ MELHOR ENVIO: {msg_erro}".upper(),
                        "valor": 0,
                        "prazo": 0,
                        "provedor": "melhorenvio"
                    })
            except Exception as e:
                print(f"⚠️ Erro crítico na conexão Logística: {e}")

        if not resultados:
            # Fallback final se nada mesmo funcionar
            resultados.append({
                "id": "sim_sedex",
                "servico": "SEDEX (SIMULADO - CHEQUE O TERMINAL)",
                "valor": 28.50 + (float(peso_kg) * 4.5),
                "prazo": 3,
                "provedor": "correios"
            })
            resultados.append({
                "id": "sim_pac",
                "servico": "PAC (Simulado - Verifique o Token)",
                "valor": 18.20 + (float(peso_kg) * 2.1),
                "prazo": 8,
                "provedor": "correios"
            })

        return resultados
