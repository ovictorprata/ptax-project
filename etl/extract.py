import requests
import pandas as pd
from datetime import datetime, date

BASE_DAILY_URL_BCB_PTAX = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)"
BASE_RANGE_URL_BCB_PTAX = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='MM-DD-YYYY'&@dataFinalCotacao='MM-DD-YYYY'&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"

def format_date_for_api(data_obj: datetime) -> str:
    return data_obj.strftime('%m-%d-%Y')

def get_cotacao_dolar_diario(data_alvo: datetime) -> pd.DataFrame:
    data_formatada = format_date_for_api(data_alvo)
    print(f'Buscando cotação para {data_formatada}...')

    params = {
        '@dataCotacao': f"'{data_formatada}'",
        '$format': 'json',
        '$select': 'cotacaoCompra,cotacaoVenda,dataHoraCotacao'
    }

    try:
        response = requests.get(BASE_DAILY_URL_BCB_PTAX, params=params, timeout=15)
        response.raise_for_status()
        dados_cotacoes = response.json()

        lista_cotacoes = dados_cotacoes.get('value', [])
        if not lista_cotacoes:
            print(f'Nenhuma cotação encontrada para o dia {data_formatada}')
            return pd.DataFrame()
        
        df_cotacoes_dia = pd.DataFrame(lista_cotacoes)
        df_cotacoes_dia['dataHoraCotacao'] = pd.to_datetime(df_cotacoes_dia['dataHoraCotacao'], errors='coerce')
        df_cotacoes_dia['dataCotacao'] = pd.to_datetime(data_alvo.date())
        df_cotacoes_dia = df_cotacoes_dia.sort_values(by='dataHoraCotacao', ascending=False).head(1)
        print(df_cotacoes_dia.head())
    except requests.exceptions.RequestException as e:
        print(f'Erro de requisição ao buscar PTAX para {data_alvo}. Erro: {e}')
        return pd.DataFrame()
    except Exception as e:
        print(f'Erro de requisição ao buscar PTAX para {data_alvo}. Erro: {e}')
        return pd.DataFrame()


def get_cotacao_dolar_periodo(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    try:
        api_start_date = format_date_for_api(start_date)
        api_end_date = format_date_for_api(end_date)
    except ValueError:
        print(f'Formato de data inválido. O formato correto é YYYY-MM-DD.')
        return None
    
    try:
        url = (
            f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
            f"CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?"
            f"@dataInicial='{api_start_date}'&@dataFinalCotacao='{api_end_date}'&"
            f"$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"
        )
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        quotation_data = response.json()
        lista_cotacoes = quotation_data.get('value', [])
        print(lista_cotacoes)
    except Exception as e:
        print(f'Um erro foi encontrado: {e}')

data_inicio = datetime(2025, 1, 1)
data_fim = datetime(2025, 1, 5)
get_cotacao_dolar_periodo(data_inicio, data_fim)




