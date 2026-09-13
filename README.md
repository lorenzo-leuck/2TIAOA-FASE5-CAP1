# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

## Nome do grupo

CardioIA

## 👨‍🎓 Integrantes:
- <a href="https://www.linkedin.com/in/lorenzo-leuck/">Lorenzo Leuck</a>


## 👩‍🏫 Professores:
### Tutor(a)
Caique
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi</a>



## 📜 Descrição

O CardioIA é um protótipo de assistente cardiológico conversacional desenvolvido para a Fase 5. A solução utiliza o IBM watsonx Assistant para interpretar mensagens em linguagem natural e responder a dúvidas gerais sobre acompanhamento da pressão arterial.

O sistema é composto por uma aplicação React Native com Expo, executável no navegador ou em dispositivos móveis, um backend em Flask e um banco SQLite para armazenar medições da sessão. O backend mantém a comunicação segura com o Watson Assistant, cria sessões de conversa, encaminha mensagens e valida os dados recebidos.

O assistente contempla os fluxos de saudação, registro de pressão, consulta de histórico, orientação geral, ajuda, encerramento e encaminhamento de sintomas potencialmente urgentes. O sistema não realiza diagnósticos, não prescreve medicamentos e não substitui profissionais de saúde. Para demonstração, devem ser utilizados somente dados fictícios ou anonimizados.


## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>.github</b>: pasta reservada para arquivos de configuração específicos do GitHub.

- <b>assets</b>: arquivos relacionados a elementos não estruturados do repositório, como a logo da FIAP.

- <b>config</b>: arquivos de configuração do assistente, incluindo `actions.json` e `assistant-blueprint.json`.

- <b>document</b>: documentos solicitados pelas atividades, incluindo o enunciado.

- <b>scripts</b>: scripts auxiliares do projeto, incluindo a importação programática das Actions do Watson.

- <b>src</b>: código-fonte do backend Flask, integração com o Watson e persistência SQLite.

- <b>mobile</b>: aplicação React Native/Expo para a interface de interação com o assistente.

- <b>run.sh</b>: script para executar o backend Flask e o frontend Expo no modo web.

- <b>README.md</b>: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).

## 🔧 Como executar o código

### Pré-requisitos

- Python 3;
- Node.js e npm;
- Conta e instância do IBM watsonx Assistant;
- Credenciais do Watson configuradas no arquivo `.env`.

### Configuração do Watson

Copie `.env.example` para `.env` e preencha as credenciais.

```env
ASSISTANT_APIKEY=
ASSISTANT_IAM_APIKEY=
ASSISTANT_URL=
ASSISTANT_AUTH_TYPE=iam
ASSISTANT_ID=
ASSISTANT_DRAFT_ENVIRONMENT_ID=
ASSISTANT_ACTION_SKILL_ID=
```

O `Assistant ID` deve ser colocado em `ASSISTANT_ID`. O `Action Skill ID` deve ser colocado em `ASSISTANT_ACTION_SKILL_ID` para que as Actions sejam importadas pela API.

### Instalação

Na raiz do projeto, crie o ambiente Python e instale as dependências:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cd mobile
npm install
cd ..
```

### Importação das Actions

As Actions do assistente estão em `config/actions.json`. Para enviá-las diretamente à API do Watson, execute:

```bash
venv/bin/python scripts/import_actions.py
```

A importação é assíncrona. Aguarde o treinamento da Skill terminar antes de iniciar os testes.

### Execução do projeto

Para iniciar o Flask e o Expo diretamente no modo web:

```bash
PYTHON_BIN=venv/bin/python ./run.sh
```

O Flask será executado na porta `5000` e o Expo abrirá a aplicação web. Os logs do servidor e do Expo serão exibidos no terminal. Pressione `Ctrl+C` para encerrar os processos.

Para executar somente o frontend mobile pelo Expo Go:

```bash
cd mobile
npm start -- --lan
```

### Endpoints do backend

- `POST /api/session`: cria uma sessão do Watson;
- `POST /api/chat`: envia uma mensagem ao assistente;
- `POST /api/measurements`: registra uma medição;
- `GET /api/measurements`: consulta o histórico da sessão.

### Segurança

As chaves da IBM são carregadas por variáveis de ambiente e não são enviadas ao frontend. O protótipo valida as medições, utiliza sessões pseudonimizadas e não deve receber dados reais de pacientes.


## 🗃 Histórico de lançamentos

* 1.0.0 - 13/09/2026
    * Implementação do assistente conversacional com IBM watsonx Assistant.
    * Integração do backend Flask com a API V2.
    * Interface React Native/Expo com suporte web.
    * Persistência SQLite para medições de pressão.
    * Importação programática das Actions por API.

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
