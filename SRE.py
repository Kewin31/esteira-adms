with col_ranking:
    # Ranking dos SREs
    st.markdown("### 🏆 Ranking SREs")
    
    # Calcular ranking baseado em sincronizados
    sre_ranking = sinc_por_sre.copy()
    sre_ranking = sre_ranking.sort_values('Sincronizados', ascending=False).reset_index(drop=True)
    
    # Container para ranking - CONSTRUINDO HTML COMPLETO
    ranking_html = '''
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #dee2e6; margin-bottom: 1rem;">
        <div style="text-align: center; font-weight: bold; color: #1e3799; margin-bottom: 0.5rem;">🏆 CLASSIFICAÇÃO</div>
    '''
    
    # Medalhas e cores
    medalhas = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
    cores_bg = ['#e8f4f8', '#f0f0f0', '#f8f0e8', '#f8f9fa', '#ffffff']
    cores_borda = ['#1e3799', '#495057', '#856404', '#6c757d', '#adb5bd']
    
    # Mostrar até 5 SREs
    num_sres = min(len(sre_ranking), 5)
    
    for i in range(num_sres):
        sre = sre_ranking.iloc[i]
        medalha = medalhas[i] if i < len(medalhas) else f"{i+1}️⃣"
       
