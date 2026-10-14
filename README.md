# Análise de Vendas de E-commerce com SQL e PostgreSQL

## Sobre o projeto

Este projeto tem como objetivo aplicar conceitos de análise de dados para investigar o desempenho de vendas de um e-commerce, transformando dados estruturados em indicadores que apoiam a tomada de decisão.

O projeto contempla a modelagem de um banco de dados relacional, a geração de dados sintéticos e a elaboração de consultas SQL para analisar pedidos, faturamento, ticket médio e desempenho por categoria de produto.

**Nota:** todos os dados são fictícios e foram gerados para fins educacionais. Os resultados não representam uma empresa real.

## Objetivos

- Modelar um banco de dados relacional.
- Praticar consultas SQL e agregações no PostgreSQL.
- Analisar o comportamento mensal e anual das vendas.
- Comparar categorias de produtos.
- Calcular indicadores para apoiar decisões de negócio.
- Documentar o processo analítico de forma reproduzível.

## Tecnologias utilizadas

- PostgreSQL 17
- SQL
- Git e GitHub

**Próximas etapas planejadas:** Python, Pandas e visualização de dados.

## Estrutura do banco de dados

O banco `analise_vendas` possui quatro tabelas:

| Tabela | Descrição |
|---|---|
| `clientes` | Cadastro de clientes fictícios |
| `produtos` | Catálogo de produtos, categorias e preços |
| `pedidos` | Data, cliente e status dos pedidos |
| `itens_pedido` | Produtos, quantidades, preços e descontos de cada pedido |

As tabelas utilizam chaves primárias, chaves estrangeiras, restrições de integridade e índices.

## Volume de dados

| Entidade | Registros |
|---|---:|
| Clientes | 1.000 |
| Produtos | 50 |
| Pedidos | 10.000 |
| Itens de pedidos | 25.000 |
| **Total** | **36.050** |

Os pedidos abrangem janeiro de 2025 a dezembro de 2026.

## Análises SQL desenvolvidas

1. **Pedidos por mês:** distribuição dos pedidos por status.
2. **Faturamento e ticket médio:** indicadores mensais dos pedidos concluídos.
3. **Faturamento por categoria:** comparação do faturamento, das unidades vendidas e dos pedidos com itens de cada categoria.
4. **Comparação anual:** análise do número de pedidos concluídos, faturamento e ticket médio.
5. **Variação mensal entre anos:** comparação do faturamento de cada mês de 2026 com o mesmo mês de 2025.

## Resultados iniciais

- Foram gerados 10.000 pedidos e 25.000 itens.
- A base possui 9.100 pedidos concluídos.
- A categoria Livros apresentou o maior faturamento na análise inicial.
- Os indicadores anuais apresentaram pequenas variações entre 2025 e 2026.
- As comparações mensais permitiram identificar oscilações positivas e negativas.

Os resultados são descritivos e refletem as regras utilizadas na geração dos dados. Não permitem atribuir causas às variações nem generalizar conclusões para empresas reais.

## Limitações

- Os dados são sintéticos, não transações reais.
- A geração matemática pode criar padrões artificiais.
- Os indicadores dependem dos preços, quantidades, descontos e status definidos nos scripts.
- O faturamento calculado considera os itens dos pedidos concluídos após os descontos cadastrados. Não equivale necessariamente à receita contábil líquida de uma empresa.

## Como executar

### Pré-requisitos

- PostgreSQL instalado e em execução.
- Cliente `psql` disponível no terminal.

### 1. Criar o banco

Conecte-se ao PostgreSQL e execute:

```sql
CREATE DATABASE analise_vendas;
```

### 2. Criar as tabelas

Na pasta do projeto, execute no PowerShell:

```powershell
psql -U postgres -h localhost -p 5432 -d analise_vendas -f sql\01_create_tables.sql
```

### 3. Gerar os dados

```powershell
psql -U postgres -h localhost -p 5432 -d analise_vendas -f sql\02_generate_data.sql
```

### 4. Executar as análises

```powershell
psql -U postgres -h localhost -p 5432 -d analise_vendas -f sql\03_analysis_queries.sql
```

**Atenção:** o script de geração foi desenvolvido para uma base vazia. Execute-o apenas uma vez por carga, para evitar duplicações e conflitos.

## Próximas melhorias

- Explorar os dados com Python e Pandas.
- Criar gráficos para os indicadores.
- Investigar a qualidade e os padrões dos dados.
- Desenvolver um dashboard.
- Ampliar as análises de clientes e produtos.

## Autor

**Vitor Morais**

Estudante de Engenharia de Computação no IFMG — Campus Bambuí, com interesse em Análise de Dados, desenvolvimento de software e uso de tecnologia para apoiar decisões.