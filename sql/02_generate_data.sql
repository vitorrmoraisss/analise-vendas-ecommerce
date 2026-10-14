-- ============================================================
-- Projeto: Analise de Vendas de E-commerce
-- Arquivo: 02_generate_data.sql
-- Banco: analise_vendas
-- Objetivo: Gerar dados ficticios e reproduziveis
-- Periodo: Janeiro/2025 a Dezembro/2026
-- ============================================================

BEGIN;

-- 1. Gerar 1.000 clientes ficticios
INSERT INTO clientes (nome, cidade, estado, data_cadastro)
SELECT
    'Cliente ' || LPAD(g::TEXT, 4, '0'),
    (ARRAY[
        'Belo Horizonte',
        'Bambui',
        'Sao Paulo',
        'Rio de Janeiro',
        'Brasilia',
        'Curitiba',
        'Goiania',
        'Uberlandia',
        'Campinas',
        'Salvador'
    ])[1 + ((g - 1) % 10)],
    (ARRAY[
        'MG', 'MG', 'SP', 'RJ', 'DF',
        'PR', 'GO', 'MG', 'SP', 'BA'
    ])[1 + ((g - 1) % 10)],
    DATE '2024-01-01' + ((g * 7) % 730)
FROM generate_series(1, 1000) AS g;


-- 2. Gerar 50 produtos ficticios
INSERT INTO produtos (nome, categoria, preco_atual)
SELECT
    'Produto ' || LPAD(g::TEXT, 3, '0'),
    (ARRAY[
        'Eletronicos',
        'Casa',
        'Esporte',
        'Moda',
        'Livros'
    ])[1 + ((g - 1) % 5)],
    ROUND((20 + ((g * 37) % 980))::NUMERIC, 2)
FROM generate_series(1, 50) AS g;


-- 3. Gerar 10.000 pedidos
-- O volume mensal varia para permitir analises temporais.
WITH pedidos_base AS (
    SELECT
        g,
        (
            DATE '2025-01-01'
            + (
                (
                    (g * 37 + (g / 100) * 13) % 730
                )::INTEGER
            )
        ) AS dia_pedido,
        1 + ((g * 73) % 1000) AS id_cliente,
        CASE
            WHEN g % 100 < 4 THEN 'cancelado'
            WHEN g % 100 < 7 THEN 'pendente'
            WHEN g % 100 < 9 THEN 'devolvido'
            ELSE 'concluido'
        END AS status
    FROM generate_series(1, 10000) AS g
)
INSERT INTO pedidos (id_cliente, data_pedido, status)
SELECT
    id_cliente,
    dia_pedido::TIMESTAMP
        + MAKE_INTERVAL(
            hours => (g % 24)::INTEGER,
            mins => ((g * 7) % 60)::INTEGER
        ),
    status
FROM pedidos_base
ORDER BY g;


-- 4. Gerar de 1 a 4 itens por pedido
-- Os precos e descontos sao registrados no momento da compra.
INSERT INTO itens_pedido (
    id_pedido,
    id_produto,
    quantidade,
    preco_unitario,
    desconto
)
SELECT
    p.id_pedido,
    1 + ((p.id_pedido * 17 + item.n * 11) % 50),
    1 + ((p.id_pedido + item.n) % 4),
    pr.preco_atual,
    CASE
        WHEN (p.id_pedido + item.n) % 10 = 0 THEN 10
        WHEN (p.id_pedido + item.n) % 7 = 0 THEN 5
        ELSE 0
    END
FROM pedidos AS p
CROSS JOIN LATERAL generate_series(
    1,
    1 + (p.id_pedido % 4)
) AS item(n)
JOIN produtos AS pr
    ON pr.id_produto =
       1 + ((p.id_pedido * 17 + item.n * 11) % 50);


COMMIT;


-- 5. Resumo da carga
SELECT 'clientes' AS tabela, COUNT(*) AS registros
FROM clientes

UNION ALL

SELECT 'produtos', COUNT(*) FROM produtos

UNION ALL

SELECT 'pedidos', COUNT(*) FROM pedidos

UNION ALL

SELECT 'itens_pedido', COUNT(*) FROM itens_pedido;