Plano para v2 — Follow-up de sinais 100% e monitoramento de targets
Objetivo
Quando um sinal atingir 100% de confiança, registrar no Discord que “poderia comprar/shortar” (alerta, sem operação real).

Guardar essa moeda/posição numa estrutura para monitorar ganhos.

A cada 5% de valorização (ganho na posição), enviar um log no Discord com o progresso.

Enviar notificações quando atingir target1, target2, target3 e fechar posição.

Como implementar (pseudo passo a passo)
1. Criar uma estrutura para armazenar as posições abertas (em memória)
python
Copy
Edit
# Exemplo de dicionário para armazenar as trades monitoradas:
posicoes_abertas = {
    'BTCUSDT': {
        'entry_price': 24000,
        'direction': 'SHORT',  # ou 'LONG'
        'targets': [22800, 22000, 21200],  # Exemplo, pode calcular a partir do report
        'last_logged_target_index': -1  # qual target já foi reportado
    },
    ...
}
2. Na função monitorar, quando detectar sinal 100% (ou >= 100%), registrar a posição nesse dicionário e mandar o alerta no Discord (não executar compra).
python
Copy
Edit
if confidence == 100:
    if symbol not in posicoes_abertas:
        last_close = df_15m['close'].iloc[-1]
        direction = 'SHORT' if check_reversal(df_15m) else 'LONG'
        # Calcular targets e stop_loss como no generate_report para usar no monitoramento
        stop_loss = ...
        target_1 = ...
        target_2 = ...
        target_3 = ...  # Pode calcular 3 targets

        posicoes_abertas[symbol] = {
            'entry_price': last_close,
            'direction': direction,
            'targets': [target_1, target_2, target_3],
            'last_logged_target_index': -1
        }

        await canal.send(f"🚀 *Possível {direction} iniciada para `{symbol}` a {last_close:.4f}*")
3. Após a análise de todos os símbolos, monitorar as posições abertas:
Buscar preço atual do símbolo

Calcular se o preço atingiu algum target novo (5% ou mais de ganho do entry_price)

Se sim, enviar mensagem e atualizar last_logged_target_index

python
Copy
Edit
for symbol, pos in list(posicoes_abertas.items()):
    df_current = get_klines(client_binance, symbol, interval='1m')  # ou 15m para ser mais leve
    current_price = df_current['close'].iloc[-1]

    entry = pos['entry_price']
    direction = pos['direction']
    targets = pos['targets']
    last_idx = pos['last_logged_target_index']

    # Define função para calcular percentual ganho
    def percentual_ganho(entry, current, direction):
        if direction == 'LONG':
            return (current - entry) / entry * 100
        else:
            return (entry - current) / entry * 100

    ganho = percentual_ganho(entry, current_price, direction)

    # Checa se ultrapassou algum novo target (incremento de 5% do entry)
    for idx, target in enumerate(targets):
        if idx <= last_idx:
            continue
        if (direction == 'LONG' and current_price >= target) or (direction == 'SHORT' and current_price <= target):
            await canal.send(f"🎯 `{symbol}` atingiu target {idx+1}: preço atual {current_price:.4f}")
            posicoes_abertas[symbol]['last_logged_target_index'] = idx

    # Fecha posição se atingiu target final ou stop loss (pode implementar stop_loss também)
    # Exemplo de fechamento no target 3
    if last_idx == len(targets) - 1:
        await canal.send(f"✅ `{symbol}` fechando posição no target final. Ganho estimado: {ganho:.2f}%")
        del posicoes_abertas[symbol]
Observações importantes
Como está em memória, ao reiniciar o bot, perde o histórico. Para persistência, poderia salvar em arquivo ou DB, mas para v2 pode ser simples.

Para evitar spam, você pode controlar cooldowns de mensagens.

A frequência do monitoramento pode ser menor para as posições abertas (ex: a cada 1 ou 5 minutos).