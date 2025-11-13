# Date: 12/11/2025
# DEV: Martinez
# Cloud Optimizer v1 Free Utility by Martinez

O Cloud Optimizer é uma ferramenta avançada para otimização e monitoramento do Windows, com interface moderna em PyQt6, automações seguras e reversíveis, e painel de desempenho em tempo real.

## Funcionalidades

- **Monitoramento em tempo real**: CPU, RAM, GPU, disco e rede, com gráficos de 60 s.
- **Otimizações rápidas**: plano de energia, limpeza de temporários, ajustes de rede, desativação de serviços pesados, redução de efeitos visuais.
- **Gerenciamento de inicialização**: lista e desativa programas do registro (HKCU/HKLM) e pastas Startup, com opção de restaurar.
- **Log de atividades**: histórico de todas as ações realizadas.
- **Execução elevada automática**: solicita privilégios de administrador quando necessário.

## Instalação

1. Instale o Python 3.10+ ([download](https://www.python.org/downloads/))
2. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
3. Execute o programa:
   ```sh
   python Main.py
   ```

## Uso

- Recomenda-se criar um ponto de restauração antes de aplicar tweaks.
- Use o painel de log para acompanhar todas as ações.
- Para restaurar programas de inicialização, utilize o botão "Itens Desativados".

## Estrutura do Projeto

```
CLOUD OPTIMIZER v1/
├── Main.py                # Ponto de entrada
├── cloud_optimizer/
│   ├── main_window.py     # Interface principal
│   ├── monitor.py         # Coleta de métricas
│   ├── tweaks.py          # Funções de otimização
│   ├── startup.py         # Gerenciamento de inicialização
│   ├── utils.py           # Elevação/admin
│   └── widgets/
│       └── log_panel.py   # Painel de log
├── assets/                # Ícones e imagens
├── requirements.txt       # Dependências
├── CHANGELOG.md           # Histórico de mudanças
├── QUICKSTART.md          # Guia rápido e FAQ
└── LICENSE                # Licença MIT
```

## Perguntas Frequentes

**Preciso executar como administrador?**
Sim, para aplicar otimizações e gerenciar inicialização.

**Funciona em quais versões do Windows?**
Windows 7, 8, 10 e 11.

**É seguro?**
Sim, mas sempre crie um ponto de restauração antes de aplicar mudanças.

**Como reverter as alterações?**
Use o ponto de restauração ou o botão de restauração de inicialização.

## Suporte & Comunidade
- Discord: (https://discord.gg/ptM8XWaN5w)
- YouTube: [Prazer Martinezkr](https://www.youtube.com/@prazerMartinezkr)
- Canal Amathyzin: [aMathyzin](https://www.youtube.com/@aMathyzin)

## Licença
MIT — Prazer Martinez



Um programa executável completo para otimização e monitoramento do sistema Windows com interface gráfica moderna.

## Funcionalidades

### 1. Otimização de Desempenho
- **Plano de Energia**: Ativa automaticamente o plano de energia de alto desempenho do Windows
- **Otimização L3 Cache**: Calcula o tamanho do cache L3 da CPU e otimiza configurações no registro do Windows
- **Limpeza de Arquivos Temporários**: Remove arquivos temporários do sistema e usuário
- **Otimização de Serviços**: Desabilita serviços desnecessários do Windows (telemetria, etc.)
- **Efeitos Visuais**: Configura Windows para melhor desempenho
- **Rede**: Otimiza configurações de rede TCP/IP

### 2. Monitoramento em Tempo Real
- **CPU**: Uso por núcleo, frequência e temperatura
- **GPU**: Uso, memória VRAM e temperatura (NVIDIA)
- **RAM**: Uso total, disponível e porcentagem
- **Disco**: Espaço usado/livre e estatísticas de I/O
- **Rede**: Bytes enviados/recebidos
- Atualização automática a cada 2 segundos

### 3. Informações do Disco
- uso de disco em tempo real

### 4. Gerenciamento de Inicialização
- Lista todos os programas que iniciam com o Windows
- Desabilita programas desnecessários automaticamente
- Remove itens inúteis da inicialização
- Melhora tempo de boot do sistema

## Requisitos

### Sistema
- Windows 7, 8, 10 ou 11 (64-bit recomendado)
- Privilégios de Administrador (obrigatório)
- .NET Framework (geralmente já instalado)

## Como Usar

### 1. Executar o Programa

**IMPORTANTE**: Sempre execute como Administrador!

- Clique com botão direito no executável
- Selecione "Executar como administrador"
- Aceite o prompt de UAC (Controle de Conta de Usuário)


## Detalhes Técnicos

Configurações modificadas:
- `LargeSystemCache`: Otimiza cache do sistema
- `DisablePagingExecutive`: Mantém kernel na RAM
- `SecondLevelDataCache`: Configura tamanho do cache baseado na CPU

### Plano de Energia

Ativa o plano de energia GUID: `8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c` (Alto Desempenho)

Configurações adicionais:
- Desliga monitor: Nunca
- Desliga disco: Nunca
- Modo de espera: Nunca
- Hibernação: Nunca

### Serviços Otimizados

Serviços desabilitados para melhor desempenho:
- **DiagTrack**: Telemetria do Windows
- **dmwappushservice**: WAP Push Message
- **SysMain**: Superfetch (pode prejudicar SSDs)
- **WSearch**: Windows Search (se não usar busca frequente)


## Avisos Importantes

### Segurança

- ✅ O programa NÃO coleta dados
- ✅ NÃO se conecta à internet
- ✅ Código fonte aberto e auditável
- ✅ Todas as modificações são locais

### Riscos

- ⚠️ Modificações no registro podem causar instabilidade se feitas incorretamente
- ⚠️ SEMPRE crie um ponto de restauração antes de usar
- ⚠️ Desabilitar serviços pode afetar algumas funcionalidades do Windows
- ⚠️ Use por sua conta e risco

### Recomendações

1. **Faça backup**: Crie um ponto de restauração do Windows
2. **Teste primeiro**: Use em um ambiente de teste se possível
3. **Leia as mensagens**: O programa avisa quando reinicialização é necessária
4. **Monitore o sistema**: Após otimizações, monitore estabilidade por alguns dias

## Solução de Problemas

### Programa não abre
- Certifique-se de executar como Administrador
- Verifique se o Windows Defender não bloqueou
- Tente desabilitar antivírus temporariamente

### Erro "Não foi possível acessar o registro"
- Execute como Administrador
- Desabilite proteção em tempo real do antivírus

### GPU não aparece
- Suporte apenas para GPUs NVIDIA (usa GPUtil)
- Certifique-se de ter drivers NVIDIA instalados
- GPUs AMD/Intel não são suportadas no momento

### Temperatura não aparece
- Nem todos os sistemas expõem sensores de temperatura via WMI
- Use programas específicos como HWiNFO64 para monitoramento detalhado


### Roadmap

Funcionalidades planejadas:
- [ ] Suporte para GPUs AMD/Intel
- [ ] Agendamento automático de otimizações
- [ ] Perfis de otimização (Gaming, Trabalho, Economia de Energia)
- [ ] Backup automático de configurações
- [ ] Modo escuro/claro
- [ ] Gráficos de histórico de desempenho
- [ ] Exportar relatórios em PDF

## Licença

Este projeto é de código aberto. Veja o arquivo LICENSE para detalhes.

## Autor

Desenvolvido por Martinez.

## Suporte

Para reportar bugs ou sugerir funcionalidades, fale no servidor do Amathyzin. (Servidor do Discord: https://discord.gg/ptM8XWaN5w)

---

**AVISO LEGAL**: Este software é fornecido "como está", sem garantias de qualquer tipo. O autor não se responsabiliza por quaisquer danos causados pelo uso deste programa. Use por sua conta e risco.
