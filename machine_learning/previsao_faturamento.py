

import getpass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


# ============================================================
# CONFIGURACOES
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "analise_vendas",
    "user": "postgres",
}

PASTA_SAIDA = Path(__file__).resolve().parent


# ============================================================
# EXTRACAO DOS DADOS DO POSTGRESQL
# ============================================================

def extrair_faturamento_mensal():
    senha = getpass.getpass("Senha do PostgreSQL: ")

    consulta = """
        SELECT
            DATE_TRUNC('month', p.data_pedido)::date AS mes,
            SUM(
                ip.quantidade * ip.preco_unitario
                * (1 - ip.desconto / 100.0)
            ) AS faturamento
        FROM itens_pedido ip
        JOIN pedidos p
            ON p.id_pedido = ip.id_pedido
        WHERE p.status = 'concluido'
        GROUP BY DATE_TRUNC('month', p.data_pedido)
        ORDER BY mes;
    """

    with psycopg2.connect(
        **DB_CONFIG,
        password=senha
    ) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(consulta)
            linhas = cursor.fetchall()
            colunas = [item[0] for item in cursor.description]

    df = pd.DataFrame(linhas, columns=colunas)

    if df.empty:
        raise ValueError(
            "A consulta nao retornou dados de faturamento."
        )

    df["mes"] = pd.to_datetime(df["mes"])
    df["faturamento"] = pd.to_numeric(df["faturamento"])

    # Garantir a ordem cronologica e remover indices antigos
    df = df.sort_values("mes").reset_index(drop=True)

    return df


# ============================================================
# TREINAMENTO E AVALIACAO DO MODELO
# ============================================================

def avaliar_modelo(df):
    # Indice temporal: 0, 1, 2, ..., 23
    X = pd.DataFrame({
        "mes_indice": range(len(df))
    })

    y = df["faturamento"]

    # Reservar os ultimos 6 meses para teste
    limite_treino = len(df) - 6

    X_treino = X.iloc[:limite_treino]
    y_treino = y.iloc[:limite_treino]

    X_teste = X.iloc[limite_treino:]
    y_teste = y.iloc[limite_treino:]

    # Modelo de regressao linear
    modelo = make_pipeline(
        StandardScaler(),
        LinearRegression()
    )

    modelo.fit(X_treino, y_treino)

    previsoes_modelo = modelo.predict(X_teste)

    # Modelo de referencia: repetir o ultimo valor do treino
    previsoes_referencia = [
        y_treino.iloc[-1]
    ] * len(y_teste)

    # Comparacao dos valores reais e previstos
    resultados = pd.DataFrame({
        "mes": df["mes"].iloc[limite_treino:].values,
        "real": y_teste.values,
        "regressao_linear": previsoes_modelo,
        "referencia_ultimo_mes": previsoes_referencia,
    })

    # Erros absolutos e percentuais
    resultados["erro_absoluto"] = (
        resultados["real"] - resultados["regressao_linear"]
    ).abs()

    resultados["erro_percentual"] = (
        resultados["erro_absoluto"]
        / resultados["real"].abs().replace(0, float("nan"))
    ) * 100

    # Exibir tabela sem aplicar arredondamento a datas
    print("\n=== COMPARACAO: VALORES REAIS X PREVISTOS ===")

    tabela_resultados = resultados.copy()
    tabela_resultados["mes"] = (
        tabela_resultados["mes"].dt.strftime("%Y-%m-%d")
    )

    colunas_numericas = [
        "real",
        "regressao_linear",
        "referencia_ultimo_mes",
        "erro_absoluto",
        "erro_percentual",
    ]

    tabela_resultados[colunas_numericas] = (
        tabela_resultados[colunas_numericas].round(2)
    )

    print(tabela_resultados.to_string(index=False))

    # Salvar resultados da avaliacao
    arquivo_csv = PASTA_SAIDA / "resultados_avaliacao.csv"

    resultados.to_csv(
        arquivo_csv,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nResultados salvos em: {arquivo_csv}")

    # Calcular metricas
    mae_modelo = mean_absolute_error(
        y_teste,
        previsoes_modelo
    )

    rmse_modelo = mean_squared_error(
        y_teste,
        previsoes_modelo
    ) ** 0.5

    mae_referencia = mean_absolute_error(
        y_teste,
        previsoes_referencia
    )

    rmse_referencia = mean_squared_error(
        y_teste,
        previsoes_referencia
    ) ** 0.5

    erro_percentual_medio = (
        resultados["erro_percentual"].mean()
    )

    print("\n=== METRICAS DE AVALIACAO ===")
    print(f"MAE - Regressao linear: R$ {mae_modelo:,.2f}")
    print(f"RMSE - Regressao linear: R$ {rmse_modelo:,.2f}")
    print(f"MAE - Referencia: R$ {mae_referencia:,.2f}")
    print(f"RMSE - Referencia: R$ {rmse_referencia:,.2f}")
    print(
        "Erro percentual absoluto medio: "
        f"{erro_percentual_medio:.2f}%"
    )

    # Comparar o MAE com a referencia
    if mae_referencia > 0:
        melhoria = (
            (mae_referencia - mae_modelo) / mae_referencia
        ) * 100

        print(
            "Reducao do MAE em relacao a referencia: "
            f"{melhoria:.2f}%"
        )

    # Treinar novamente com todos os meses para previsao futura
    modelo_final = make_pipeline(
        StandardScaler(),
        LinearRegression()
    )

    modelo_final.fit(X, y)

    X_futuro = pd.DataFrame({
        "mes_indice": range(len(df), len(df) + 3)
    })

    previsoes_futuras = modelo_final.predict(X_futuro)

    meses_futuros = pd.date_range(
        start=df["mes"].max() + pd.offsets.MonthBegin(1),
        periods=3,
        freq="MS"
    )

    futuro = pd.DataFrame({
        "mes": meses_futuros,
        "faturamento_previsto": previsoes_futuras
    })

    print("\n=== PREVISAO EXPLORATORIA DOS PROXIMOS 3 MESES ===")

    tabela_futuro = futuro.copy()
    tabela_futuro["mes"] = (
        tabela_futuro["mes"].dt.strftime("%Y-%m-%d")
    )
    tabela_futuro["faturamento_previsto"] = (
        tabela_futuro["faturamento_previsto"].round(2)
    )

    print(tabela_futuro.to_string(index=False))

    return resultados, futuro


# ============================================================
# GERACAO DO GRAFICO
# ============================================================

def gerar_grafico(df, resultados, futuro):
    arquivo_saida = (
        PASTA_SAIDA / "previsao_faturamento.png"
    )

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["mes"],
        df["faturamento"],
        marker="o",
        label="Faturamento historico"
    )

    plt.plot(
        resultados["mes"],
        resultados["regressao_linear"],
        marker="s",
        linestyle="--",
        label="Regressao linear (teste)"
    )

    plt.plot(
        futuro["mes"],
        futuro["faturamento_previsto"],
        marker="^",
        linestyle=":",
        label="Previsao exploratoria"
    )

    plt.title("Faturamento mensal: historico e previsao")
    plt.xlabel("Mes")
    plt.ylabel("Faturamento (R$)")
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        arquivo_saida,
        dpi=200,
        bbox_inches="tight"
    )

    print(f"\nGrafico salvo em: {arquivo_saida}")

    plt.show()


# ============================================================
# EXECUCAO PRINCIPAL
# ============================================================

def main():
    try:
        df = extrair_faturamento_mensal()

        if len(df) < 8:
            print(
                "Dados insuficientes: sao necessarios pelo menos "
                "8 meses para esta avaliacao."
            )
            return

        print(f"\nMeses extraidos: {len(df)}")
        print(
            f"Periodo: {df['mes'].min():%Y-%m} "
            f"ate {df['mes'].max():%Y-%m}"
        )

        if len(df) < 12:
            print(
                "Aviso: ha menos de 12 meses de dados. "
                "Os resultados podem ser pouco confiaveis."
            )

        resultados, futuro = avaliar_modelo(df)

        gerar_grafico(
            df,
            resultados,
            futuro
        )

    except (psycopg2.Error, ValueError) as erro:
        print(f"\nErro ao acessar ou processar os dados: {erro}")

    except Exception as erro:
        print(f"\nErro inesperado: {erro}")


if __name__ == "__main__":
    main()
