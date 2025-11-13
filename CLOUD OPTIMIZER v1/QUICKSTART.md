# Date: 12/112025
# DEV: Martinez
# Cloud Optimizer v1 Free Utility by Martinez

# Guia de Início Rápido

#### Passo 1: Criar Ponto de Restauração
1. Pressione `Win + R`
2. Digite `sysdm.cpl` e pressione Enter
3. Vá para aba "Proteção do Sistema"
4. Clique em "Criar"
5. Dê um nome (ex: "Antes Otimização")

#### Passo 2: Executar Otimizações
1. Abra o Otimizador como Administrador
2. Vá para aba "Otimização"
3. Clique em "Ativar Desempenho Máximo"
4. Clique em "Calcular e Otimizar L3 Cache"
5. Clique em "Limpar Arquivos Temporários"
6. Clique em "Otimizar Serviços do Windows"
7. Clique em "Desativar Efeitos Visuais"

#### Passo 3: Gerenciar Inicialização
1. Vá para aba "Programas de Inicialização"
2. Clique em "Atualizar Lista"
3. Revise a lista de programas
4. Clique em "Desativar Programas Inúteis"

#### Passo 4: Reiniciar
1. Salve todo o trabalho
2. Reinicie o computador
3. Aproveite o desempenho melhorado!

### 4. Monitorar

Para ver o desempenho do sistema:
1. Abra o Otimizador
2. Vá para aba "Monitoramento"
3. Clique em "Iniciar Monitoramento"
4. Observe temperatura, uso de CPU, GPU, RAM, etc.


### Estrutura Básica (Para Desenvolvedores!)

```python
# Principais módulos e funções do Cloud Optimizer:

# Janela principal e navegação
class MainWindow:
    def build_monitor_page()      # Painel de monitoramento em tempo real
    def build_tweaks_page()       # Cartões de otimização (energia, rede, limpeza, etc)
    def build_startup_page()      # Gerenciador de inicialização (ativar/desativar/restaurar)
    def append_log(msg)           # Adiciona mensagem ao painel de log

# Coleta de métricas do sistema
class Monitor:
    def get_metrics()             # Retorna uso de CPU, RAM, GPU, disco, rede, temperatura

# Funções de otimização
# (módulo tweaks.py)
def set_high_performance():       # Ativa plano de energia de alto desempenho
def clean_temp_files():           # Limpa arquivos temporários do sistema
def optimize_network():           # Ajusta rede e limpa cache DNS
def optimize_services():          # Desativa serviços pesados (SysMain, DiagTrack, etc)
def disable_visual_effects():     # Reduz efeitos visuais para performance
def disable_useless_programs():   # Remove apps comuns da inicialização

def is_admin():                   # Verifica se está rodando como administrador
def run_as_admin():               # Eleva o processo automaticamente

# Gerenciamento de inicialização
# (módulo startup.py)
def list_startup_programs():      # Lista todos os programas que iniciam com o Windows
def disable_startup_item(entry):  # Desativa item de inicialização (registro/pasta)
def list_disabled_startup_items():# Lista itens desativados para restaurar
def restore_startup_item(entry):  # Restaura item para inicialização

# Painel de log
class LogPanelWidget:
    def append(msg):              # Adiciona mensagem ao log
    def clear_logs():             # Limpa o log
    def copy_logs():              # Copia o log para área de transferência
```

## Perguntas Frequentes

**P: Preciso executar como Administrador?**
R: Sim, sempre. Muitas otimizações requerem privilégios elevados.

**P: É seguro?**
R: Sim, mas sempre crie um ponto de restauração antes.

**P: Funciona no Windows 11?**
R: Sim, compatível com Windows 7, 8, 10 e 11.

**P: Quanto de desempenho vou ganhar?**
R: Varia por sistema. Geralmente 5-15% em sistemas mais antigos.

**P: Posso reverter as mudanças?**
R: Sim, use o ponto de restauração que criou.

**P: Por que minha GPU não aparece?**
R: Atualmente só suporta NVIDIA. AMD/Intel em breve.

## Problemas Comuns

### Erro: "Acesso negado"
**Solução**: Execute como Administrador

### Erro: "Módulo não encontrado"
**Solução**:
```bash
pip install -r requirements.txt
```

### Programa não abre
**Solução**:
1. Desabilite antivírus temporariamente
2. Adicione exceção no Windows Defender
3. Execute como Administrador

### Temperatura não aparece
**Solução**: Normal em alguns sistemas. Use HWiNFO64 para detalhes.

# 🚀 Guia Rápido: Como Abrir o Cloud Optimizer

Este tutorial vai te ajudar a rodar o Cloud Optimizer do zero, instalar dependências e resolver os erros mais comuns.

## 1. Pré-requisitos
- Windows 7 ou superior (7,8,10 e 11)
- Python 3.10+ instalado ([baixar aqui](https://www.python.org/downloads/))
- Pip atualizado
- Permissão de administrador (para tweaks avançados)

## 2. Instale as dependências
Abra o terminal (CMD) na pasta do projeto e rode:
```sh
pip install -r requirements.txt
```
Se aparecer erro de arquivo não encontrado, confira se o nome está correto (`requirements.txt`).

## 3. Execute o programa
No terminal, digite:
```sh
python Main.py
```
Se pedir permissão de administrador, aceite para liberar todas as funções.

## 4. Possíveis erros e soluções
- **Erro: "No module named PyQt6"**
  - Rode novamente: `pip install PyQt6`
- **Erro: "PermissionError" ao desativar inicialização**
  - Execute o programa como administrador (botão direito > "Executar como administrador").
- **Erro: "requirements.txt not found"**
  - Verifique se está na pasta correta e se o arquivo existe.
- **Gráfico não aparece ou está preto**
  - Instale o pacote: `pip install pyqtgraph GPUtil`
  - Se persistir, feche e abra o programa novamente.
- **Temperatura da CPU não aparece**
  - Nem todo hardware expõe sensores; isso é normal em alguns PCs.

## 5. Dicas extras
- Sempre crie um ponto de restauração antes de aplicar tweaks.
- Use o botão de log para acompanhar tudo que foi feito.
- Para restaurar programas de inicialização, use o botão "Itens Desativados".

## 6. Suporte
Se tiver dúvidas ou problemas:
- Consulte o arquivo CHANGELOG.md para detalhes das funções
- Entre no Discord: [discord.gg/ptM8XNaM5w]
- Veja tutoriais no YouTube: [Amathyzin](https://www.youtube.com/@aMathyzin)

---
Pronto! Agora é só aproveitar o Cloud Optimizer 🚀
