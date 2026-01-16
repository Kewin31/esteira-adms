def criar_card_indicador(valor, label, delta_info=None, icone="📊"):
    """Cria card de indicador visualmente atraente"""
    delta_html = ""
    if delta_info is not None:
        valor_delta, tipo_delta = delta_info
        if tipo_delta == "positive" and valor_delta is not None:
            delta_html = f'<div class="metric-delta-positive">📈 +{valor_delta}%</div>'
        elif tipo_delta == "negative" and valor_delta is not None:
            delta_html = f'<div class="metric-delta-negative">📉 {valor_delta}%</div>'
        # Não mostra nada se for "neutral" ou valor_delta for None
    
    # VERIFICAÇÃO DE TIPO ADICIONADA
    if isinstance(valor, (int, float)):
        valor_formatado = f"{valor:,}"
    else:
        valor_formatado = str(valor)
    
    return f'''
    <div class="metric-card-exec">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <span style="font-size: 1.5rem;">{icone}</span>
            <div style="flex-grow: 1;">
                <div class="metric-value">{valor_formatado}</div>
                <div class="metric-label">{label}</div>
                {delta_html}
            </div>
        </div>
    </div>
    '''
