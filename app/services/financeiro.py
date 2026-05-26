# =============================================================================
# Caminho  : app/services/financeiro.py
# Arquivo  : financeiro.py
# Função   : Lógica de Negócio para o Módulo Financeiro (Depreciação, Fechamentos)
# =============================================================================

from app.extensions import db
from app.models.gestao.patrimonio import Patrimonio
from app.models.gestao.lancamento import Lancamento
from app.models.gestao.plano_contas import PlanoContas
from datetime import datetime
import calendar

class FinanceiroService:
    
    @staticmethod
    def processar_depreciacao_mensal(empresa_id, mes, ano, usuario_id):
        """
        Executa a depreciação de todos os bens ativos da empresa para o mês/ano informado.
        Gera um lançamento de despesa de depreciação para cada bem.
        """
        data_competencia = datetime(ano, mes, 1)
        # Último dia do mês para o vencimento/pagamento (ajuste contábil)
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        data_fechamento = datetime(ano, mes, ultimo_dia)
        
        # 1. Busca todos os bens ativos que ainda não foram totalmente depreciados
        bens = Patrimonio.query.filter(
            Patrimonio.empresa_id == empresa_id,
            Patrimonio.status == 'ATIVO',
            Patrimonio.depreciacao_acumulada < (Patrimonio.valor_aquisicao - Patrimonio.valor_residual)
        ).all()
        
        processados = 0
        total_depreciado = 0
        
        # 2. Busca a conta de despesa de depreciação no plano de contas (Padronizada: 4.2.050)
        # TODO: Tornar este código de conta configurável nos parâmetros do sistema
        conta_despesa = PlanoContas.query.filter_by(
            empresa_id=empresa_id, 
            codigo='4.2.050'
        ).first()
        
        if not conta_despesa:
            return {"success": False, "error": "Conta de despesa de depreciação (4.2.050) não encontrada no Plano de Contas."}

        for bem in bens:
            # Verifica se já houve depreciação para este bem neste mês (Anti-duplicidade)
            ja_depreciado = Lancamento.query.filter_by(
                patrimonio_id=bem.id,
                data_competencia=data_competencia
            ).first()
            
            if ja_depreciado:
                continue
            
            # Cálculo: (Valor Aquisição - Valor Residual) / Vida Útil
            valor_mensal = (bem.valor_aquisicao - bem.valor_residual) / bem.vida_util_meses
            
            # Garante que não deprecie mais do que o valor restante
            restante = bem.valor_aquisicao - bem.valor_residual - bem.depreciacao_acumulada
            valor_a_lancar = min(valor_mensal, restante)
            
            if valor_a_lancar <= 0:
                continue
                
            # 3. Gera o Lançamento Financeiro (Ajuste de Resultado)
            novo_lancamento = Lancamento(
                empresa_id=empresa_id,
                usuario_id=usuario_id,
                plano_contas_id=conta_despesa.id,
                patrimonio_id=bem.id,
                descricao=f"DEPRECIAÇÃO MENSAL REF. {bem.descricao} ({mes}/{ano})",
                valor=valor_a_lancar,
                data_vencimento=data_fechamento,
                data_pagamento=data_fechamento,
                data_competencia=data_competencia,
                tipo='DESPESA',
                status='PAGO', # Lançamento de ajuste contábil já nasce liquidado
                observacoes=f"Processamento automático de depreciação via AriOne Financeiro."
            )
            
            # 4. Atualiza o valor acumulado no bem
            bem.depreciacao_acumulada += valor_a_lancar
            
            db.session.add(novo_lancamento)
            processados += 1
            total_depreciado += valor_a_lancar
            
        try:
            db.session.commit()
            return {
                "success": True, 
                "message": f"Processamento concluído: {processados} bens depreciados.",
                "total": total_depreciado
            }
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
