import sqlite3
import os

db_path = r'c:\AriOneDEV\instance\arione.db'
report_path = r'c:\AriOneDEV\db_report.txt'

def force_fix():
    if not os.path.exists(db_path):
        with open(report_path, 'w') as f: f.write(f"Erro: Banco nao encontrado em {db_path}")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Get current columns
    c.execute("PRAGMA table_info(funcionarios)")
    existing = [col[1] for col in c.fetchall()]
    
    needed = [
        ('rg_orgao','TEXT'),('rg_data_emissao','DATE'),('pis_pasep','TEXT'),
        ('nome_mae','TEXT'),('nome_pai','TEXT'),('titulo_eleitor','TEXT'),
        ('reservista','TEXT'),('email_pessoal','TEXT'),('email_corporativo','TEXT'),
        ('whatsapp','TEXT'),('gestor_id','INTEGER'),('nivel_hierarquico','TEXT'),
        ('turno','TEXT'),('regime_escala','TEXT'),('ponto_tolerancia','INTEGER DEFAULT 5'),
        ('unidade_negocio','TEXT'),('aso_data','DATE'),('aso_validade','DATE'),
        ('epi_entregues','TEXT'),('tipo_sanguineo','TEXT'),('alergias','TEXT'),
        ('tipo_conta','TEXT'),('foto','TEXT'),('path_documentos','TEXT')
    ]
    
    report = []
    report.append(f"Existentes: {existing}\n")
    
    for n, t in needed:
        if n not in existing:
            try:
                c.execute(f"ALTER TABLE funcionarios ADD COLUMN {n} {t}")
                report.append(f"SUCESSO: Coluna {n} adicionada.\n")
            except Exception as e:
                report.append(f"FALHA: Coluna {n} - {e}\n")
        else:
            report.append(f"OK: Coluna {n} já existe.\n")
            
    conn.commit()
    conn.close()
    
    with open(report_path, 'w') as f:
        f.writelines(report)

if __name__ == '__main__':
    force_fix()
