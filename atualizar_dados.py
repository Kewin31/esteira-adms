import pandas as pd
import requests
from shareplum import Site
from shareplum import Office365
import os

# Pegando as credenciais dos Secrets do GitHub
usuario = os.getenv('SHAREPOINT_USER')
senha = os.getenv('SHAREPOINT_PASSWORD')
site_url = os.getenv('SHAREPOINT_SITE')
lista_nome = os.getenv('SHAREPOINT_LIST')

# Conectar ao SharePoint
authcookie = Office365(site_url, username=usuario, password=senha).GetCookies()
site = Site(site_url, authcookie=authcookie)

# Buscar dados da lista
lista = site.List(lista_nome)
dados = lista.GetListItems()

# Converter para DataFrame
df = pd.DataFrame(dados)

# Salvar como Excel no repositório (na pasta que seu Streamlit lê)
df.to_excel('dados/dashboard.xlsx', index=False)

print("✅ Dados atualizados com sucesso!")
