
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path

# Dados obtidos da consulta SQL no PostgreSQL
categorias = [
    "Livros",
    "Eletrônicos",
    "Moda",
    "Esporte",
    "Casa"
]

faturamento = [
    6506608.25,
    6198569.15,
    5951628.80,
    5508636.80,
    5191359.80
]

# Formatação dos valores em reais
def formatar_reais(valor, pos):
    valor_formatado = f"{valor:,.0f}"
    valor_formatado = valor_formatado.replace(",", ".")
    return f"R$ {valor_formatado}"

# Criar o gráfico
fig, ax = plt.subplots(figsize=(11, 6.5))

barras = ax.barh(categorias, faturamento)

# Maior faturamento no topo
ax.invert_yaxis()

# Valores ao lado das barras
for barra, valor in zip(barras, faturamento):
    ax.text(
        barra.get_width() + 60000,
        barra.get_y() + barra.get_height() / 2,
        f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        va="center",
        fontsize=10
    )

ax.set_title(
    "Faturamento por categoria",
    fontsize=18,
    fontweight="bold",
    pad=18
)

ax.set_xlabel("Faturamento (R$)", fontsize=11)
ax.xaxis.set_major_formatter(
    FuncFormatter(formatar_reais)
)

ax.grid(axis="x", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.text(
    0.01,
    0.01,
    "Fonte: projeto de análise de vendas | Dados sintéticos para fins de estudo",
    fontsize=9,
    color="dimgray"
)

plt.tight_layout(rect=[0, 0.05, 1, 1])

# Salvar a imagem na pasta do projeto
pasta_saida = Path(__file__).resolve().parent
arquivo_saida = pasta_saida / "faturamento_por_categoria.png"

plt.savefig(
    arquivo_saida,
    dpi=200,
    bbox_inches="tight"
)

print(f"Gráfico salvo em: {arquivo_saida}")

plt.show()
