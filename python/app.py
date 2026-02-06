from flask import Flask, render_template, request, Response
from calculos import (
    DadosEmpregado,
    TipoRescisao,
    calcular_rescisao,
    calcular_impostos,
    calcular_salario_liquido,
)
from datetime import datetime, timedelta
from weasyprint import HTML
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        tipo = TipoRescisao(request.form["tipo_rescisao"])
        data_inicio = datetime.strptime(request.form["data_inicio"], "%Y-%m-%d")

        if tipo == TipoRescisao.PEDIDO_DEMISSAO:
            data_solicitacao = datetime.strptime(request.form["data_solicitacao_demissao"], "%Y-%m-%d")
            cumprira_aviso = request.form.get("cumprira_aviso")
            if cumprira_aviso == "sim":
                data_fim = data_solicitacao + timedelta(days=30)
            else:
                data_saida_str = request.form.get("data_saida_pretendida")
                if data_saida_str:
                    data_fim = datetime.strptime(data_saida_str, "%Y-%m-%d")
                else:
                    data_fim = data_solicitacao
        else:
            data_fim = datetime.strptime(request.form["data_fim"], "%Y-%m-%d")

        dia_pagamento = int(request.form["dia_pagamento"])

        if data_fim.day >= dia_pagamento:
            data_inicio_saldo = data_fim.replace(day=dia_pagamento)
            dias_trabalhados_saldo = (data_fim - data_inicio_saldo).days + 1
        else:
            mes_anterior = data_fim - relativedelta(months=1)
            data_inicio_saldo = mes_anterior.replace(day=dia_pagamento)
            dias_trabalhados_saldo = (data_fim - data_inicio_saldo).days + 1

        meses_para_13 = data_fim.month
        if data_fim.day < 15:
            meses_para_13 -= 1

        if data_inicio.year == data_fim.year:
            meses_para_13 -= (data_inicio.month - 1)
            if data_inicio.day > 15:
                 meses_para_13 -=1

        meses_trabalhados_ferias = (relativedelta(data_fim, data_inicio).years * 12) + relativedelta(data_fim, data_inicio).months

        dias_aviso_devido = 0
        dias_aviso_cumprido = 0

        if tipo == TipoRescisao.PEDIDO_DEMISSAO:
            dias_aviso_devido = 30
            cumprira_aviso = request.form.get("cumprira_aviso")
            if cumprira_aviso == "sim":
                dias_aviso_cumprido = 30
            else:
                dias_aviso_cumprido = (data_fim - data_solicitacao).days
                dias_aviso_cumprido = max(0, min(dias_aviso_cumprido, 30))
        else:
            dias_aviso_devido = int(request.form.get("aviso_devido", 0))
            dias_aviso_cumprido = int(request.form.get("aviso_cumprido", 0))

        dados = DadosEmpregado(
            salario=float(request.form["salario"]),
            meses_trabalhados_ferias=meses_trabalhados_ferias,
            meses_trabalhados_13=meses_para_13,
            dias_trabalhados_saldo=dias_trabalhados_saldo,
            dias_aviso_devido=dias_aviso_devido,
            dias_aviso_cumprido=dias_aviso_cumprido,
            ferias_vencidas=1
            if "tem_ferias_vencidas" in request.form and (data_fim - data_inicio).days > 365
            else 0,
            ferias_em_dobro=False,
        )

        verbas = calcular_rescisao(dados, tipo)
        impostos = calcular_impostos(verbas, dados.salario)

        resultado = {**verbas, **impostos}
        total_bruto = verbas.get("Total Bruto", {}).get("valor", 0)
        total_descontos_impostos = impostos.get("Total de Descontos", {}).get("valor", 0)
        desconto_aviso = verbas.get("Aviso prévio", {}).get("valor", 0) if verbas.get("Aviso prévio", {}).get("valor", 0) < 0 else 0
        liquido = total_bruto + desconto_aviso - total_descontos_impostos
        resultado["Líquido a Receber"] = {"valor": liquido, "calculo": f"Total Bruto (R$ {total_bruto:.2f}) - Descontos (R$ {total_descontos_impostos + abs(desconto_aviso):.2f})"}
        return render_template("calculo_rescisao.html", resultado=resultado)

    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    return render_template("formulario_rescisao.html", data_inicio=data_inicio_str, data_fim=data_fim_str)

@app.route("/salario-mensal", methods=["GET", "POST"])
def salario_mensal():
    resultado = None
    if request.method == "POST":
        salario_bruto = float(request.form.get("salario_bruto", 0))
        num_dependentes = int(request.form.get("num_dependentes", 0))
        bonus_anual = float(request.form.get("bonus_anual", 0))
        va_vr_mensal = float(request.form.get("va_vr_mensal", 0))
        if salario_bruto > 0:
            resultado = calcular_salario_liquido(salario_bruto, num_dependentes, bonus_anual, va_vr_mensal)

    return render_template("remuneracao_mensal.html", resultado=resultado)

@app.route("/export/rescisao/pdf", methods=["POST"])
def export_rescisao_pdf():
    form_data = request.form
    tipo = TipoRescisao(form_data["tipo_rescisao"])

    dados = DadosEmpregado(
        salario=float(form_data["salario"]),
        meses_trabalhados_ferias=int(form_data["meses_trabalhados_ferias"]),
        meses_trabalhados_13=int(form_data["meses_trabalhados_13"]),
        dias_trabalhados_saldo=int(form_data["dias_trabalhados_saldo"]),
        dias_aviso_devido=int(form_data["dias_aviso_devido"]),
        dias_aviso_cumprido=int(form_data["dias_aviso_cumprido"]),
        ferias_vencidas=int(form_data["ferias_vencidas"]),
        ferias_em_dobro=(form_data.get("ferias_em_dobro") == 'True'),
    )
    verbas = calcular_rescisao(dados, tipo)
    impostos = calcular_impostos(verbas, dados.salario)
    resultado = {**verbas, **impostos}
    total_bruto = verbas.get("Total Bruto", {}).get("valor", 0)
    total_descontos_impostos = impostos.get("Total de Descontos", {}).get("valor", 0)
    desconto_aviso = verbas.get("Aviso prévio", {}).get("valor", 0) if verbas.get("Aviso prévio", {}).get("valor", 0) < 0 else 0
    liquido = total_bruto + desconto_aviso - total_descontos_impostos
    resultado["Líquido a Receber"] = {"valor": liquido, "calculo": "..."}

    html = render_template("pdf_rescisao.html", resultado=resultado)
    pdf = HTML(string=html).write_pdf()
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=rescisao.pdf'})

@app.route("/export/salario-mensal/pdf", methods=["POST"])
def export_salario_mensal_pdf():
    salario_bruto = float(request.form.get("salario_bruto", 0))
    num_dependentes = int(request.form.get("num_dependentes", 0))
    bonus_anual = float(request.form.get("bonus_anual", 0))
    va_vr_mensal = float(request.form.get("va_vr_mensal", 0))
    
    resultado = calcular_salario_liquido(salario_bruto, num_dependentes, bonus_anual, va_vr_mensal)

    html = render_template("pdf_salario_mensal.html", resultado=resultado)
    pdf = HTML(string=html).write_pdf()
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=salario_mensal.pdf'})

if __name__ == "__main__":
    app.run(debug=False)
