from dataclasses import dataclass
from enum import Enum


class TipoRescisao(Enum):
    SEM_JUSTA_CAUSA = "sem_justa_causa"
    PEDIDO_DEMISSAO = "pedido_demissao"
    JUSTA_CAUSA = "justa_causa"
    ACORDO = "acordo"
    TERMINO_CONTRATO = "termino_contrato"


@dataclass
class DadosEmpregado:
    salario: float
    meses_trabalhados_ferias: int
    meses_trabalhados_13: int
    dias_trabalhados_saldo: int
    dias_aviso_devido: int
    dias_aviso_cumprido: int
    ferias_vencidas: int
    ferias_em_dobro: bool


def saldo_salario(salario, dias):
    valor = (salario / 30) * dias
    calculo = f"(Salário R$ {salario:.2f} / 30 dias) * {dias} dias trabalhados."
    return {"valor": valor, "calculo": calculo}


def aviso_previo(salario, devido, cumprido, tipo_rescisao):
    dias_a_pagar = devido - cumprido
    valor_dia = salario / 30
    valor = valor_dia * dias_a_pagar

    # Em pedido de demissão, o aviso não cumprido é SEMPRE um desconto.
    if tipo_rescisao == TipoRescisao.PEDIDO_DEMISSAO:
        valor *= -1
        calculo = f"Desconto de {abs(dias_a_pagar)} dias de aviso não cumprido. (R$ {salario:.2f} / 30) * {abs(dias_a_pagar)}."
    else:
        valor = max(0, valor)
        calculo = f"Aviso indenizado de {dias_a_pagar} dias. (R$ {salario:.2f} / 30) * {dias_a_pagar}."
    
    return {"valor": valor, "calculo": calculo}


def ferias_vencidas(salario, periodos, dobro):
    if periodos <= 0:
        return {"valor": 0, "calculo": "Nenhum período de férias vencidas."}
    base = salario * periodos
    calculo_base = f"Salário (R$ {salario:.2f}) * {periodos} período(s)"
    if dobro:
        base *= 2
        calculo_base += " (em dobro)"
    terco = base / 3
    valor = base + terco
    calculo = f"{calculo_base} + 1/3 sobre o valor (R$ {terco:.2f})."
    return {"valor": valor, "calculo": calculo}


def ferias_proporcionais(salario, meses):
    meses_validos = meses % 12 # Pega apenas os meses do período aquisitivo incompleto
    if meses_validos == 0:
        return {"valor": 0, "calculo": "Nenhum mês para férias proporcionais."}
    base = (salario / 12) * meses_validos
    terco = base / 3
    valor = base + terco
    calculo = f"({meses_validos}/12 avos de R$ {salario:.2f}) + 1/3 sobre o valor (R$ {terco:.2f})."
    return {"valor": valor, "calculo": calculo}


def decimo_terceiro(salario, meses):
    valor = (salario / 12) * meses
    calculo = f"{meses}/12 avos de R$ {salario:.2f}."
    return {"valor": valor, "calculo": calculo}


# =========================
# TABELAS DE IMPOSTO (Exemplos para 2025 - confirmar valores)
# =========================
TABELA_INSS = [
    {"limite": 1518.00, "aliquota": 0.075},
    {"limite": 2793.88, "aliquota": 0.09},
    {"limite": 4190.83, "aliquota": 0.12},
    {"limite": 8157.41, "aliquota": 0.14},
]

TABELA_IRRF = [
    {"limite": 2428.80, "aliquota": 0.0,   "deducao": 0.00},
    {"limite": 2826.65, "aliquota": 0.075, "deducao": 182.16},
    {"limite": 3751.05, "aliquota": 0.15,  "deducao": 394.16},
    {"limite": 4664.68, "aliquota": 0.225, "deducao": 675.49},
    {"limite": None,    "aliquota": 0.275, "deducao": 908.73},
]


def calcular_inss(base_calculo, tipo_verba=""):
    """Calcula o INSS de forma progressiva, faixa a faixa."""
    inss = 0.0
    limite_anterior = 0.0
    calculo_str = f"Cálculo progressivo sobre a base ({tipo_verba}) de R$ {base_calculo:.2f}:\n"

    for faixa in TABELA_INSS:
        limite = faixa["limite"]
        aliquota = faixa["aliquota"]

        if base_calculo > limite_anterior:
            base_faixa = min(base_calculo, limite) - limite_anterior
            valor_faixa = base_faixa * aliquota
            inss += valor_faixa
            calculo_str += f"  - Faixa até R$ {limite:.2f}: (R$ {base_faixa:.2f} * {aliquota*100}%) = R$ {valor_faixa:.2f}\n"
            limite_anterior = limite
        else:
            break

    return {"valor": round(inss, 2), "calculo": calculo_str.strip()}


def calcular_irrf(base_calculo, num_dependentes=0, tipo_verba=""):
    """Calcula o IRRF com base na tabela de 2025."""
    deducao_dependentes = 189.59 * num_dependentes
    base_irrf = base_calculo - deducao_dependentes

    aliquota, deducao = 0.0, 0.0
    for faixa in TABELA_IRRF:
        if faixa["limite"] is None or base_irrf <= faixa["limite"]:
            aliquota = faixa["aliquota"]
            deducao = faixa["deducao"]
            break

    valor = (base_irrf * aliquota) - deducao
    calculo = f"Base de cálculo ({tipo_verba}): R$ {base_calculo:.2f}. Base p/ IRRF (já deduzido INSS e dependentes): R$ {base_irrf:.2f}. Fórmula: (R$ {base_irrf:.2f} * {aliquota*100}%) - R$ {deducao:.2f}."
    return {"valor": max(0, round(valor, 2)), "calculo": calculo}


def calcular_impostos(verbas, salario_base):
    """
    Calcula os impostos (INSS, IRRF) sobre as verbas rescisórias.
    """
    # Base de cálculo para o INSS incide sobre Saldo de Salário e 13º.
    # Férias (vencidas ou proporcionais) não têm incidência de INSS.
    base_inss_mes = verbas.get("Saldo de salário", {}).get("valor", 0)
    base_inss_13 = verbas.get("13º salário proporcional", {}).get("valor", 0)

    inss_salario_detalhe = calcular_inss(base_inss_mes, "Saldo Salário")
    inss_13_detalhe = calcular_inss(base_inss_13, "13º")
    total_inss = inss_salario_detalhe["valor"] + inss_13_detalhe["valor"]

    # --- Cálculo do IRRF ---
    # O IRRF sobre o 13º é calculado separadamente (tributação exclusiva na fonte).
    base_irrf_13 = base_inss_13 - inss_13_detalhe["valor"] # Base do IRRF é o 13º bruto menos o INSS do 13º
    irrf_13_detalhe = calcular_irrf(base_irrf_13, tipo_verba="13º Salário")

    # O IRRF sobre as outras verbas (saldo de salário, férias) é calculado em conjunto.
    saldo_salario_valor = verbas.get("Saldo de salário", {}).get("valor", 0)
    ferias_vencidas_valor = verbas.get("Férias vencidas", {}).get("valor", 0)
    ferias_proporcionais_valor = verbas.get("Férias proporcionais", {}).get("valor", 0)
    total_ferias = ferias_vencidas_valor + ferias_proporcionais_valor

    base_calculo_irrf_mes = saldo_salario_valor + total_ferias

    base_irrf_mes = base_calculo_irrf_mes - inss_salario_detalhe["valor"] # Base do IRRF é a soma das verbas menos o INSS do salário

    # Cria um descritivo mais claro para a base de cálculo
    tipo_verba_detalhado = (
        f"Saldo Salário (R$ {saldo_salario_valor:.2f}) + Férias (R$ {total_ferias:.2f})"
    )
    irrf_mes_detalhe = calcular_irrf(base_irrf_mes, tipo_verba=tipo_verba_detalhado)
    total_irrf = irrf_13_detalhe["valor"] + irrf_mes_detalhe["valor"]

    # Aviso prévio indenizado tem INSS, mas não IRRF.
    # Para simplificar, não estamos tratando aqui, mas seria um próximo passo.

    descontos = {}
    if inss_salario_detalhe["valor"] > 0:
        descontos["(-) Desconto INSS sobre Saldo Salário"] = inss_salario_detalhe
    if inss_13_detalhe["valor"] > 0:
        descontos["(-) Desconto INSS sobre 13º"] = inss_13_detalhe
    if irrf_mes_detalhe["valor"] > 0:
        descontos["(-) Desconto IRRF sobre Salário/Férias"] = irrf_mes_detalhe
    if irrf_13_detalhe["valor"] > 0:
        descontos["(-) Desconto IRRF sobre 13º"] = irrf_13_detalhe

    if descontos:
        descontos["Total de Descontos"] = {"valor": total_inss + total_irrf, "calculo": "Soma de todos os descontos de INSS e IRRF."}

    return descontos

def calcular_rescisao(dados: DadosEmpregado, tipo: TipoRescisao):
    r = {}

    r["Saldo de salário"] = saldo_salario(dados.salario, dados.dias_trabalhados_saldo)

    if tipo != TipoRescisao.JUSTA_CAUSA:
        r["Férias vencidas"] = ferias_vencidas(
            dados.salario, dados.ferias_vencidas, dados.ferias_em_dobro
        )
        r["Férias proporcionais"] = ferias_proporcionais(
            dados.salario, dados.meses_trabalhados_ferias
        )
        r["13º salário proporcional"] = decimo_terceiro(
            dados.salario, dados.meses_trabalhados_13
        )
    else:
        r["Férias vencidas"] = {"valor": 0, "calculo": "Não aplicável para justa causa."}
        r["Férias proporcionais"] = {"valor": 0, "calculo": "Não aplicável para justa causa."}
        r["13º salário proporcional"] = {"valor": 0, "calculo": "Não aplicável para justa causa."}

    r["Aviso prévio"] = aviso_previo(
        dados.salario, dados.dias_aviso_devido, dados.dias_aviso_cumprido, tipo
    )

    # Filtra valores zerados para não poluir o resultado
    verbas_brutas = {k: v for k, v in r.items() if v.get("valor", 0) != 0}

    # Calcula o total bruto somando apenas os valores positivos
    total_bruto = sum(v["valor"] for v in verbas_brutas.values() if v["valor"] > 0)
    verbas_brutas["Total Bruto"] = {"valor": total_bruto, "calculo": "Soma de todas as verbas rescisórias."}

    return verbas_brutas
