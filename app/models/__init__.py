# =============================================================================
# Caminho  : app/models/__init__.py
# Função   : Ponto central de imports de todos os models do AriOne.
# =============================================================================

# ── Cadastros ────────────────────────────────────────────────────────────────
from app.models.cadastros.empresa    import Empresa

from app.models.cadastros.socio      import (Socio, SocioEmpresa,
                                             ContaBancariaSocio,
                                             DocumentoSocio, HistoricoSocio)

from app.models.cadastros.investidor import (Investidor, InvestidorEmpresa,
                                             MovimentacaoInvestidor,
                                             ContaBancariaInvestidor,
                                             DocumentoInvestidor)

from app.models.cadastros.funcionario import Funcionario, Cargo, Setor

# ── Sistema ──────────────────────────────────────────────────────────────────
from app.models.usuario          import Usuario
from app.models.sistema.versao   import Versao
from app.models.sistema.perfil   import Perfil
from app.models.sistema.parametro import ParametroSistema
from app.models.sistema.licenca   import Licenca
from app.models.sistema.status    import StatusWorkflow

# ── Digital ─────────────────────────────────────────────────────────────────
from app.models.digital.lead import Lead
from app.models.digital.captura import Captura
from app.models.digital.automacao import Automacao
from app.models.digital.conversao import Conversao

# ── Catálogos ────────────────────────────────────────────────────────────────
from app.models.catalogos import (Marca, Categoria, Subcategoria, UnidadeMedida,
                                   Etiqueta, Insumo, Acessorio, Embalagem, MateriaPrima,
                                   Produto, ProdutoVariacao, Servico)

# ── Operações ────────────────────────────────────────────────────────────────
from app.models.operacoes.vendas import OrcamentoVenda, PedidoVenda
from app.models.operacoes.compras import OrcamentoCompra, PedidoCompra
from app.models.operacoes.producao import OrdemProducao

# ── Gestão ───────────────────────────────────────────────────────────────────
from app.models.gestao.ponto import Ponto
from app.models.gestao.centro_custo import CentroCusto
from app.models.gestao.plano_contas import PlanoContas
from app.models.gestao.patrimonio import Patrimonio
from app.models.gestao.lancamento import Lancamento, RateioLancamento
from app.models.gestao.caixa import Caixa, MovimentacaoCaixa

# ── Comercial ───────────────────────────────────────────────────────────────
from app.models.comercial.models import (Vendedor, RedeRevenda, Revendedor, 
                                        Ministerio, ParceriaMinisterial, Influenciador,
                                        TabelaPreco, TabelaPrecoItem, PerfilVenda,
                                        FormaPagamento, OperadoraFinanceira)