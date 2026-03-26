import os
import argparse
from google.analytics.admin import AnalyticsAdminServiceClient
from google.analytics.admin_v1alpha.types import CustomDimension, CustomMetric
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

# =========================================================================
# SCRIPT GA4 - REGISTRO E PAINEL (CALCULADORA CLT)
# =========================================================================
# COMO AUTENTICAR NA API ANTES DE RODAR:
# 1. Acesse o Google Cloud Console (https://console.cloud.google.com/)
# 2. Crie ou selecione um Projeto.
# 3. Vá em "APIs e Serviços" -> "Biblioteca" e ative duas APIs:
#    - Google Analytics Admin API
#    - Google Analytics Data API
# 4. Vá em "Credenciais", crie uma "Conta de Serviço" (Service Account).
# 5. Crie uma chave (JSON) para essa conta e baixe para a pasta do projeto como 'credentials.json'.
# 6. No GA4, vá em "Administrador" > "Gerenciamento de Acesso" e adicione o email
#    da Conta de Serviço (ex: bot@...) que você criou com a permissão de "Editor" (ou Administrador).
# 7. Defina a variável de ambiente apontando para o arquivo json (já configurado no script abaixo).
# =========================================================================

from dotenv import load_dotenv

load_dotenv()
PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID")

def registrar_dimensoes_e_metricas():
    """
    Usa a Analytics Admin API para registrar os campos do form. 
    Sem fazer isso, o GA4 ignora os novos campos e eles não aparecem nem na UI e nem na extração!
    """
    client = AnalyticsAdminServiceClient()
    parent = f"properties/{PROPERTY_ID}"
    
    dimensoes_evento = [
        "calculation_type",
        "app_user_id",
        
        "salario_01_nome_usuario",
        
        "rescisao_01_nome_usuario",
        "rescisao_02_tipo_rescisao",
        "rescisao_04_dia_pagamento",
        "rescisao_05_data_inicio",
        "rescisao_06_data_fim",
        "rescisao_07_tem_ferias_vencidas",
        
        "restituicao_01_nome_usuario"
    ]
    
    print("\n--- REGISTRANDO DIMENSÕES PERSONALIZADAS ---")
    for param in dimensoes_evento:
        try:
            custom_dim = CustomDimension(
                parameter_name=param,
                display_name=f"{param.split('_')[0].upper()} {param.replace('_', ' ').title()}",
                scope=CustomDimension.DimensionScope.EVENT,
                description=f"Campo capturado do form para {param}"
            )
            client.create_custom_dimension(parent=parent, custom_dimension=custom_dim)
            print(f" Dimensão '{param}' criada com sucesso!")
        except Exception as e:
            if "already exists" in str(e).lower() or "409" in str(e):
                print(f" Dimensão '{param}' já existe.")
            else:
                print(f" Erro ao criar '{param}': {e}")
                
    metricas = [
        ("salario_receber", "Moeda Salario a Receber"),
        ("rescisao_receber", "Moeda Rescisao a Receber"),
        ("restituicao_receber", "Moeda Restituicao a Receber"),
        
        ("salario_02_salario_bruto", "Salario Bruto"),
        ("salario_03_num_dependentes", "Num Dependentes Salario"),
        ("salario_04_va_vr_mensal", "VA VR Mensal"),
        ("salario_05_bonus_anual", "Bonus Anual"),
        
        ("rescisao_03_salario", "Salario Rescisao"),
        
        ("restituicao_02_rendimentos", "Rendimentos Restituicao"),
        ("restituicao_03_previdencia_oficial", "Previdencia Oficial"),
        ("restituicao_04_irrf_retido", "IRRF Retido"),
        ("restituicao_05_previdencia_privada", "Previdencia Privada"),
        ("restituicao_06_num_dependentes", "Num Dependentes Restituicao"),
        ("restituicao_07_despesas_medicas", "Despesas Medicas"),
        ("restituicao_08_despesas_instrucao", "Despesas Instrucao"),
        ("restituicao_09_pensao_alimenticia", "Pensao Alimenticia")
    ]
    
    print("\n--- REGISTRANDO MÉTRICAS PERSONALIZADAS ---")
    for param, display in metricas:
        try:
            custom_metric = CustomMetric(
                parameter_name=param,
                display_name=display,
                scope=CustomMetric.MetricScope.EVENT,
                measurement_unit=CustomMetric.MeasurementUnit.STANDARD
            )
            client.create_custom_metric(parent=parent, custom_metric=custom_metric)
            print(f" Métrica '{param}' criada com sucesso!")
        except Exception as e:
            if "already exists" in str(e).lower() or "409" in str(e):
                print(f" Métrica '{param}' já existe.")
            else:
                print(f" Erro ao criar '{param}': {e}")

    print("\nRegistro concluído! Aguarde de 24h a 48h para os dados popularem os relatórios por completo.\n")


def gerar_painel_terminal():
    """
    Usa a Google Analytics Data API para extrair eventos e printar no terminal,
    simulando um Painel (Dashboard) rápido do que os usuários enviaram.
    """
    client = BetaAnalyticsDataClient()
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="eventName"),
            Dimension(name="customEvent:app_user_id"),
            Dimension(name="customEvent:calculation_type"),
            Dimension(name="customEvent:rescisao_02_tipo_rescisao")
        ],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="customEvent:salario_receber"),
            Metric(name="customEvent:rescisao_receber")
        ],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    )
    
    try:
        response = client.run_report(request)
        print("============= PAINEL: CÁLCULOS DOS ÚLTIMOS 7 DIAS =============")
        print(f"{'Usuário':<15} | {'Tipo de Cálculo':<15} | {'Motivo (Rescisão)':<20} | {'Salário Calc.':<12} | {'Rescisão Calc.':<12}")
        print("-" * 80)
        
        for row in response.rows:
            user_id = row.dimension_values[1].value
            calc_type = row.dimension_values[2].value
            motivo_resc = row.dimension_values[3].value
            motivo_str = motivo_resc if motivo_resc != '(not set)' else '-'
            
            sal_val = row.metric_values[1].value
            resc_val = row.metric_values[2].value
            
            print(f"{user_id:<15} | {calc_type:<15} | {motivo_str:<20} | R$ {sal_val:<9} | R$ {resc_val:<9}")
            
    except Exception as e:
        print(f"Erro ao gerar painel. (Você configurou o PROPERTY_ID e a Service Account corretamente?)\nErro: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automação do GA4 da Calculadora")
    parser.add_argument("--setup", action="store_true", help="Cria as dimensões de form no GA4 via Admin API (Rodar apenas uma vez)")
    parser.add_argument("--painel", action="store_true", help="Gera um relatório rápido dos envios no Terminal via Data API")
    args = parser.parse_args()

    if args.setup:
        registrar_dimensoes_e_metricas()
    elif args.painel:
        gerar_painel_terminal()
    else:
        print("Uso: python ga4_painel.py --setup   (para criar os campos na API do Google Analytics)")
        print("     python ga4_painel.py --painel  (para ver a extração de relatório)")
