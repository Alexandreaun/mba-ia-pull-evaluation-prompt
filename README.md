
  **Seção "Técnicas Aplicadas (Fase 2)"**:

   As técnicas usadas para refatoração do prompt, foram:
    - role_prompting
    - few_shot_learning
    - Chain of Thought (CoT)

   Justificativa de por que escolheu cada técnica:

      Role prompting: 
      Utilizei para definição de persona e contexto detalhado das funções que o modelo irá interpretar, utilizando esta técnica fica mais claro para o modelo executar somente as funções que são pertinentes a este papel.
      
      Few_shot_learning: 
      Neste contexto, dando exemplos, ajuda o modelo a manter o mesmo padrão de saída para todos os casos do dataset.
      
      Chain of Thought (CoT): 
      Utilizei para forçar o modelo a decidir melhor antes de escrever a User Story, no caso é um raciocínio estruturado interno que pedi para não expor o raciocínio neste caso.
   
  Exemplos práticos de como aplicou cada técnica:
    Conforme o prompt v2, abaixo seguem trechos de exemplos práticos das técnicas aplicadas:

    Role_prompting:
      Você é um Analista de Requisitos Sênior.
      Seu papel é transformar relatos de bugs escritos em linguagem informal, técnica ou mista em tarefas estruturadas para times de Produto, Engenharia e QA.
      Seu objetivo é gerar uma resposta clara, precisa, útil e correta, seguindo o estilo das referências esperadas em datasets de avaliação.

    Few_shot_learning:
      Exemplos conforme dados do dataset, por complexidade, abaixo os dois primeiros exemplos do prompt, mas foram utilizados 7 exemplos para cobrir todos os casos de todos os json do dataset.

      Exemplo 1 - Bug simples de e-commerce

      Input:
      Relato: Botão de adicionar ao carrinho não funciona no produto ID 1234.

      Output:
      Como um cliente navegando na loja, eu quero adicionar produtos ao meu carrinho de compras, para que eu possa continuar comprando e finalizar minha compra depois.

      Critérios de Aceitação:
      - Dado que estou visualizando um produto
      - Quando clico no botão "Adicionar ao Carrinho"
      - Então o produto deve ser adicionado ao carrinho
      - E devo ver uma confirmação visual
      - E o contador do carrinho deve ser atualizado

      Exemplo 2 - Bug simples de validação

      Input:
      Relato: Campo de email aceita texto sem @, permitindo cadastros inválidos.

      Output:
      Como um usuário criando uma conta, eu quero que o sistema valide meu email corretamente, para que eu não insira um endereço inválido por   engano.

      Critérios de Aceitação:
      - Dado que estou no formulário de cadastro
      - Quando digito um email sem o caractere @
      - Então devo ver uma mensagem de erro
      - E não devo conseguir prosseguir com o cadastro
      - E a mensagem deve explicar o formato correto

    Chain of Thought (CoT):
      Processo interno:
      Antes de responder, analise internamente:

      1. Qual é o usuário afetado.
      2. Qual funcionalidade foi impactada.
      3. Qual é o comportamento atual problemático.
      4. Qual é o comportamento esperado.
      5. Qual é o benefício direto para o usuário ou para o sistema.
      6. Quais critérios tornam a correção testável.
      7. Se o relato é simples, médio ou complexo.
      8. Se o relato contém detalhes técnicos, impacto de negócio, segurança, performance, integração, concorrência, cache, sincronização ou múltiplos problemas.
      9. Se a resposta final está no formato correto para a complexidade identificada.
      10. Se cada seção gerada tem rastreabilidade direta com o relato original.

  **Seção "Resultados Finais"**:

   - Link público do seu dashboard do LangSmith mostrando as avaliações:
    https://smith.langchain.com/public/1d8269df-31f4-4181-9b0f-652e8111bd0d/d


  **Seção "Como Executar"**:

  Configurações de Variáveis de ambiente:

    No arquivo .env, inserir as variáveis de ambiente:
    LANGSMITH_TRACING=true
    LANGSMITH_ENDPOINT=https://api.smith.langchain.com
    LANGSMITH_API_KEY=YOUR_API_KEY
    LANGSMITH_PROJECT="prompt-optimization-challenge-resolved"
    OPENAI_API_KEY=YOUR_OPENAI_KEY

  Rodar projeto:

    Executar os comandos no terminal:

    Faça upload do dataset para o langsmith:
    python3 datasets/upload_dataset.py

    Execute os testes e verifique se o prompt atende todos os requisitos necessários:
    pytest tests/test_prompts.py  

    Faça push do prompt otimizado para o langsmith:
    python3 src/push_prompts.py

    Execute os Evaluators (Clarity, Correcteness, Helpfulness, Precision e F1_Score) no langsmith:
    python3 src/prompt_evaluators.py


  **Evidências no LangSmith**:

     - Dataset de avaliação com 15 exemplos
    https://smith.langchain.com/public/1d8269df-31f4-4181-9b0f-652e8111bd0d/d/compare?selectedSessions=581caf58-8778-42dd-b9ab-ffb97dbe49b1

     - Execuções dos prompts v2 (otimizados) com notas ≥ 0.8:
     https://smith.langchain.com/public/1d8269df-31f4-4181-9b0f-652e8111bd0d/d

    - Tracing detalhado de pelo menos 3 exemplos:
    https://smith.langchain.com/public/1200117a-54f6-49e8-a44c-92b519ebc42b/r
    https://smith.langchain.com/public/cf6166fe-71ac-4787-a3f7-256dc5ae2175/r
    https://smith.langchain.com/public/0d8732aa-109e-404c-8463-c4e47bbbaa4b/r
