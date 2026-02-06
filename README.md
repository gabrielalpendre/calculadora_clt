# Calculadora RH

Uma aplicação web simples construída com Flask para realizar cálculos trabalhistas comuns no cenário brasileiro, focando em rescisão de contrato e análise de remuneração mensal.

## Funcionalidades

A aplicação é dividida em duas calculadoras principais:

### 1. Calculadora de Rescisão
- Calcula as verbas rescisórias para diferentes cenários (pedido de demissão, demissão sem justa causa, etc.).
- Considera detalhes como aviso prévio (trabalhado ou indenizado), férias vencidas e proporcionais, 13º proporcional e saldo de salário.
- Realiza o cálculo dos descontos de INSS e IRRF sobre as verbas rescisórias.
- Permite a exportação do resultado detalhado para um arquivo **PDF**.

### 2. Calculadora de Salário Mensal
- Calcula o salário líquido mensal a partir do salário bruto, considerando descontos de INSS e IRRF.
- Permite incluir o número de dependentes para o cálculo do IRRF.
- Oferece uma **sugestão de salário equivalente para o modelo PJ (Pessoa Jurídica)**, levando em conta benefícios como 13º, férias, FGTS, VA/VR e bônus.
- Apresenta uma **análise do valor/hora** de trabalho, comparando o modelo CLT (base 220h) e PJ (base 168h).
- Permite a impressão/exportação do relatório completo para um arquivo **PDF**.

The version in Github Pages is live in https://gabrielalpendre.github.io/calculadora_clt/
Static page in /docs folder of this repo