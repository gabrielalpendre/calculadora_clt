from calculos import calcular_inss, calcular_irrf


def sugerir_salario_pj(salario_bruto: float, bonus_anual: float, va_vr_mensal: float):
    """
    Calcula um salário PJ sugerido com base em um pacote de remuneração CLT.
    """
    salario_anual = salario_bruto * 12
    decimo_terceiro = salario_bruto
    terco_ferias = salario_bruto / 3
    fgts_anual = salario_anual * 0.08
    va_vr_anual = va_vr_mensal * 12

    total_anual_clt = (
        salario_anual
        + decimo_terceiro
        + terco_ferias
        + fgts_anual
        + va_vr_anual
        + bonus_anual
    )

    salario_pj_sugerido = total_anual_clt / 12

    calculo = (
        f"  Salário Anual (12x): R$ {salario_anual:.2f}\n"
        f"+ 13º Salário: R$ {decimo_terceiro:.2f}\n"
        f"+ 1/3 de Férias: R$ {terco_ferias:.2f}\n"
        f"+ FGTS Anual (8%): R$ {fgts_anual:.2f}\n"
        f"+ VA/VR Anual (12x): R$ {va_vr_anual:.2f}\n"
        f"+ Bônus/PLR Anual: R$ {bonus_anual:.2f}\n"
        f"--------------------------------------------------\n"
        f"= Total Anualizado CLT: R$ {total_anual_clt:.2f}\n"
        f"÷ 12 meses\n"
        f"--------------------------------------------------\n"
        f"= Salário PJ Mensal Sugerido: R$ {salario_pj_sugerido:.2f}"
    )

    return {"valor": salario_pj_sugerido, "calculo": calculo}


def calcular_salario_liquido(salario_bruto: float, num_dependentes: int = 0, bonus_anual: float = 0, va_vr_mensal: float = 0):
    """
    Calcula o salário líquido mensal a partir do salário bruto,
    reutilizando as funções de cálculo de imposto.
    """
    # 1. Calcular INSS sobre o salário bruto
    inss_detalhe = calcular_inss(salario_bruto, tipo_verba="Salário Bruto")
    inss_valor = inss_detalhe["valor"]

    # 2. Calcular a base de cálculo para o IRRF
    # Base IRRF = Salário Bruto - Desconto INSS - (Dependentes * dedução)
    base_calculo_irrf = salario_bruto - inss_valor

    # 3. Calcular IRRF
    irrf_detalhe = calcular_irrf(
        base_calculo_irrf, num_dependentes, tipo_verba="Salário Bruto"
    )
    irrf_valor = irrf_detalhe["valor"]

    # 4. Calcular o salário líquido
    salario_liquido = salario_bruto - inss_valor - irrf_valor

    # 5. Calcular sugestão PJ
    sugestao_pj = sugerir_salario_pj(salario_bruto, bonus_anual, va_vr_mensal)

    return {
        "Salário Bruto": {"valor": salario_bruto, "calculo": "Valor base informado."},
        "(-) Desconto INSS": inss_detalhe,
        "(-) Desconto IRRF": irrf_detalhe,
        "Salário Líquido": {"valor": salario_liquido, "calculo": f"Salário Bruto (R$ {salario_bruto:.2f}) - INSS (R$ {inss_valor:.2f}) - IRRF (R$ {irrf_valor:.2f})"},
        "Sugestão Salário PJ": sugestao_pj,
    }