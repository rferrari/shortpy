README - BotShort v2
Descrição
Bot de monitoramento de sinais para operar SHORT no mercado de futuros, utilizando análise técnica com indicadores (EMA, RSI, MACD, etc).

Nesta versão v2, foram implementadas funcionalidades para registro e acompanhamento das posições abertas, com alertas mais visuais e interativos no Discord.

Funcionalidades principais
1. Monitoramento e geração de sinais
Verifica moedas com capitalização dentro do filtro.

Analisa candles em 15m, 1h e 4h para calcular indicadores técnicos.

Quando um sinal bearish (SHORT) 100% confirmado ocorre (EMA crossover, reversão, alta confiança), cria uma posição aberta.

2. Criação e comunicação de posições no Discord
Ao abrir uma posição SHORT:

Envia um embed colorido vermelho com detalhes da entrada, stop loss e targets.

Adiciona uma reação ✅ na mensagem para confirmação visual da equipe.

3. Acompanhamento contínuo das posições abertas
A cada minuto o bot verifica o preço atual das posições abertas.

Quando um target é atingido, adiciona campo no embed informando o ganho parcial.

Se o stop loss é acionado, o bot fecha a posição e atualiza o embed com informações da perda.

Quando todos os targets são atingidos, o bot fecha a posição e informa o ganho total no embed.

4. Gestão e fechamento das posições
As posições são mantidas na memória durante a execução do bot.

O embed da posição é atualizado continuamente, mantendo o histórico de status e ganhos/paradas.

Posições fechadas são removidas da lista de monitoramento.

Estrutura do projeto
bot.py: arquivo principal que roda o bot Discord, faz monitoramento dos sinais e gerencia as posições.

positions.py: classe para representar posições abertas, com lógica de targets, stop loss, e fechamento.

data.py: funções para obter dados das moedas, preços e candles (já existentes).

analysis.py: funções para cálculo de indicadores técnicos (EMA, RSI, MACD, etc).

Como usar
Configure as variáveis no .env:

ini
Copy
Edit
API_KEY=suakeybinance
API_SECRET=suasecretbinance
DISCORD_TOKEN=seutokendiscord
CANAL_ID=seu_id_canal_discord
Instale dependências (exemplo com pip):

bash
Copy
Edit
pip install discord.py python-dotenv pandas numpy
Execute o bot:

bash
Copy
Edit
python bot.py
Observações importantes
A confirmação visual via reação ✅ permite à equipe validar que a posição está sendo acompanhada.

Atualizações são feitas editando o embed original da posição, evitando spam no canal.

O bot suporta até 3 targets de lucro e stop loss, adaptáveis conforme sua estratégia.

A lógica atual é para operações SHORT; para LONG, a estrutura pode ser adaptada.

Próximos passos sugeridos
Implementar comando Discord para listar posições abertas e status.

Salvar posições em banco de dados para persistência entre reinícios do bot.

Adicionar alertas para sinais LONG e outros setups.

Melhorar interface e interatividade via botões e menus.

