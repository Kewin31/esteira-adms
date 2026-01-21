# NOVA ABA: PERFORMANCE DOS SREs
with tab4:
    st.markdown('<div class="section-title-exec">🏆 PERFORMANCE DOS SREs</div>', unsafe_allow_html=True)
    
    if 'SRE' in df.columns and 'Status' in df.columns:
        # Filtros específicos para esta aba
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            # Filtrar por ano
            if 'Ano' in df.columns:
                anos_sre = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_sre = ['Todos'] + list(anos_sre)
                ano_sre = st.selectbox(
                    "📅 Filtrar por Ano:",
                    options=anos_opcoes_sre,
                    key="filtro_ano_sre"
                )
        
        with col_filtro2:
            # Filtrar por mês
            if 'Mês' in df.columns:
                meses_sre = sorted(df['Mês'].dropna().unique().astype(int))
                meses_opcoes_sre = ['Todos'] + [str(m) for m in meses_sre]
                mes_sre = st.selectbox(
                    "📆 Filtrar por Mês:",
                    options=meses_opcoes_sre,
                    key="filtro_mes_sre"
                )
        
        # Aplicar filtros
        df_sre = df.copy()
        
        if 'Ano' in df_sre.columns and ano_sre != 'Todos':
            df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
        
        if 'Mês' in df_sre.columns and mes_sre != 'Todos':
            df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
        
        # Filtrar apenas chamados sincronizados para análise SRE
        df_sincronizados = df_sre[df_sre['Status'] == 'Sincronizado'].copy()
        
        if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
            # 1. Ranking dos SREs que mais sincronizaram
            st.markdown("### 🥇 Ranking de Sincronizações por SRE")
            
            sincronizacoes_por_sre = df_sincronizados['SRE'].value_counts().reset_index()
            sincronizacoes_por_sre.columns = ['SRE', 'Sincronizações']
            sincronizacoes_por_sre = sincronizacoes_por_sre.sort_values('Sincronizações', ascending=False)
            
            # Criar título dinâmico
            titulo_sinc = "Top 10 SREs com Mais Sincronizações"
            if ano_sre != 'Todos':
                titulo_sinc += f" - {ano_sre}"
            if mes_sre != 'Todos':
                titulo_sinc += f"/{mes_sre}"
            
            # Criar gráfico de barras
            fig_sinc_sre = px.bar(
                sincronizacoes_por_sre.head(10),
                x='SRE',
                y='Sincronizações',
                title=titulo_sinc,
                text='Sincronizações',
                color='Sincronizações',
                color_continuous_scale='Greens'
            )
            
            fig_sinc_sre.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                marker_line_color='#218838',
                marker_line_width=1.5
            )
            
            fig_sinc_sre.update_layout(
                height=400,
                plot_bgcolor='white',
                xaxis_title="SRE",
                yaxis_title="Número de Sincronizações",
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig_sinc_sre, use_container_width=True)
            
            # 2. Dashboard comparativo dos SREs
            st.markdown("### 📊 Dashboard Comparativo dos SREs")
            
            # Explicação da métrica de eficiência
            with st.expander("ℹ️ **Sobre a métrica de eficiência**", expanded=False):
                st.markdown("""
                #### 📈 **Como calculamos a eficiência do SRE:**
                
                **Fórmula:** 
                ```
                Eficiência = (Revisões / Sincronizações) × 100
                ```
                
                **Interpretação:**
                - **Eficiência ALTA** → SRE encontra muitos erros (faz muitas revisões por sincronização)
                - **Eficiência BAIXA** → SRE encontra poucos erros (faz poucas revisões por sincronização)
                
                **Por que isso importa:**
                1. **Qualidade**: SREs que fazem mais revisões estão encontrando mais problemas
                2. **Prevenção**: Revisões evitam que erros cheguem em produção
                3. **Excelência**: SREs eficientes garantem entregas mais confiáveis
                
                **Exemplo prático:**
                - SRE A: 100 sincronizações, 25 revisões → Eficiência = 25%
                - SRE B: 100 sincronizações, 10 revisões → Eficiência = 10%
                - **SRE A é 2.5× mais eficiente** que SRE B!
                """)
            
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                # Tabela de performance
                performance_sre = pd.DataFrame()
                
                # Sincronizações
                performance_sre['SRE'] = sincronizacoes_por_sre['SRE']
                performance_sre['Sincronizações'] = sincronizacoes_por_sre['Sincronizações']
                
                # Revisões por SRE
                if 'Revisões' in df_sincronizados.columns:
                    revisoes_por_sre = df_sincronizados.groupby('SRE')['Revisões'].sum().reset_index()
                    revisoes_por_sre.columns = ['SRE', 'Revisões']
                    performance_sre = pd.merge(
                        performance_sre, 
                        revisoes_por_sre, 
                        on='SRE', 
                        how='left'
                    )
                    performance_sre['Revisões'] = performance_sre['Revisões'].fillna(0)
                
                # **CORREÇÃO: Calcular eficiência como Revisões/Sincronizações**
                if 'Revisões' in performance_sre.columns:
                    performance_sre['Eficiência'] = performance_sre.apply(
                        lambda x: (x['Revisões'] / x['Sincronizações'] * 100) 
                        if x['Sincronizações'] > 0 else 0,
                        axis=1
                    )
                    performance_sre['Eficiência'] = performance_sre['Eficiência'].round(2)
                
                # Ordenar por eficiência (maior é melhor)
                performance_sre = performance_sre.sort_values('Eficiência', ascending=False)
                
                # Criar DataFrame para exibição com tooltips
                display_performance = performance_sre.head(15).copy()
                
                # Adicionar ranking
                display_performance['Ranking'] = range(1, len(display_performance) + 1)
                
                st.dataframe(
                    display_performance[['Ranking', 'SRE', 'Sincronizações', 'Revisões', 'Eficiência']],
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Ranking": st.column_config.NumberColumn(
                            "#",
                            width="small",
                            help="Posição no ranking de eficiência"
                        ),
                        "SRE": st.column_config.TextColumn(
                            "SRE",
                            width="medium"
                        ),
                        "Sincronizações": st.column_config.NumberColumn(
                            "Sincronizações",
                            help="Número de chamados sincronizados pelo SRE",
                            format="%d"
                        ),
                        "Revisões": st.column_config.NumberColumn(
                            "Revisões",
                            help="Total de revisões feitas pelo SRE (quanto mais, melhor)",
                            format="%d"
                        ),
                        "Eficiência": st.column_config.NumberColumn(
                            "Eficiência (%)",
                            help="Cálculo: (Revisões / Sincronizações) × 100%\\n\\n"
                                 "📊 **Interpretação:**\\n"
                                 "• ALTA (>20%): Excelente detecção de erros\\n"
                                 "• MÉDIA (10-20%): Boa revisão\\n"
                                 "• BAIXA (<10%): Pode melhorar na detecção\\n\\n"
                                 "🔍 **Quanto MAIOR, MELHOR!**",
                            format="%.2f%%",
                            width="small"
                        )
                    }
                )
            
            with col_comp2:
                # Gráfico de eficiência
                if len(performance_sre) > 0:
                    st.markdown("#### 📈 Ranking de Eficiência (Top 10)")
                    
                    top10_eficiencia = performance_sre.head(10).copy()
                    
                    fig_eficiencia = go.Figure()
                    
                    fig_eficiencia.add_trace(go.Bar(
                        x=top10_eficiencia['SRE'],
                        y=top10_eficiencia['Eficiência'],
                        name='Eficiência',
                        text=[f"{v:.1f}%" for v in top10_eficiencia['Eficiência']],
                        textposition='outside',
                        marker_color='#1e3799',
                        marker_line_color='#0c2461',
                        marker_line_width=1.5,
                        opacity=0.8,
                        hovertemplate="<b>%{x}</b><br>"
                                    "Eficiência: %{y:.2f}%<br>"
                                    "Sincronizações: %{customdata[0]}<br>"
                                    "Revisões: %{customdata[1]}<br>"
                                    "<extra></extra>",
                        customdata=top10_eficiencia[['Sincronizações', 'Revisões']].values
                    ))
                    
                    # Adicionar linha de média
                    media_eficiencia = top10_eficiencia['Eficiência'].mean()
                    fig_eficiencia.add_hline(
                        y=media_eficiencia,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Média: {media_eficiencia:.1f}%",
                        annotation_position="top right"
                    )
                    
                    # Adicionar zonas de classificação
                    fig_eficiencia.add_hrect(
                        y0=20, y1=100,
                        fillcolor="rgba(144, 238, 144, 0.2)",
                        line_width=0,
                        annotation_text="Excelente (>20%)",
                        annotation_position="top left"
                    )
                    
                    fig_eficiencia.add_hrect(
                        y0=10, y1=20,
                        fillcolor="rgba(255, 255, 224, 0.2)",
                        line_width=0,
                        annotation_text="Bom (10-20%)"
                    )
                    
                    fig_eficiencia.add_hrect(
                        y0=0, y1=10,
                        fillcolor="rgba(255, 182, 193, 0.2)",
                        line_width=0,
                        annotation_text="Pode melhorar (<10%)",
                        annotation_position="bottom left"
                    )
                    
                    fig_eficiencia.update_layout(
                        title="Eficiência dos SREs (Revisões por Sincronização)",
                        xaxis_title="SRE",
                        yaxis_title="Eficiência (%)",
                        plot_bgcolor='white',
                        height=400,
                        showlegend=False,
                        margin=dict(t=50, b=50, l=50, r=50),
                        yaxis=dict(range=[0, min(100, top10_eficiencia['Eficiência'].max() * 1.2)])
                    )
                    
                    st.plotly_chart(fig_eficiencia, use_container_width=True)
                
                # Métricas gerais
                st.markdown("#### 📊 Métricas Gerais")
                
                total_sres = len(sincronizacoes_por_sre)
                media_sinc = sincronizacoes_por_sre['Sincronizações'].mean()
                
                col_met1, col_met2 = st.columns(2)
                with col_met1:
                    st.metric("Total de SREs", f"{total_sres}")
                
                with col_met2:
                    st.metric("Média de Sincronizações", f"{media_sinc:.1f}")
                
                if 'Revisões' in performance_sre.columns:
                    total_revisoes_sre = performance_sre['Revisões'].sum()
                    media_revisoes = performance_sre['Revisões'].mean()
                    
                    st.metric("Total de Revisões (SREs)", f"{int(total_revisoes_sre)}")
                    st.metric("Média de Revisões por SRE", f"{media_revisoes:.1f}")
            
            # 3. Evolução temporal do SRE líder em eficiência
            st.markdown("### 📈 Evolução Temporal do SRE Líder (Eficiência)")
            
            if not performance_sre.empty:
                sre_lider_eficiencia = performance_sre.iloc[0]['SRE']
                eficiencia_lider = performance_sre.iloc[0]['Eficiência']
                
                # Filtros para a evolução temporal
                col_evol1, col_evol2, col_evol3 = st.columns(3)
                
                with col_evol1:
                    # Seletor de período
                    periodo_selecionado = st.selectbox(
                        "Período:",
                        options=['Diário', 'Mensal', 'Anual'],
                        key="periodo_evolucao"
                    )
                
                with col_evol2:
                    # Seletor de ano para filtro
                    if 'Ano' in df_sincronizados.columns:
                        anos_lider = sorted(df_sincronizados['Ano'].dropna().unique().astype(int))
                        ano_lider = st.selectbox(
                            "Ano:",
                            options=['Todos'] + list(anos_lider),
                            key="ano_lider"
                        )
                
                with col_evol3:
                    # Seletor de SRE (pode escolher outro além do líder)
                    sres_disponiveis = sorted(df_sincronizados['SRE'].dropna().unique())
                    sre_selecionado = st.selectbox(
                        "Selecionar SRE:",
                        options=[sre_lider_eficiencia] + [s for s in sres_disponiveis if s != sre_lider_eficiencia],
                        key="sre_selecionado"
                    )
                
                # Filtrar dados para o SRE selecionado
                df_sre_selecionado = df_sincronizados[df_sincronizados['SRE'] == sre_selecionado].copy()
                
                if 'Ano' in df_sre_selecionado.columns and ano_lider != 'Todos':
                    df_sre_selecionado = df_sre_selecionado[df_sre_selecionado['Ano'] == int(ano_lider)]
                
                if not df_sre_selecionado.empty:
                    if periodo_selecionado == 'Diário':
                        # Agrupar por dia
                        df_sre_selecionado['Data'] = df_sre_selecionado['Criado'].dt.date
                        evolucao_sre = df_sre_selecionado.groupby('Data').agg({
                            'Revisões': 'sum'
                        }).reset_index()
                        evolucao_sre['Sincronizações'] = 1
                        evolucao_sre = evolucao_sre.groupby('Data').sum().reset_index()
                        eixo_x = 'Data'
                        titulo_evol = f"Evolução Diária de {sre_selecionado}"
                    
                    elif periodo_selecionado == 'Mensal':
                        # Agrupar por mês/ano
                        df_sre_selecionado['Ano_Mês'] = df_sre_selecionado['Criado'].dt.strftime('%Y-%m')
                        evolucao_sre = df_sre_selecionado.groupby('Ano_Mês').agg({
                            'Revisões': 'sum'
                        }).reset_index()
                        evolucao_sre['Sincronizações'] = df_sre_selecionado.groupby('Ano_Mês').size().values
                        eixo_x = 'Ano_Mês'
                        titulo_evol = f"Evolução Mensal de {sre_selecionado}"
                    
                    else:  # Anual
                        # Agrupar por ano
                        evolucao_sre = df_sre_selecionado.groupby('Ano').agg({
                            'Revisões': 'sum'
                        }).reset_index()
                        evolucao_sre['Sincronizações'] = df_sre_selecionado.groupby('Ano').size().values
                        eixo_x = 'Ano'
                        titulo_evol = f"Evolução Anual de {sre_selecionado}"
                    
                    # Calcular eficiência por período
                    evolucao_sre['Eficiência'] = (evolucao_sre['Revisões'] / evolucao_sre['Sincronizações'] * 100).round(2)
                    evolucao_sre = evolucao_sre.sort_values(eixo_x)
                    
                    # Criar gráfico de linha duplo
                    fig_evol_sre = go.Figure()
                    
                    # Adicionar linha de eficiência
                    fig_evol_sre.add_trace(go.Scatter(
                        x=evolucao_sre[eixo_x],
                        y=evolucao_sre['Eficiência'],
                        mode='lines+markers',
                        name='Eficiência (%)',
                        line=dict(color='#1e3799', width=3),
                        marker=dict(size=10, color='#0c2461'),
                        yaxis='y',
                        text=evolucao_sre['Eficiência'],
                        hovertemplate="<b>%{x}</b><br>Eficiência: %{y:.2f}%<br>Sincronizações: %{customdata[0]}<br>Revisões: %{customdata[1]}<extra></extra>",
                        customdata=evolucao_sre[['Sincronizações', 'Revisões']].values
                    ))
                    
                    # Adicionar barras para sincronizações (eixo secundário)
                    fig_evol_sre.add_trace(go.Bar(
                        x=evolucao_sre[eixo_x],
                        y=evolucao_sre['Sincronizações'],
                        name='Sincronizações',
                        marker_color='rgba(40, 167, 69, 0.3)',
                        yaxis='y2',
                        opacity=0.6
                    ))
                    
                    fig_evol_sre.update_layout(
                        title=f"{titulo_evol} - Eficiência vs Sincronizações",
                        xaxis_title="Período",
                        yaxis_title="Eficiência (%)",
                        yaxis2=dict(
                            title="Sincronizações",
                            overlaying='y',
                            side='right',
                            showgrid=False
                        ),
                        plot_bgcolor='white',
                        height=400,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        margin=dict(t=50, b=50, l=50, r=50)
                    )
                    
                    st.plotly_chart(fig_evol_sre, use_container_width=True)
                    
                    # Estatísticas da evolução
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    
                    with col_stat1:
                        eficiencia_media = evolucao_sre['Eficiência'].mean()
                        st.metric("Eficiência média", f"{eficiencia_media:.1f}%")
                    
                    with col_stat2:
                        max_eficiencia = evolucao_sre['Eficiência'].max()
                        periodo_max = evolucao_sre.loc[evolucao_sre['Eficiência'].idxmax(), eixo_x]
                        st.metric("Melhor período", f"{periodo_max}: {max_eficiencia:.1f}%")
                    
                    with col_stat3:
                        total_sinc = evolucao_sre['Sincronizações'].sum()
                        st.metric("Total sincronizações", f"{total_sinc}")
                    
                    with col_stat4:
                        total_rev = evolucao_sre['Revisões'].sum()
                        st.metric("Total revisões", f"{total_rev}")
        else:
            st.info("ℹ️ Nenhum dado de sincronização disponível para análise dos SREs.")
    else:
        st.warning("⚠️ Coluna 'SRE' não encontrada nos dados.")
