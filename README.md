# SerialForge

Terminal serial com interface gráfica, feito em PySide6.

## Recursos

- Conexão serial com baudrate, data bits, paridade e stop bits configuráveis
- Log em tempo real em ASCII ou HEX, com timestamp e direção TX/RX
- Envio manual de frames em ASCII (com escapes `\n`, `\r`, `\xNN`) ou HEX
- **Comandos** salvos em arquivo (`.sfcmd`), com envio manual ou repetição automática
- **Triggers** (`.sftrig`) que reagem a padrões recebidos: destacar, inserir linha,
  enviar comando ou encerrar a conexão
- **Linhas de controle** no estilo Docklight: RTS e DTR clicáveis, CTS/DSR/DCD/RI
  monitorados em tempo real, e flow control RTS/CTS habilitável

## Instalação

### AppImage (recomendado)

Baixe o `.AppImage` na [página de releases](../../releases), dê permissão de
execução e rode:

```bash
chmod +x SerialForge-x86_64.AppImage
./SerialForge-x86_64.AppImage
```

Na primeira execução ele oferece adicionar um atalho ao menu de aplicativos
(sem senha de administrador).

### Pacote com instalador

Baixe o `SerialForge-linux-x86_64.tar.gz` na página de releases:

```bash
tar xzf SerialForge-linux-x86_64.tar.gz
cd SerialForge-linux-x86_64
sudo ./install.sh          # ou ./install.sh --user, sem sudo
```

Instala o executável em `/usr/local/bin/serialforge` e o atalho no menu.
Para remover: `sudo ./install.sh --uninstall`.

### Permissão de acesso à porta serial

O usuário precisa pertencer ao grupo da porta:

```bash
sudo usermod -aG uucp $USER      # Arch / Manjaro
sudo usermod -aG dialout $USER   # Debian / Ubuntu
```

Faça logout e login depois.

## Desenvolvimento

```bash
python -m venv venv
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python main.py
```

### Build

```bash
./venv/bin/python -m pip install pyinstaller
./scripts/build_release.sh       # executável + tar.gz (+ AppImage, se appimagetool estiver no PATH)
```

Os ícones são gerados a partir de `app/assets/artwork/` com
`scripts/generate_icons.py` — só é necessário rodar se a arte mudar.

### Releases

Empurrar uma tag dispara o workflow que compila e publica os artefatos:

```bash
git tag v1.0.0
git push origin v1.0.0
```
