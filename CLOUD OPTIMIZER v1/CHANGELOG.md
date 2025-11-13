# Cloud Optimizer v1 Free Utility by Martinez
# Dev: Martinez
# Date: 12/11/2025



# Changelog

## [1.1.0] - 2025-11-12

Versão que consolida tudo que construímos até aqui: interface redesenhada com PyQt6, monitoramento em tempo real com gráficos, automações de otimização confiáveis e um gerenciador de inicialização elegante com reversão segura. A aplicação agora é distribuída em executável standalone e mantém um histórico de mudanças para cada ação executada.

### Destaques
- � **Interface refinada em PyQt6**: janela frameless com controles personalizados, tema escuro, navegação lateral animada e log embutido.
- 📊 **Monitoramento em tempo real**: métricas de CPU, GPU (via GPUtil), RAM, disco e rede, além de gráfico de 60 s com PyQtGraph e limites visuais aprimorados.
- ⚙️ **Tweaks guiados e seguros**: cada botão verifica privilégios de administrador, exibe aviso para criação de ponto de restauração e registra o resultado.
- � **Gerenciamento de inicialização**: lista entradas do registro (HKCU/HKLM) e pastas Startup, permite desativar com um clique e guardar tudo em “Disabled by CloudOptimizer” para restauração rápida.
- 🛡️ **Execução elevada automática**: ao iniciar, o app solicita privilégios administrativos para evitar falhas na hora dos ajustes de sistema.

### O que cada função faz
- `MainWindow` (em `cloud_optimizer/main_window.py`)
  - Monta toda a interface, alterna páginas, aplica animações e controla logs.
  - `build_monitor_page`: cria o painel de métricas, ativa o `Monitor` e o gráfico com limitações de 0-100 % e 60 s.
  - `build_tweaks_page`: exibe cartões para cada otimização, gerencia threads e mostra feedback visual.
  - `build_startup_page`: renderiza lista de programas de inicialização, conecta botões de desativar/restaurar e abre o diálogo de itens desativados.
- `Monitor` (em `cloud_optimizer/monitor.py`)
  - Usa `psutil` e `GPUtil` para coletar CPU, RAM, GPU, disco e rede.
  - Calcula deltas de leitura/gravação e monta strings prontas para exibição.
- Tweaks (em `cloud_optimizer/tweaks.py`)
  - `set_high_performance`: ativa plano de energia de alto desempenho e remove timeouts.
  - `clean_temp_files`: remove temporários de pastas do usuário e do sistema.
  - `optimize_network`: aplica ajustes `netsh` e limpa cache DNS.
  - `optimize_services`: desativa serviços pesados como SysMain, WSearch e DiagTrack.
  - `disable_visual_effects`: ajusta chaves do registro para melhor desempenho gráfico.
  - `disable_useless_programs`: remove apps comuns da inicialização e tenta desabilitar tarefas associadas.
- Inicialização (em `cloud_optimizer/startup.py`)
  - `list_startup_programs`: busca entradas em HKCU/HKLM Run e nas pastas Startup.
  - `disable_startup_item`: move valores para a chave `DisabledByCloudOptimizer` ou para uma pasta dedicada.
  - `list_disabled_startup_items` e `restore_startup_item`: permitem reverter qualquer item com segurança.
- Utilidades (em `cloud_optimizer/utils.py`)
  - `is_admin` e `run_as_admin`: detectam e elevam o processo automaticamente para garantir que os tweaks funcionem.
- LogPanel (em `cloud_optimizer/widgets/log_panel.py`)
  - Widget reutilizável que exibe histórico de ações, permite limpar ou copiar com um clique.

### Dependências principais
- Python 3.10+
- PyQt6 (UI)
- psutil (métricas de sistema)
- GPUtil (uso de GPU Nvidia)
- pyqtgraph (gráficos em tempo real)

### Notas técnicas
- Todos os tweaks potencialmente arriscados exigem execução como administrador.
- Itens de inicialização removidos são armazenados em área de quarentena para restauração.
- Monitoramento continua funcionamento mesmo sem PyQtGraph ou GPUtil (o app trata ausência dessas libs).

### Limitações atuais
- Temperaturas dependem de sensores expostos por `psutil`; alguns hardwares podem não fornecer dados.
- Algumas otimizações (serviços, rede) podem solicitar reinicialização para efeito completo.
- Usuários sem privilégios administrativos terão algumas ações bloqueadas.

### Segurança
- ✅ Executa apenas comandos locais, sem tráfego externo.
- ✅ Mantém backup das entradas de inicialização antes de desativar.
- ✅ Logs visíveis para o usuário acompanhar cada operação.
- ⚠️ Recomendado criar ponto de restauração antes de aplicar múltiplos tweaks.

## [Futuro] - Roadmap

### Planejado para vesao paga!
- [ ] Suporte para GPUs AMD (via PyAMDGPUInfo)
- [ ] Suporte para GPUs Intel
- [ ] Gráficos em tempo real de desempenho
- [ ] Histórico de monitoramento
- [ ] Exportação de relatórios
- [ ] Perfis de otimização (Gaming, Trabalho, Economia)
- [ ] Agendamento de tarefas
- [ ] Backup/Restore de configurações
- [ ] Modo escuro/claro
- [ ] Tradução para inglês
- [ ] Otimização de jogos específicos
- [ ] Overclock assistido (avançado)
- [ ] Benchmark integrado
- [ ] Comparação de desempenho
- [ ] Sugestões inteligentes baseadas em hardware
- [ ] Integração com ferramentas externas
- [ ] API para automação
- [ ] Modo CLI (linha de comando)



## 🆘 Suporte & Comunidade

Se tiver dúvidas, sugestões ou encontrar algum bug:
- Abra uma issue no repositório do GitHub
- Participe do Discord do aMathyzin: [discord.gg/ptM8XNaM5w]
- Assista tutoriais e novidades no YouTube:
  - [Prazer Martinezkr](https://www.youtube.com/@prazerMartinezkr)
  - [Canal aMathyzin](https://www.youtube.com/@aMathyzin)

Fique à vontade para compartilhar feedback, pedir novas funções ou mostrar seu resultado!

---
---

**Nota**: Este é o primeiro lançamento público. Feedback é muito bem-vindo!
