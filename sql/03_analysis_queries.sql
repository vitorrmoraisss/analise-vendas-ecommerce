-- =====================================================
-- Analise 1: Quantidade de pedidos por mes
-- Objetivo: Investigar variacoes temporais
-- =====================================================

SELECT
    DATE_TRUNC('month', data_pedido)::DATE AS mes,
    COUNT(*) AS quantidade_pedidos,
    COUNT(*) FILTER (
        WHERE status = 'concluido'
    ) AS pedidos_concluidos,
    COUNT(*) FILTER (
        WHERE status = 'cancelado'
    ) AS pedidos_cancelados,
    COUNT(*) FILTER (
        WHERE status = 'pendente'
    ) AS pedidos_pendentes,
    COUNT(*) FILTER (
        WHERE status = 'devolvido'
    ) AS pedidos_devolvidos
FROM pedidos
GROUP BY DATE_TRUNC('month', data_pedido)
ORDER BY mes;






-- =====================================================
-- Analise 2: Faturamento e ticket medio por mes
-- Considera apenas pedidos concluidos
-- =====================================================

WITH vendas_por_pedido AS (
    SELECT
        p.id_pedido,
        DATE_TRUNC('month', p.data_pedido)::DATE AS mes,
        SUM(
            ip.quantidade
            * ip.preco_unitario
            * (1 - ip.desconto / 100.0)
        ) AS valor_pedido
    FROM pedidos p
    JOIN itens_pedido ip
        ON ip.id_pedido = p.id_pedido
    WHERE p.status = 'concluido'
    GROUP BY
        p.id_pedido,
        DATE_TRUNC('month', p.data_pedido)::DATE
)
SELECT
    mes,
    COUNT(*) AS pedidos_concluidos,
    ROUND(SUM(valor_pedido), 2) AS faturamento,
    ROUND(AVG(valor_pedido), 2) AS ticket_medio
FROM vendas_por_pedido
GROUP BY mes
ORDER BY mes;






-- =====================================================
-- Analise 3: Faturamento por categoria de produto
-- Considera apenas pedidos concluidos
-- =====================================================

SELECT
    pr.categoria,
    COUNT(DISTINCT p.id_pedido) AS pedidos,
    SUM(ip.quantidade) AS unidades_vendidas,
    ROUND(
        SUM(
            ip.quantidade
            * ip.preco_unitario
            * (1 - ip.desconto / 100.0)
        ),
        2
    ) AS faturamento
FROM pedidos p
JOIN itens_pedido ip
    ON ip.id_pedido = p.id_pedido
JOIN produtos pr
    ON pr.id_produto = ip.id_produto
WHERE p.status = 'concluido'
GROUP BY pr.categoria
ORDER BY faturamento DESC;





-- =====================================================
-- Analise 4: Comparacao anual de vendas
-- Considera apenas pedidos concluidos
-- =====================================================

WITH vendas_por_pedido AS (
    SELECT
        p.id_pedido,
        EXTRACT(YEAR FROM p.data_pedido)::INTEGER AS ano,
        SUM(
            ip.quantidade
            * ip.preco_unitario
            * (1 - ip.desconto / 100.0)
        ) AS valor_pedido
    FROM pedidos p
    JOIN itens_pedido ip
        ON ip.id_pedido = p.id_pedido
    WHERE p.status = 'concluido'
    GROUP BY
        p.id_pedido,
        EXTRACT(YEAR FROM p.data_pedido)::INTEGER
)
SELECT
    ano,
    COUNT(*) AS pedidos_concluidos,
    ROUND(SUM(valor_pedido), 2) AS faturamento,
    ROUND(AVG(valor_pedido), 2) AS ticket_medio
FROM vendas_por_pedido
GROUP BY ano
ORDER BY ano;





-- Analise 5: Comparacao mensal entre 2025 e 2026

WITH vendas_mensais AS (
    SELECT
        EXTRACT(YEAR FROM p.data_pedido)::INTEGER AS ano,
        EXTRACT(MONTH FROM p.data_pedido)::INTEGER AS mes,
        COUNT(DISTINCT p.id_pedido) AS pedidos,
        SUM(
            ip.quantidade
            * ip.preco_unitario
            * (1 - ip.desconto / 100.0)
        ) AS faturamento
    FROM pedidos p
    JOIN itens_pedido ip
        ON ip.id_pedido = p.id_pedido
    WHERE p.status = 'concluido'
      AND p.data_pedido >= DATE '2025-01-01'
      AND p.data_pedido < DATE '2027-01-01'
    GROUP BY
        EXTRACT(YEAR FROM p.data_pedido),
        EXTRACT(MONTH FROM p.data_pedido)
)
SELECT
    a.mes,
    ROUND(a.faturamento, 2) AS faturamento_2025,
    ROUND(b.faturamento, 2) AS faturamento_2026,
    ROUND(
        100.0 * (b.faturamento - a.faturamento)
        / NULLIF(a.faturamento, 0),
        2
    ) AS variacao_percentual
FROM vendas_mensais a
JOIN vendas_mensais b
    ON b.mes = a.mes
   AND b.ano = 2026
WHERE a.ano = 2025
ORDER BY a.mes;

