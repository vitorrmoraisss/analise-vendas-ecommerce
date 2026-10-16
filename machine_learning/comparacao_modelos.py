
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg2
import getpass
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing


# Configuracoes do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "analise_vendas",
    "user": "postgres",
    "password": getpass.getpass("Digite a senha do PostgreSQL: "),
}

# Arquivos de saida
PASTA_SAIDA = Path(__file__).resolve().parent
ARQUIVO_CSV = PASTA_SAIDA / "comparacao_resultados.csv"
ARQUIVO_GRAFICO = PASTA_SAIDA / "comparacao_modelos.png"

# Quantidade de meses reservados para teste
MESES_TESTE = 6


def extrair_faturamento_mensal():
    """Extrai o faturamento mensal dos pedidos concluidos."""

    consulta = """
        SELECT
            DATE_TRUNC('month', p.data_pedido)::date AS mes,
            SUM(
                ip.quantidade
                * ip.preco_unitario
                * (1 - COALESCE(ip.desconto, 0) / 100.0)
            ) AS faturamento
        FROM pedidos p
        JOIN itens_pedido ip
            ON ip.id_pedido = p.id_pedido
        WHERE p.status = 'concluido'
        GROUP BY DATE_TRUNC('month', p.data_pedido)
        ORDER BY mes;
    """

    conexao = psycopg2.connect(**DB_CONFIG)

    try:
        with conexao.cursor() as cursor:
            cursor.execute(consulta)
            resultados = cursor.fetchall()
    finally:
        conexao.close()

    dados = pd.DataFrame(
        resultados,
        columns=["mes", "faturamento"],
    )

    dados["mes"] = pd.to_datetime(dados["mes"])
    dados["faturamento"] = pd.to_numeric(
        dados["faturamento"]
    )

    # Garante a sequencia mensal completa
    dados = dados.set_index("mes").sort_index()
    dados = dados.asfreq("MS")

    if dados["faturamento"].isna().any():
        raise ValueError(
            "Existem meses sem faturamento. "
            "Verifique os dados antes de continuar."
        )

    return dados["faturamento"]


def calcular_metricas(real, previsto):
    """Calcula MAE, RMSE e erro percentual absoluto medio."""

    mae = mean_absolute_error(real, previsto)
    rmse = np.sqrt(mean_squared_error(real, previsto))

    denominador = np.abs(np.asarray(real, dtype=float))
    erros = np.abs(
        np.asarray(real, dtype=float)
        - np.asarray(previsto, dtype=float)
    )

    mape = np.mean(erros / denominador) * 100

    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE (%)": mape,
    }


def main():
    faturamento = extrair_faturamento_mensal()

    if len(faturamento) <= MESES_TESTE:
        raise ValueError(
            "Nao ha meses suficientes para treinamento e teste."
        )

    treino = faturamento.iloc[:-MESES_TESTE]
    teste = faturamento.iloc[-MESES_TESTE:]

    print(f"Meses extraidos: {len(faturamento)}")
    print(
        f"Periodo: {faturamento.index.min():%Y-%m} "
        f"ate {faturamento.index.max():%Y-%m}"
    )
    print(f"Meses para treinamento: {len(treino)}")
    print(f"Meses para teste: {len(teste)}")

    # Modelo 1: regressao linear
    x_treino = np.arange(len(treino)).reshape(-1, 1)
    x_teste = np.arange(
        len(treino), len(treino) + len(teste)
    ).reshape(-1, 1)

    modelo_linear = LinearRegression()
    modelo_linear.fit(x_treino, treino.values)
    previsao_linear = modelo_linear.predict(x_teste)

    # Modelo 2: Holt com tendencia aditiva
    modelo_holt = ExponentialSmoothing(
        treino,
        trend="add",
        damped_trend=True,
        seasonal=None,
        initialization_method="estimated",
    )

    ajuste_holt = modelo_holt.fit(optimized=True)
    previsao_holt = ajuste_holt.forecast(len(teste)).values

    # Modelo de referencia: ultimo valor do treinamento
    previsao_referencia = np.repeat(
        treino.iloc[-1],
        len(teste),
    )

    # Comparacao das previsoes
    resultados = pd.DataFrame(
        {
            "mes": teste.index,
            "real": teste.values,
            "regressao_linear": previsao_linear,
            "holt": previsao_holt,
            "referencia": previsao_referencia,
        }
    )

    resultados.to_csv(
        ARQUIVO_CSV,
        index=False,
        float_format="%.2f",
    )

    modelos = {
        "Regressao Linear": previsao_linear,
        "Holt": previsao_holt,
        "Referencia": previsao_referencia,
    }

    linhas_metricas = []

    for nome, previsoes in modelos.items():
        metricas = calcular_metricas(
            teste.values,
            previsoes,
        )
        linhas_metricas.append(
            {"Modelo": nome, **metricas}
        )

    tabela_metricas = pd.DataFrame(linhas_metricas)
    tabela_metricas = tabela_metricas.sort_values("MAE")

    print("\n=== COMPARACAO DE MODELOS ===")
    print(
        tabela_metricas.to_string(
            index=False,
            formatters={
                "MAE": lambda v: f"R$ {v:,.2f}",
                "RMSE": lambda v: f"R$ {v:,.2f}",
                "MAPE (%)": lambda v: f"{v:.2f}%",
            },
        )
    )

    melhor_modelo = tabela_metricas.iloc[0]["Modelo"]
    print(f"\nMenor MAE: {melhor_modelo}")

    # Grafico dos valores reais e previstos
    plt.figure(figsize=(12, 6))
    plt.plot(
        teste.index,
        teste.values,
        marker="o",
        linewidth=2,
        label="Faturamento real",
    )
    plt.plot(
        teste.index,
        previsao_linear,
        marker="s",
        linestyle="--",
        label="Regressao linear",
    )
    plt.plot(
        teste.index,
        previsao_holt,
        marker="^",
        linestyle="--",
        label="Holt",
    )
    plt.plot(
        teste.index,
        previsao_referencia,
        linestyle=":",
        label="Modelo de referencia",
    )

    plt.title("Comparacao de modelos - faturamento mensal")
    plt.xlabel("Mes")
    plt.ylabel("Faturamento (R$)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(ARQUIVO_GRAFICO, dpi=150)
    plt.close()

    print(f"\nCSV salvo em: {ARQUIVO_CSV}")
    print(f"Grafico salvo em: {ARQUIVO_GRAFICO}")


if __name__ == "__main__":
    main()
