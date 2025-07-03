import os
import subprocess
from config.settings import SMB_CONFIG

def mount_smb_share():
    """Monta o compartilhamento SMB no Linux."""
    try:
        # Criar diretório de montagem se não existir
        if not os.path.exists(SMB_CONFIG['mount_point']):
            os.makedirs(SMB_CONFIG['mount_point'])
            print(f"✓ Diretório de montagem criado: {SMB_CONFIG['mount_point']}")
        # Verificar se já está montado
        if os.path.ismount(SMB_CONFIG['mount_point']):
            print(f"✓ Compartilhamento já montado em: {SMB_CONFIG['mount_point']}")
            return True
        # Comando para montar o compartilhamento
        mount_cmd = [
            'sudo', 'mount', '-t', 'cifs',
            f"//{SMB_CONFIG['host']}/{SMB_CONFIG['share']}",
            SMB_CONFIG['mount_point'],
            '-o', f"username={SMB_CONFIG['username']},password={SMB_CONFIG['password']},iocharset=utf8,file_mode=0777,dir_mode=0777"
        ]
        print(f"🔗 Montando compartilhamento SMB: //{SMB_CONFIG['host']}/{SMB_CONFIG['share']}")
        result = subprocess.run(mount_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Compartilhamento montado com sucesso em: {SMB_CONFIG['mount_point']}")
            return True
        else:
            print(f"✗ Erro ao montar compartilhamento: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Erro ao montar compartilhamento SMB: {e}")
        return False

def unmount_smb_share():
    """Desmonta o compartilhamento SMB."""
    if os.path.ismount(SMB_CONFIG['mount_point']):
        try:
            subprocess.run(['sudo', 'umount', SMB_CONFIG['mount_point']], check=True)
            print(f"✓ Compartilhamento desmontado: {SMB_CONFIG['mount_point']}")
        except Exception as e:
            print(f"⚠ Aviso: Não foi possível desmontar o compartilhamento: {e}")
