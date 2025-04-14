# 🎵 Editor de Rádio para Euro Truck Simulator 2

Este é um editor gráfico avançado para estações de rádio do Euro Truck Simulator 2 (arquivo `live_streams.sii`), desenvolvido em **Python** com **Tkinter**.

## 🚀 Recursos Principais

- 📂 **Gerenciamento completo de arquivos**
- 🌍 **Suporte multilíngue avançado**
- 🎨 **Interface intuitiva com ordenação de colunas**
- ⭐ **Marcação de estações favoritas**

## 📥 Download e Instalação

### 🔹 Versão Instalável (Windows)

1. Baixe na [página de Releases](https://github.com/adambravo79/editor-radios/releases)
2. Execute o instalador
3. Siga as instruções na tela

## 📚 Estrutura de Arquivos

```txt
project_root/
│
├── languages/ # Pasta de configurações de idioma
│ ├── config_pt_BR.json # Configurações em Português Brasileiro
│ ├── config_en_US.json # Configurações em Inglês Americano
│ └── (outros idiomas) # Arquivos adicionais de idioma
│
├── backups/ # Pasta de backups automáticos (criada durante a execução)
│ ├── live_streams.sii.bak_20240101_120000
│ └── (outros backups)
│
├── main.py # Arquivo principal do aplicativo
├── user_settings.json # Configurações de usuário persistentes
└── README.md # Este arquivo de documentação
```

### Detalhes dos Arquivos

1. **Arquivos de Idioma** (`languages/`):
   - Formato JSON com todas as traduções da interface
   - Estrutura padrão:

     ```json
     {
       "app_title": "Editor de Rádio",
       "buttons": {
         "open": "Abrir",
         "save": "Salvar"
       },
       "messages": {
         "save_success": "Arquivo salvo com sucesso!"
       }
     }
     ```

2. **Backups Automáticos**:
   - Criados na primeira abertura de um arquivo
   - Nome padrão: `[nome_original].bak_[AAAAMMDD_HHMMSS]`
   - Armazenados na subpasta `backups` do diretório do arquivo original

3. **user_settings.json**:
   - Armazena as preferências do usuário:

     ```json
     {
       "language": "pt_BR"
     }
     ```

## ▶️ Como Executar

```bash
# Navegue até a pasta do projeto
cd caminho/para/project_root

# Execute o aplicativo
python main.py
```

### 🛠️ Dependências

Listadas no arquivo requirements.txt:

```txt
tkinter>=0.1.0
ttkthemes>=3.2.2
```

Instale com:

```bash
pip install -r requirements.txt
```

## ⚙️ Como Contribuir

1. Faça um fork do repositório
2. Crie uma branch (`git checkout -b minha-feature`)
3. Faça suas alterações e commit (`git commit -m "Adicionei um recurso X"`)
4. Envie para o repositório remoto (`git push origin minha-feature`)
5. Abra um Pull Request 🚀

## 📜 Licença

Este projeto é licenciado sob a licença **MIT**. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido por [Andre "AdamBravo" Nascimento]** 🚛📻
