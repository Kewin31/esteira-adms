# Na seção de Informações da Base de Dados, adicione:

# INFORMAÇÕES DA BASE DE DADOS
st.markdown("## 📊 Informações da Base de Dados")

if 'Criado' in df_uso.columns and not df_uso.empty:
    data_min = df_uso['Criado'].min()
    data_max = df_uso['Criado'].max()
    
    # Verificar duplicatas
    if 'Chamado' in df_uso.columns:
        duplicatas = df_uso['Chamado'].duplicated().sum()
        total_registros = len(df_uso)
        percentual_duplicatas = (duplicatas / total_registros * 100) if total_registros > 0 else 0
        
        # Cores baseadas no percentual
        if percentual_duplicatas > 20:
            cor_status = "#dc3545"
            emoji_status = "🔴"
            texto_status = "CRÍTICO"
        elif percentual_duplicatas > 5:
            cor_status = "#ffc107"
            emoji_status = "🟡"
            texto_status = "ALERTA"
        elif percentual_duplicatas > 0:
            cor_status = "#17a2b8"
            emoji_status = "🔵"
            texto_status = "ATENÇÃO"
        else:
            cor_status = "#28a745"
            emoji_status = "✅"
            texto_status = "OK"
    
    st.markdown(f"""
    <div class="info-base">
        <p style="margin: 0; font-weight: 600;">📅 Base atualizada em: {get_horario_brasilia()}</p>
        <p style="margin: 0.3rem 0 0 0; color: #6c757d;">
        Período coberto: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | 
        Total de registros: {len(df_uso):,}
        </p>
        {'<p style="margin: 0.3rem 0 0 0; color: ' + cor_status + '; font-weight: 600;">' + 
         emoji_status + ' Status Duplicatas: ' + texto_status + ' - ' + 
         str(duplicatas) + ' chamados duplicados (' + f'{percentual_duplicatas:.1f}' + '%)</p>' 
         if 'Chamado' in df_uso.columns and duplicatas > 0 else ''}
    </div>
    """, unsafe_allow_html=True)
