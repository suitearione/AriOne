# =============================================================================
# Caminho  : app/utils/backup_manager.py
# Arquivo  : backup_manager.py
# Função   : Gerenciador de Backups e Snapshots de Segurança AriOne.
# Descrição: Implementa a estratégia 3-2-1, compressão, verificação de 
#            integridade e metadados para backups seguros.
# =============================================================================

import os
import shutil
import json
import hashlib
import zipfile
from datetime import datetime
from flask import current_app

class BackupManager:
    """Gerencia a criação, listagem e integridade de backups do sistema."""
    
    # Rastreamento de Status Global (Singleton-like behavior para monitoramento UI)
    _status = {
        'running': False,
        'last_success': None,
        'message': 'Pronto',
        'progress': 0
    }

    @classmethod
    def get_global_status(cls):
        return cls._status

    def __init__(self):
        self.backup_dir = os.path.join(current_app.instance_path, 'backups')
        self.secret_key = current_app.config.get('SECRET_KEY', 'arione_default_backup_key')
        os.makedirs(self.backup_dir, exist_ok=True)

    def _generate_checksum(self, file_path):
        """Gera o hash SHA256 de um arquivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def create_snapshot(self, scope='db', note='', custom_paths=None, custom_dest=None):
        """
        Cria um snapshot compactado e seguro.
        Escopos: 'db' (Banco), 'media' (Uploads), 'full' (Ambos), 'custom' (Pastas específicas)
        custom_dest: Caminho customizado para salvar o backup (local ou rede)
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        snapshot_name = f"arione_snapshot_{scope}_{timestamp}"
        zip_filename = f"{snapshot_name}.zip"

        # Usa destino customizado se fornecido, senão usa diretório padrão
        if custom_dest:
            # Cria diretório de destino se não existir
            os.makedirs(custom_dest, exist_ok=True)
            zip_path = os.path.join(custom_dest, zip_filename)
        else:
            zip_path = os.path.join(self.backup_dir, zip_filename)

        # Caminhos base
        db_path = os.path.join(current_app.instance_path, 'arione.db')
        static_folder = current_app.static_folder

        try:
            BackupManager._status['running'] = True
            BackupManager._status['message'] = f'Criando Snapshot [{scope}]...'
            BackupManager._status['progress'] = 10

            print(f"🛡️ AriOne Security: Iniciando Snapshot [{scope}]...")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                metadata = {
                    'created_at': datetime.now().isoformat(),
                    'scope': scope,
                    'note': note,
                    'encryption': 'None (SHA256 Integrity Only)',
                    'files': []
                }

                # 1. Backup do Banco de Dados
                if scope in ['db', 'full'] and os.path.exists(db_path):
                    db_checksum = self._generate_checksum(db_path)
                    zipf.write(db_path, arcname='arione.db')
                    metadata['files'].append({'name': 'arione.db', 'type': 'database', 'checksum': db_checksum})

                # 2. Backup de Mídias (Lógica Granular)
                paths_to_include = []
                if scope == 'full':
                    paths_to_include.append(os.path.join(static_folder, 'uploads'))
                elif scope == 'media' or scope == 'custom':
                    if custom_paths:
                        for p in custom_paths:
                            full_p = os.path.join(static_folder, p)
                            if os.path.exists(full_p): paths_to_include.append(full_p)
                    else:
                        paths_to_include.append(os.path.join(static_folder, 'uploads'))

                for base_path in paths_to_include:
                    for root, dirs, files in os.walk(base_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, static_folder)
                            zipf.write(file_path, arcname=arcname)
                    
                    metadata['files'].append({
                        'path': os.path.relpath(base_path, static_folder),
                        'type': 'media_directory'
                    })

                # 3. Inclusão de Metadados
                zipf.writestr('metadata.json', json.dumps(metadata, indent=4))

            # Gera hash externo para validação rápida do pacote
            pkg_checksum = self._generate_checksum(zip_path)
            
            # ✅ PADRÃO OURO: Criptografia Opcional
            try:
                from cryptography.fernet import Fernet
                import base64
                # Deriva uma chave de 32 bytes do SECRET_KEY
                key = base64.urlsafe_b64encode(hashlib.sha256(self.secret_key.encode()).digest())
                f = Fernet(key)
                
                with open(zip_path, 'rb') as original:
                    encrypted_data = f.encrypt(original.read())
                
                with open(zip_path, 'wb') as encrypted_file:
                    encrypted_file.write(encrypted_data)
                
                metadata['encryption'] = 'AES-256 (Fernet)'
                print("🔒 AriOne Security: Snapshot criptografado com sucesso.")
            except ImportError:
                print("⚠️ AriOne Security: 'cryptography' não instalado. Snapshot salvo sem cifragem (Apenas SHA256).")

            with open(f"{zip_path}.sha256", "w") as f:
                f.write(pkg_checksum)

            BackupManager._status['running'] = False
            BackupManager._status['last_success'] = datetime.now().isoformat()
            BackupManager._status['message'] = 'Sucesso'
            BackupManager._status['progress'] = 100

            return {
                'success': True,
                'filename': zip_filename,
                'path': zip_path,
                'size': os.path.getsize(zip_path),
                'checksum': pkg_checksum
            }

        except Exception as e:
            BackupManager._status['running'] = False
            BackupManager._status['message'] = f'Erro: {str(e)}'
            BackupManager._status['progress'] = 0
            if os.path.exists(zip_path):
                os.remove(zip_path)
            return {'success': False, 'error': str(e)}

    def sync_to_cloud(self, file_path, provider_type='aws_s3', provider_id=None):
        """Sincroniza um snapshot local com a nuvem (AWS S3, Google Drive, etc)."""
        config_path = os.path.join(current_app.instance_path, 'api_keys.json')
        if not os.path.exists(config_path):
            return {'success': False, 'error': 'Configurações de nuvem não encontradas no Hub.'}
        
        try:
            with open(config_path, 'r') as f:
                connections = json.load(f)
            
            # Filtra conexão pelo tipo e ID (se fornecido)
            conn = None
            for c in connections:
                if c['provider'] == provider_type and (not provider_id or c['id'] == provider_id):
                    conn = c
                    break
            
            if not conn:
                return {'success': False, 'error': f'Nenhuma conexão "{provider_type}" ativa encontrada no Hub.'}
            
            if provider_type == 'aws_s3':
                return self._sync_aws(file_path, conn)
            elif provider_type == 'gdrive':
                return self._sync_gdrive(file_path, conn)
            else:
                return {'success': False, 'error': f'Provedor "{provider_type}" ainda não suporta upload automático.'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _sync_aws(self, file_path, conn):
        """Lógica interna para upload AWS S3."""
        try:
            import boto3
            d = conn['data']
            s3 = boto3.client(
                's3',
                aws_access_key_id=d.get('access_key'),
                aws_secret_access_key=d.get('secret_key'),
                region_name=d.get('region', 'us-east-1')
            )
            filename = os.path.basename(file_path)
            s3.upload_file(file_path, d.get('bucket'), filename)
            self._save_cloud_meta(file_path, conn['label'])
            return {'success': True, 'provider': conn['label']}
        except ImportError:
            return {'success': False, 'error': 'Biblioteca "boto3" não instalada. Execute "pip install boto3".'}
        except Exception as e:
            return {'success': False, 'error': f'Erro AWS: {str(e)}'}

    def _sync_gdrive(self, file_path, conn):
        """Lógica interna para upload Google Drive via Service Account."""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            
            d = conn['data']
            info_raw = d.get('json_token')
            if not info_raw:
                return {'success': False, 'error': 'JSON de Service Account não encontrado na configuração.'}
            
            info = json.loads(info_raw)
            creds = service_account.Credentials.from_service_account_info(info)
            service = build('drive', 'v3', credentials=creds)
            
            file_metadata = {'name': os.path.basename(file_path)}
            media = MediaFileUpload(file_path, resumable=True)
            
            # Executa Upload
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
            self._save_cloud_meta(file_path, conn['label'])
            return {'success': True, 'provider': conn['label']}
            
        except ImportError as ie:
            return {'success': False, 'error': f'Falha técnica: {str(ie)}. Verifique se as bibliotecas google-api-python-client, google-auth-httplib2 e google-auth-oauthlib estão instaladas no ambiente correto.'}
        except Exception as e:
            return {'success': False, 'error': f'Erro Google Drive: {str(e)}'}

    def _save_cloud_meta(self, file_path, provider_label):
        """Salva metadados de sincronização localmente."""
        cloud_meta = {
            'provider': provider_label,
            'status': 'success',
            'synced_at': datetime.now().isoformat()
        }
        with open(f"{file_path}.cloud", 'w') as f:
            json.dump(cloud_meta, f)

    def list_snapshots(self):
        """Retorna lista de snapshots disponíveis com metadados."""
        snapshots = []
        if not os.path.exists(self.backup_dir):
            return snapshots

        for file in os.listdir(self.backup_dir):
            if file.endswith('.zip'):
                path = os.path.join(self.backup_dir, file)
                stats = os.stat(path)
                
                # Tenta ler o hash externo
                checksum = "N/A"
                hash_path = f"{path}.sha256"
                if os.path.exists(hash_path):
                    with open(hash_path, 'r') as f:
                        checksum = f.read().strip()

                # Tenta ler status cloud
                cloud_info = None
                cloud_path = f"{path}.cloud"
                if os.path.exists(cloud_path):
                    try:
                        with open(cloud_path, 'r') as f:
                            cloud_info = json.load(f)
                    except: pass

                snapshots.append({
                    'filename': file,
                    'size': stats.st_size,
                    'created_at': datetime.fromtimestamp(stats.st_mtime).strftime('%d/%m/%Y %H:%M'),
                    'checksum': checksum,
                    'path': path,
                    'cloud': cloud_info
                })
        
        # Ordena por data (mais recente primeiro)
        snapshots.sort(key=lambda x: x['created_at'], reverse=True)
        return snapshots

    def list_s3_snapshots(self):
        """Lista arquivos disponíveis diretamente no bucket S3."""
        import json
        config_path = os.path.join(current_app.instance_path, 'api_keys.json')
        if not os.path.exists(config_path): return []
        
        try:
            with open(config_path, 'r') as f: connections = json.load(f)
            conn = next((c for c in connections if c['provider'] == 'aws_s3'), None)
            if not conn: return []

            import boto3
            d = conn['data']
            s3 = boto3.client('s3', aws_access_key_id=d.get('access_key'), aws_secret_access_key=d.get('secret_key'), region_name=d.get('region', 'us-east-1'))
            
            response = s3.list_objects_v2(Bucket=d.get('bucket'))
            cloud_files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].endswith('.zip'):
                        cloud_files.append({
                            'filename': obj['Key'],
                            'size': obj['Size'],
                            'created_at': obj['LastModified'].strftime('%d/%m/%Y %H:%M'),
                            'provider': conn['label']
                        })
            return cloud_files
        except:
            return []


    def delete_snapshot(self, filename):
        """Remove um snapshot e seu hash associado."""
        path = os.path.join(self.backup_dir, filename)
        if os.path.exists(path):
            os.remove(path)
            hash_path = f"{path}.sha256"
            if os.path.exists(hash_path):
                os.remove(hash_path)
            return True
        return False

    def auto_cleanup(self, limit=30):
        """Remove os snapshots mais antigos se excederem o limite."""
        snapshots = self.list_snapshots()
        if len(snapshots) > limit:
            to_delete = snapshots[limit:]
            for snap in to_delete:
                self.delete_snapshot(snap['filename'])
            return len(to_delete)
        return 0
