# =============================================================================
# Caminho  : app/utils/progress.py
# Função   : Controle de progresso AriOne (Sincronizado com Contagem Real: 158) - v1.05
# =============================================================================

def get_standardization_progress():
    """Retorna o status simplificado para barras de progresso rápidas"""
    summary = get_ari_progress_summary()
    return summary

def get_matrix_progress():
    """
    Retorna a estrutura completa sincronizada com a contagem manual do usuário (156 cards).
    """
    matrix = {
        'CADASTROS': {
            'icon': 'fas fa-folder-open', 'color': '#34495E',
            'setores': {
                'Pessoas / Entidades': {
                    'cards': {
                        'Clientes': {'iniciado': 1, 'pronto': 1}, 'Fornecedores': {'iniciado': 1, 'pronto': 0}, 
                        'Funcionários': {'iniciado': 1, 'pronto': 1}, 'Transportadoras': {'iniciado': 1, 'pronto': 0}, 
                        'Vendedores': {'iniciado': 1, 'pronto': 0}, 'Contatos': {'iniciado': 1, 'pronto': 0},
                        'Sócios': {'iniciado': 0, 'pronto': 0}, 'Acionistas': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Comercial': {
                    'cards': {
                        'Canais Venda': {'iniciado': 1, 'pronto': 0}, 'Regiões': {'iniciado': 0, 'pronto': 0}, 
                        'Cond. Pagto': {'iniciado': 1, 'pronto': 0}, 'Formas Pagto': {'iniciado': 1, 'pronto': 0},
                        'Tabelas Preço': {'iniciado': 1, 'pronto': 0}, 'Comissões': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Catálogos / Produtos': {
                    'cards': {
                        'Produtos': {'iniciado': 1, 'pronto': 0}, 'Categorias': {'iniciado': 1, 'pronto': 0}, 
                        'Marcas': {'iniciado': 1, 'pronto': 0}, 'Serviços': {'iniciado': 0, 'pronto': 0},
                        'Unidades Medida': {'iniciado': 1, 'pronto': 1}, 'Atributos': {'iniciado': 0, 'pronto': 0},
                        'Kits / Combos': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Empresa / Parâmetros': {
                    'cards': {
                        'Minha Empresa': {'iniciado': 1, 'pronto': 1}, 'Unidades': {'iniciado': 1, 'pronto': 0}, 
                        'Departamentos': {'iniciado': 1, 'pronto': 1}, 'Cargos': {'iniciado': 1, 'pronto': 1}, 
                        'Centro Custos': {'iniciado': 1, 'pronto': 1}, 'Config. Gerais': {'iniciado': 1, 'pronto': 0},
                        'Status do Sistema': {'iniciado': 1, 'pronto': 1}, 'Logradouros': {'iniciado': 0, 'pronto': 0},
                        'Comercial': {'iniciado': 1, 'pronto': 1}
                    }
                }
            }
        },
        'OPERAÇÕES': {
            'icon': 'fas fa-boxes-stacked', 'color': '#E67E22',
            'setores': {
                'Compras': {
                    'cards': {
                        'Pedido Compra': {'iniciado': 1, 'pronto': 0}, 'Cotações': {'iniciado': 0, 'pronto': 0}, 
                        'Solicitações': {'iniciado': 1, 'pronto': 0}, 'Entrada NF': {'iniciado': 1, 'pronto': 0},
                        'Ordens Serviço': {'iniciado': 1, 'pronto': 0}, 'Fornecedores Homolog.': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Estoque': {
                    'cards': {
                        'Saldos': {'iniciado': 1, 'pronto': 0}, 'Movimentação': {'iniciado': 1, 'pronto': 0}, 
                        'Inventário': {'iniciado': 0, 'pronto': 0}, 'Kardex': {'iniciado': 1, 'pronto': 0},
                        'Lotes / Validade': {'iniciado': 1, 'pronto': 0}, 'Endereçamento': {'iniciado': 0, 'pronto': 0},
                        'Transferências': {'iniciado': 1, 'pronto': 0}
                    }
                },
                'Vendas / Comercial': {
                    'cards': {
                        'Orçamentos': {'iniciado': 1, 'pronto': 0}, 'Pedidos': {'iniciado': 1, 'pronto': 0}, 
                        'Devoluções': {'iniciado': 0, 'pronto': 0}, 'Contratos': {'iniciado': 1, 'pronto': 0},
                        'CRM Vendas': {'iniciado': 1, 'pronto': 0}, 'Pós-Venda': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Produção / Indústria': {
                    'cards': {
                        'Ordens Prod.': {'iniciado': 0, 'pronto': 0}, 'Fichas Técnicas': {'iniciado': 0, 'pronto': 0}, 
                        'Apontamentos': {'iniciado': 0, 'pronto': 0}, 'Plano PCA': {'iniciado': 0, 'pronto': 0},
                        'Insumos': {'iniciado': 0, 'pronto': 0}, 'Qualidade': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Logística / Expedição': {
                    'cards': {
                        'Romaneios': {'iniciado': 0, 'pronto': 0}, 'Separação': {'iniciado': 0, 'pronto': 0}, 
                        'Packing List': {'iniciado': 0, 'pronto': 0}, 'Rastreio': {'iniciado': 0, 'pronto': 0},
                        'Fretes': {'iniciado': 0, 'pronto': 0}, 'Etiquetas': {'iniciado': 1, 'pronto': 0},
                        'Cargas': {'iniciado': 0, 'pronto': 0}
                    }
                }
            }
        },
        'FINANCEIRO': {
            'icon': 'fas fa-hand-holding-dollar', 'color': '#27AE60',
            'setores': {
                'Contas': {
                    'cards': {
                        'Receber': {'iniciado': 1, 'pronto': 0}, 'Pagar': {'iniciado': 1, 'pronto': 0}, 
                        'Relatórios': {'iniciado': 0, 'pronto': 0}, 'Baixas': {'iniciado': 1, 'pronto': 0}
                    }
                },
                'Bancos': {
                    'cards': {
                        'Contas Bancárias': {'iniciado': 1, 'pronto': 1}, 'Extratos': {'iniciado': 1, 'pronto': 0}, 
                        'Conciliação': {'iniciado': 0, 'pronto': 0}, 'Tarifas': {'iniciado': 1, 'pronto': 0}
                    }
                },
                'Caixas / Fluxo': {
                    'cards': {
                        'Fluxo Caixa': {'iniciado': 1, 'pronto': 0}, 'PDV': {'iniciado': 1, 'pronto': 1}, 
                        'Fechamento': {'iniciado': 1, 'pronto': 0}, 'Suprimentos': {'iniciado': 1, 'pronto': 0}
                    }
                },
                'Gerencial': {
                    'cards': {
                        'DRE': {'iniciado': 1, 'pronto': 1}, 'Plano Contas': {'iniciado': 1, 'pronto': 1}, 
                        'Orçamentos': {'iniciado': 0, 'pronto': 0}, 'BI Financeiro': {'iniciado': 1, 'pronto': 1}
                    }
                }
            }
        },
        'GESTÃO': {
            'icon': 'fas fa-chart-line', 'color': '#8e44ad',
            'setores': {
                'RH / Pessoal': {
                    'cards': {
                        'Recrutas': {'iniciado': 1, 'pronto': 0}, 'Treinamentos': {'iniciado': 0, 'pronto': 0}, 
                        'Avaliação': {'iniciado': 0, 'pronto': 0}, 'Pontos': {'iniciado': 1, 'pronto': 0},
                        'Férias': {'iniciado': 1, 'pronto': 0}, 'Holerites': {'iniciado': 1, 'pronto': 0}
                    }
                },
                'Marketing': {
                    'cards': {
                        'Campanhas': {'iniciado': 0, 'pronto': 0}, 'Leads': {'iniciado': 1, 'pronto': 0}, 
                        'CRM': {'iniciado': 1, 'pronto': 0}, 'Redes Sociais': {'iniciado': 0, 'pronto': 0},
                        'Mídias': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Estratégico': {
                    'cards': {
                        'Executivo': {'iniciado': 1, 'pronto': 1}, 'Operacional': {'iniciado': 1, 'pronto': 0}, 
                        'Metas': {'iniciado': 1, 'pronto': 0}, 'Lucratividade': {'iniciado': 1, 'pronto': 1},
                        'Performance': {'iniciado': 1, 'pronto': 1}, 'BI Geral': {'iniciado': 1, 'pronto': 1}
                    }
                }
            }
        },
        'FISCAL': {
            'icon': 'fas fa-file-invoice-dollar', 'color': '#d35400',
            'setores': {
                'Escrituração': {
                    'cards': {
                        'Entradas': {'iniciado': 1, 'pronto': 0}, 'Saídas': {'iniciado': 1, 'pronto': 0}, 
                        'Serviços': {'iniciado': 1, 'pronto': 1}
                    }
                },
                'Tributação': {
                    'cards': {
                        'Regras ICMS': {'iniciado': 0, 'pronto': 0}, 'CFOP': {'iniciado': 1, 'pronto': 1}, 
                        'NCM': {'iniciado': 1, 'pronto': 1}
                    }
                },
                'Governança': {
                    'cards': {
                        'SPED': {'iniciado': 0, 'pronto': 0}, 'Sintegra': {'iniciado': 0, 'pronto': 0}, 
                        'Contabilidade': {'iniciado': 1, 'pronto': 0}
                    }
                }
            }
        },
        'PATRIMÔNIO': {
            'icon': 'fas fa-building', 'color': '#2C3E50',
            'setores': {
                'Imóveis': {
                    'cards': {
                        'Apartamentos': {'iniciado': 0, 'pronto': 0}, 'Casas': {'iniciado': 0, 'pronto': 0}, 
                        'Galpões': {'iniciado': 0, 'pronto': 0}, 'Terrenos': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Máquinas': {
                    'cards': {
                        'Industriais': {'iniciado': 1, 'pronto': 1}, 'Agrícolas': {'iniciado': 0, 'pronto': 0},
                        'Manutenção': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Equipamentos': {
                    'cards': {
                        'Informática': {'iniciado': 1, 'pronto': 1}, 'Escritórios': {'iniciado': 0, 'pronto': 0},
                        'Móveis': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Veículos': {
                    'cards': {
                        'Passeios': {'iniciado': 1, 'pronto': 0}, 'Utilitários': {'iniciado': 0, 'pronto': 0}, 
                        'Motos': {'iniciado': 0, 'pronto': 0}, 'Seguros': {'iniciado': 1, 'pronto': 0}
                    }
                },
                'Softwares': {
                    'cards': {
                        'Licenças': {'iniciado': 1, 'pronto': 1}, 'Sistemas': {'iniciado': 1, 'pronto': 1},
                        'Subscrições': {'iniciado': 0, 'pronto': 0}
                    }
                }
            }
        },
        'DIGITAL': {
            'icon': 'fas fa-cloud-arrow-up', 'color': '#16a085',
            'setores': {
                'One Products': {
                    'cards': {
                        'LinkOne': {'iniciado': 1, 'pronto': 1}, 'LeadOne': {'iniciado': 1, 'pronto': 1}, 
                        'SiteOne': {'iniciado': 1, 'pronto': 1}, 'ChatOne': {'iniciado': 1, 'pronto': 1}, 
                        'ShopOne': {'iniciado': 1, 'pronto': 0}, 'MetricsOne': {'iniciado': 1, 'pronto': 0},
                        'MailOne': {'iniciado': 1, 'pronto': 0}, 'PayOne': {'iniciado': 1, 'pronto': 0}
                    }
                },
                'Infraestrutura': {
                    'cards': {
                        'Cloud API': {'iniciado': 1, 'pronto': 1}, 'Storage': {'iniciado': 1, 'pronto': 1},
                        'Backup 321': {'iniciado': 1, 'pronto': 1}, 'Gateways': {'iniciado': 1, 'pronto': 1},
                        'SSL / HTTPS': {'iniciado': 1, 'pronto': 1}, 'Websites': {'iniciado': 1, 'pronto': 1},
                        'Domínios': {'iniciado': 1, 'pronto': 1}, 'DNS': {'iniciado': 1, 'pronto': 1}
                    }
                },
                'Integrações': {
                    'cards': {
                        'Marketplaces': {'iniciado': 1, 'pronto': 0}, 'ERP Sync': {'iniciado': 1, 'pronto': 0},
                        'Webhooks': {'iniciado': 1, 'pronto': 0}, 'Logistica API': {'iniciado': 1, 'pronto': 0},
                        'Bancos API': {'iniciado': 1, 'pronto': 0}, 'Whatsapp API': {'iniciado': 1, 'pronto': 0},
                        'Zapier / Sync': {'iniciado': 1, 'pronto': 0}
                    }
                }
            }
        },
        'SISTEMA': {
            'icon': 'fas fa-gears', 'color': '#7A255F',
            'setores': {
                'Administração': {
                    'cards': {
                        'Usuários': {'iniciado': 1, 'pronto': 1}, 'Empresas': {'iniciado': 1, 'pronto': 1}, 
                        'Perfis': {'iniciado': 1, 'pronto': 1}, 'Sessões': {'iniciado': 1, 'pronto': 1}
                    }
                },
                'Controles': {
                    'cards': {
                        'Conexões': {'iniciado': 1, 'pronto': 0}, 'Armazenamento': {'iniciado': 1, 'pronto': 0}, 
                        'Auditoria': {'iniciado': 1, 'pronto': 1}, 'Versões': {'iniciado': 1, 'pronto': 1}, 
                        'Segurança': {'iniciado': 1, 'pronto': 1}, 'Progresso DEV': {'iniciado': 1, 'pronto': 1},
                        'Logs Erro': {'iniciado': 1, 'pronto': 0}, 'Config Mail': {'iniciado': 1, 'pronto': 0},
                        'Limpeza Cache': {'iniciado': 0, 'pronto': 0}
                    }
                },
                'Sobre AriOne': {
                    'cards': {
                        'Institucional': {'iniciado': 1, 'pronto': 1}, 
                        'Roadmap': {'iniciado': 1, 'pronto': 0}, 
                        'Créditos': {'iniciado': 1, 'pronto': 1},
                        'Hub de Licenciamento': {'iniciado': 1, 'pronto': 1}
                    }
                }
            }
        }
    }
    return matrix

def get_ari_progress_summary():
    """Calcula o resumo consolidado de todo o sistema Arione"""
    matrix = get_matrix_progress()
    total = 0
    iniciados = 0
    prontos = 0
    for modulo_info in matrix.values():
        for setor_info in modulo_info.get('setores', {}).values():
            for card_status in setor_info.get('cards', {}).values():
                total += 1
                if card_status.get('iniciado'): iniciados += 1
                if card_status.get('pronto'): prontos += 1
                
    return {
        'total': total,
        'iniciados': iniciados,
        'prontos': prontos,
        'percent_prontos': round((prontos / total) * 100) if total > 0 else 0,
        'percent_iniciados': round((iniciados / total) * 100) if total > 0 else 0
    }

def is_ari_dev():
    from flask import current_app
    return current_app.config.get('AMBIENTE') == 'Desenvolvimento'
