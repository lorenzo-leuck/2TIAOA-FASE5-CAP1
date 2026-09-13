# Relatório do Fluxo Conversacional


As Actions foram definidas no arquivo `config/actions.json` e importadas programaticamente para a Action Skill usando a API `AssistantV2.update_skill`. O fluxo possui intenções de entrada, exemplos de frases e respostas específicas.

### Saudação

Frases como `oi`, `olá` e `bom dia` ativam a Action de saudação. O assistente apresenta sua finalidade e informa que pode orientar sobre pressão arterial e registrar medições.

### Orientação sobre pressão

Frases como `o que é pressão alta` ativam a Action de orientação. A resposta explica que a pressão alta está relacionada à elevação persistente da pressão nas artérias e ressalta que uma única medição não confirma diagnóstico.

### Registro de medição

Frases como `quero medir minha pressão` ativam a Action de registro. O assistente solicita o formato sistólica por diastólica, como `120 por 80`. Quando uma medição completa é recebida, o Flask valida os valores, registra a informação no SQLite e retorna uma confirmação com interpretação informativa.

São aceitos os formatos `120 por 80`, `120/80` e `120 x 80`. Valores incompletos, como `minha pressão está 80`, recebem uma solicitação para informar os dois números. Valores inconsistentes são rejeitados.

### Sintomas urgentes

Frases como `estou com dor no peito e falta de ar` ativam a Action de urgência. A resposta orienta procurar imediatamente o SAMU, pelo telefone 192, ou um pronto-socorro. O assistente não tenta diagnosticar a causa dos sintomas e não utiliza uma medição de pressão para minimizar uma situação de emergência.

### Fallback

Mensagens fora do escopo recebem uma resposta de fallback em português, apresentando as funções que o CardioIA oferece. O backend também utiliza um limiar de confiança para evitar que classificações fracas sejam tratadas como intenções válidas.

## Segurança, ética e limitações

Dados de saúde são sensíveis. Por isso, o protótipo utiliza somente o identificador da sessão, não solicita nome, CPF ou outros dados desnecessários e mantém as credenciais fora do código-fonte. O sistema também apresenta um aviso de que não substitui avaliação profissional.

As respostas foram limitadas a orientações gerais. A interpretação de uma medição é informativa e não representa diagnóstico. Sintomas como dor no peito associada à falta de ar sempre recebem prioridade de encaminhamento emergencial.

## Validação

Foram testados a criação de sessão, o envio de mensagens, a saudação, a orientação sobre pressão, o registro de `120 por 80`, a rejeição de valores inválidos, o tratamento de uma medida incompleta, o encaminhamento de sintomas urgentes e o fallback para mensagens fora do escopo.

O projeto foi validado com a aplicação React Native em modo web, o backend Flask e a Action Skill treinada no IBM watsonx Assistant.
