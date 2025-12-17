from typing import List, Dict


# =========================
# TABELA PROGRESSIVA INSS (empregado CLT)
# =========================
TABELA_INSS = [
    {"limite": 1518.00, "aliquota": 0.075},
    {"limite": 2793.88, "aliquota": 0.09},
    {"limite": 4190.83, "aliquota": 0.12},
    {"limite": 8157.41, "aliquota": 0.14},
]


# =========================
# TABELA OFICIAL IR (mensal)
# =========================
TABELA_IR = [
    {"limite": 2428.80, "aliquota": 0.0,   "deducao": 0.00},
    {"limite": 2826.65, "aliquota": 0.075, "deducao": 182.16},
    {"limite": 3751.05, "aliquota": 0.15,  "deducao": 394.16},
    {"limite": 4664.68, "aliquota": 0.225, "deducao": 675.49},
    {"limite": None,    "aliquota": 0.275, "deducao": 908.73},
]


# =========================
# CÁLCULO DO INSS
# =========================
def calcular_inss(salario_bruto: float) -> float:
    inss = 0.0
    limite_anterior = 0.0

    for faixa in TABELA_INSS:
        limite = faixa["limite"]
        aliquota = faixa["aliquota"]

        if salario_bruto > limite_anterior:
            base_faixa = min(salario_bruto, limite) - limite_anterior
            inss += base_faixa * aliquota
            limite_anterior = limite
        else:
            break

    return round(inss, 2)


# =========================
# BASE DE CÁLCULO IR
# =========================
def calcular_base_ir(salario_bruto: float, inss: float) -> float:
    return max(0.0, salario_bruto - inss)


# =========================
# FAIXA DO IR
# =========================
def encontrar_faixa_ir(base: float, tabela: List[Dict]) -> Dict:
    for faixa in tabela:
        limite = faixa["limite"]
        if limite is None or base <= limite:
            return faixa
    raise ValueError("Faixa de IR não encontrada")


# =========================
# CÁLCULO DO IR (OFICIAL)
# =========================
def calcular_ir(salario_bruto: float) -> float:
    inss = calcular_inss(salario_bruto)
    base_ir = calcular_base_ir(salario_bruto, inss)

    faixa = encontrar_faixa_ir(base_ir, TABELA_IR)
    aliquota = faixa["aliquota"]
    deducao = faixa["deducao"]

    ir = (base_ir * aliquota) - deducao
    return max(0.0, round(ir, 2))


# =========================
# EXEMPLO DE USO
# =========================
if __name__ == "__main__":
    salario_bruto = 9480.80

    inss = calcular_inss(salario_bruto)
    ir = calcular_ir(salario_bruto)
    salario_liquido = salario_bruto - inss - ir

    print(f"Salário bruto:   R$ {salario_bruto:.2f}")
    print(f"INSS:            R$ {inss:.2f}")
    print(f"Base IR:         R$ {salario_bruto - inss:.2f}")
    print(f"IR:              R$ {ir:.2f}")
    print(f"Salário líquido: R$ {salario_liquido:.2f}")
