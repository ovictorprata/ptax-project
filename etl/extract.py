import requests
import pandas as pd
from datetime import datetime, date

BASE_DAILY_URL_BCB_PTAX = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)"
BASE_RANGE_URL_BCB_PTAX = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='MM-DD-YYYY'&@dataFinalCotacao='MM-DD-YYYY'&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"

def format_date_for_api(date_obj: datetime) -> str:
    return date_obj.strftime('%m-%d-%Y')

def get_daily_dollar_rate(target_date: datetime) -> pd.DataFrame:
    formatted_date = format_date_for_api(target_date)
    print(f'Fetching exchange rate for {formatted_date}...')

    params = {
        '@dataCotacao': f"'{formatted_date}'",
        '$format': 'json',
        '$select': 'cotacaoCompra,cotacaoVenda,dataHoraCotacao'
    }

    try:
        response = requests.get(BASE_DAILY_URL_BCB_PTAX, params=params, timeout=15)
        response.raise_for_status()
        exchange_data = response.json()

        rates_list = exchange_data.get('value', [])
        if not rates_list:
            print(f'No exchange rate found for {formatted_date}')
            return pd.DataFrame()
        
        daily_rates_df = pd.DataFrame(rates_list)
        daily_rates_df['dataHoraCotacao'] = pd.to_datetime(daily_rates_df['dataHoraCotacao'], errors='coerce')
        daily_rates_df['dataCotacao'] = pd.to_datetime(target_date.date())
        daily_rates_df = daily_rates_df.sort_values(by='dataHoraCotacao', ascending=False).head(1)
        print(daily_rates_df.head())
        return daily_rates_df
    except requests.exceptions.RequestException as e:
        print(f'Request error when fetching PTAX for {target_date}. Error: {e}')
        return pd.DataFrame()
    except Exception as e:
        print(f'Unexpected error when fetching PTAX for {target_date}. Error: {e}')
        return pd.DataFrame()

def get_dollar_rate_for_period(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    try:
        api_start_date = format_date_for_api(start_date)
        api_end_date = format_date_for_api(end_date)
    except ValueError:
        print('Invalid date format. The correct format is YYYY-MM-DD.')
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
        rates_list = quotation_data.get('value', [])
        print(rates_list)
        return pd.DataFrame(rates_list)
    except Exception as e:
        print(f'An error occurred: {e}')
        return pd.DataFrame()

# Example usage
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 1, 5)
get_dollar_rate_for_period(start_date, end_date)