# =============================================================================
# Caminho  : app/models/cadastros/empresa.py
# Arquivo  : empresa.py
# Função   : Model para cadastro de empresas no AriOne.
# Descrição: Armazena dados completos de empresas: identificação, contatos,
#            endereços (faturamento, entrega, correspondência), informações
#            digitais, ciclo de vida e dados fiscais. Empresas nunca são
#            excluídas — apenas encerradas (ativa=False) para manter histórico.
# =============================================================================

from datetime import datetime
from app import db


class Empresa(db.Model):
    __tablename__ = 'empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # IDENTIFICAÇÃO
    # ═══════════════════════════════════════════════════════════════════════
    razao_social        = db.Column(db.String(200), nullable=False)
    nome_fantasia       = db.Column(db.String(200), nullable=True)
    area_atuacao_resumo = db.Column(db.String(200), nullable=True)
    setor_atividade     = db.Column(db.String(100), nullable=True)
    objeto_social       = db.Column(db.String(50), nullable=True)
    logo                = db.Column(db.String(255), nullable=True)
    
    # Documentos & Tipo
    tipo_pessoa   = db.Column(db.String(2), default='PJ')
    unidade       = db.Column(db.String(10), default='MATRIZ')
    cnpj          = db.Column(db.String(18), unique=True, nullable=True)
    cpf           = db.Column(db.String(14), unique=True, nullable=True)
    rg            = db.Column(db.String(20), nullable=True)
    ie            = db.Column(db.String(20), nullable=True)
    im            = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    profissao      = db.Column(db.String(100), nullable=True)
    pis_pasep      = db.Column(db.String(15), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # CONTATO
    # ═══════════════════════════════════════════════════════════════════════
    telefone      = db.Column(db.String(20), nullable=True)
    whatsapp      = db.Column(db.String(20), nullable=True)
    email         = db.Column(db.String(200), nullable=True)
    email_contato = db.Column(db.String(200), nullable=True)
    contato_nome  = db.Column(db.String(100), nullable=True)
    contato_tipo  = db.Column(db.String(50), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIGITAL
    # ═══════════════════════════════════════════════════════════════════════
    slug      = db.Column(db.String(100), unique=True, nullable=True)
    website   = db.Column(db.String(200), nullable=True)
    instagram = db.Column(db.String(100), nullable=True)
    facebook  = db.Column(db.String(100), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # ENDEREÇO DE FATURAMENTO
    # ═══════════════════════════════════════════════════════════════════════
    end_fat_cep         = db.Column(db.String(9), nullable=True)
    end_fat_logradouro  = db.Column(db.String(200), nullable=True)
    end_fat_numero      = db.Column(db.String(20), nullable=True)
    end_fat_complemento = db.Column(db.String(100), nullable=True)
    end_fat_bairro      = db.Column(db.String(100), nullable=True)
    end_fat_cidade      = db.Column(db.String(100), nullable=True)
    end_fat_uf          = db.Column(db.String(2), nullable=True)
    end_fat_referencia  = db.Column(db.String(200), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # ENDEREÇO DE ENTREGA
    # ═══════════════════════════════════════════════════════════════════════
    end_ent_cep         = db.Column(db.String(9), nullable=True)
    end_ent_logradouro  = db.Column(db.String(200), nullable=True)
    end_ent_numero      = db.Column(db.String(20), nullable=True)
    end_ent_complemento = db.Column(db.String(100), nullable=True)
    end_ent_bairro      = db.Column(db.String(100), nullable=True)
    end_ent_cidade      = db.Column(db.String(100), nullable=True)
    end_ent_uf          = db.Column(db.String(2), nullable=True)
    end_ent_referencia  = db.Column(db.String(200), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # ENDEREÇO DE CORRESPONDÊNCIA
    # ═══════════════════════════════════════════════════════════════════════
    end_cor_cep         = db.Column(db.String(9), nullable=True)
    end_cor_logradouro  = db.Column(db.String(200), nullable=True)
    end_cor_numero      = db.Column(db.String(20), nullable=True)
    end_cor_complemento = db.Column(db.String(100), nullable=True)
    end_cor_bairro      = db.Column(db.String(100), nullable=True)
    end_cor_cidade      = db.Column(db.String(100), nullable=True)
    end_cor_uf          = db.Column(db.String(2), nullable=True)
    end_cor_referencia  = db.Column(db.String(200), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # CICLO DE VIDA
    # ═══════════════════════════════════════════════════════════════════════
    data_abertura       = db.Column(db.Date, nullable=True)
    data_encerramento   = db.Column(db.Date, nullable=True)
    motivo_encerramento = db.Column(db.Text, nullable=True)
    ativa               = db.Column(db.Boolean, default=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # FISCAL / NF-e
    # ═══════════════════════════════════════════════════════════════════════
    regime_tributario = db.Column(db.String(50), nullable=True)
    natureza_juridica = db.Column(db.String(10), nullable=True)
    cnae_principal    = db.Column(db.String(10), nullable=True)
    cnae_secundario   = db.Column(db.String(10), nullable=True)
    retencao_irrf     = db.Column(db.String(50), nullable=True)
    declaracao_ir     = db.Column(db.String(50), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # ALOCAÇÃO ORGANIZACIONAL
    # ═══════════════════════════════════════════════════════════════════════
    setor_id         = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=True)
    departamento_id  = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=True)
    cargo_id         = db.Column(db.Integer, db.ForeignKey('cargos.id'), nullable=True)
    
    nfe_serie         = db.Column(db.String(10), nullable=True)
    nfe_ultimo_numero = db.Column(db.Integer, nullable=True)
    nfe_ambiente      = db.Column(db.String(1), nullable=True)
    danfe_formato     = db.Column(db.String(1), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # METADADOS
    # ═══════════════════════════════════════════════════════════════════════
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ═══════════════════════════════════════════════════════════════════════
    # RELACIONAMENTOS
    # ═══════════════════════════════════════════════════════════════════════
    socios       = db.relationship('SocioEmpresa', back_populates='empresa', cascade='all, delete-orphan')
    investidores = db.relationship('InvestidorEmpresa', back_populates='empresa', cascade='all, delete-orphan')

    # Relacionamentos Organizacionais
    setor        = db.relationship('Setor', foreign_keys=[setor_id])
    departamento = db.relationship('Setor', foreign_keys=[departamento_id])
    cargo        = db.relationship('Cargo', foreign_keys=[cargo_id])

    def __repr__(self):
        return f'<Empresa {self.razao_social}>'
    
    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS AUXILIARES
    # ═══════════════════════════════════════════════════════════════════════
    
    @property
    def endereco_completo_faturamento(self):
        """Retorna endereço de faturamento formatado"""
        if not self.end_fat_logradouro:
            return None
        
        partes = [self.end_fat_logradouro]
        if self.end_fat_numero:
            partes.append(f'nº {self.end_fat_numero}')
        if self.end_fat_complemento:
            partes.append(self.end_fat_complemento)
        if self.end_fat_bairro:
            partes.append(f'- {self.end_fat_bairro}')
        if self.end_fat_cidade and self.end_fat_uf:
            partes.append(f'- {self.end_fat_cidade}/{self.end_fat_uf}')
        if self.end_fat_cep:
            partes.append(f'CEP: {self.end_fat_cep}')
        
        return ', '.join(partes)
    
    @property
    def endereco_completo_entrega(self):
        """Retorna endereço de entrega formatado"""
        if not self.end_ent_logradouro:
            return None
        
        partes = [self.end_ent_logradouro]
        if self.end_ent_numero:
            partes.append(f'nº {self.end_ent_numero}')
        if self.end_ent_complemento:
            partes.append(self.end_ent_complemento)
        if self.end_ent_bairro:
            partes.append(f'- {self.end_ent_bairro}')
        if self.end_ent_cidade and self.end_ent_uf:
            partes.append(f'- {self.end_ent_cidade}/{self.end_ent_uf}')
        if self.end_ent_cep:
            partes.append(f'CEP: {self.end_ent_cep}')
        
        return ', '.join(partes)
    
    @property
    def cpf_formatado(self):
        """Retorna CPF formatado: 000.000.000-00"""
        if not self.cpf:
            return '—'
        limpo = ''.join(c for c in self.cpf if c.isdigit())
        if len(limpo) != 11:
            return self.cpf
        return f'{limpo[:3]}.{limpo[3:6]}.{limpo[6:9]}-{limpo[9:]}'

    @property
    def cnpj_formatado(self):
        """Retorna CNPJ formatado: 00.000.000/0000-00"""
        if not self.cnpj:
            return None
        # Remove caracteres não numéricos
        cnpj_limpo = ''.join(c for c in self.cnpj if c.isdigit())
        if len(cnpj_limpo) != 14:
            return self.cnpj  # Retorna como está se não tiver 14 dígitos
        # Formata
        return f'{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}'
    
    @property
    def status_label(self):
        """Retorna label do status"""
        return 'Ativa' if self.ativa else 'Encerrada'
    
    @property
    def dias_desde_abertura(self):
        """Retorna quantos dias desde a abertura"""
        if not self.data_abertura:
            return None
        from datetime import date
        return (date.today() - self.data_abertura).days
    
    @classmethod
    def get_ativas(cls):
        """Retorna apenas empresas ativas"""
        return cls.query.filter_by(ativa=True).order_by(cls.razao_social).all()
    
    @classmethod
    def get_encerradas(cls):
        """Retorna apenas empresas encerradas"""
        return cls.query.filter_by(ativa=False).order_by(cls.data_encerramento.desc()).all()
    
    @classmethod
    def buscar_por_cnpj(cls, cnpj):
        """Busca empresa por CNPJ (aceita formatado ou não)"""
        # Remove caracteres não numéricos
        cnpj_limpo = ''.join(c for c in cnpj if c.isdigit())
        return cls.query.filter(cls.cnpj.like(f'%{cnpj_limpo}%')).first()
    
    def encerrar(self, motivo=''):
        """Encerra a empresa (não exclui)"""
        from datetime import date
        self.ativa = False
        self.data_encerramento = date.today()
        if motivo:
            self.motivo_encerramento = motivo
    
    def reativar(self):
        """Reativa uma empresa encerrada"""
        self.ativa = True
        self.data_encerramento = None
        self.motivo_encerramento = None

class EmpresaContato(db.Model):
    __tablename__ = 'empresas_contatos'
    id              = db.Column(db.Integer, primary_key=True)
    empresa_id      = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    nome            = db.Column(db.String(100), nullable=False)
    cargo           = db.Column(db.String(100), nullable=True)
    whatsapp        = db.Column(db.String(20), nullable=True)
    email           = db.Column(db.String(200), nullable=True)
    setor_id        = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=True)

    empresa    = db.relationship('Empresa', backref=db.backref('contatos_lista', cascade='all, delete-orphan'))
    setor      = db.relationship('Setor', foreign_keys=[setor_id])
    departamento = db.relationship('Setor', foreign_keys=[departamento_id])

    def __repr__(self):
        return f'<EmpresaContato {self.nome} - {self.cargo}>'