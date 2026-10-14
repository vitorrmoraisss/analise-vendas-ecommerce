-- =====================================================
-- Projeto: Análise de Vendas de E-commerce
-- Banco: analise_vendas
-- Descrição: Criação das tabelas do projeto
-- =====================================================

CREATE TABLE clientes (
    id_cliente INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    data_cadastro DATE NOT NULL
);

CREATE TABLE produtos (
    id_produto INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    categoria VARCHAR(60) NOT NULL,
    preco_atual NUMERIC(12, 2) NOT NULL
        CHECK (preco_atual >= 0)
);

CREATE TABLE pedidos (
    id_pedido INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente INTEGER NOT NULL
        REFERENCES clientes(id_cliente),
    data_pedido TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL
        CHECK (
            status IN (
                'concluido',
                'cancelado',
                'pendente',
                'devolvido'
            )
        )
);

CREATE TABLE itens_pedido (
    id_item INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_pedido INTEGER NOT NULL
        REFERENCES pedidos(id_pedido),
    id_produto INTEGER NOT NULL
        REFERENCES produtos(id_produto),
    quantidade INTEGER NOT NULL
        CHECK (quantidade > 0),
    preco_unitario NUMERIC(12, 2) NOT NULL
        CHECK (preco_unitario >= 0),
    desconto NUMERIC(5, 2) NOT NULL DEFAULT 0
        CHECK (desconto >= 0 AND desconto <= 100)
);

-- Índices para auxiliar as consultas

CREATE INDEX idx_pedidos_data
    ON pedidos(data_pedido);

CREATE INDEX idx_pedidos_status
    ON pedidos(status);

CREATE INDEX idx_pedidos_cliente
    ON pedidos(id_cliente);

CREATE INDEX idx_itens_pedido_pedido
    ON itens_pedido(id_pedido);

CREATE INDEX idx_itens_pedido_produto
    ON itens_pedido(id_produto);