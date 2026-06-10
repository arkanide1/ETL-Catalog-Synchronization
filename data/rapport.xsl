<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:r="http://ensias.ma/catalogue/rapport"
                exclude-result-prefixes="r">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:strip-space elements="*"/>

<xsl:template match="/">
  <html lang="fr">
    <head>
      <meta charset="UTF-8"/>
      <title>Rapport ETL – Validation catalogue</title>
      <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: 'Segoe UI', Roboto, sans-serif; background:#eef2f7; padding:25px; }
        .wrapper { max-width:1300px; margin:0 auto; background:white; border-radius:24px; box-shadow:0 10px 25px rgba(0,0,0,0.1); overflow:hidden; }
        .entete { background:#1e3c72; color:white; padding:25px 30px; }
        .entete h1 { margin-bottom:8px; }
        .stats { display:flex; flex-wrap:wrap; gap:20px; background:#f8fafc; padding:25px 30px; border-bottom:1px solid #e2e8f0; }
        .stat-card { background:white; border-radius:20px; padding:18px 25px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.05); flex:1; min-width:130px; }
        .stat-nb { font-size:2.2rem; font-weight:800; color:#0f3b5f; }
        .resume-types { display:flex; gap:15px; padding:20px 30px; flex-wrap:wrap; background:white; border-bottom:1px solid #e2e8f0; }
        .type-badge { padding:8px 20px; border-radius:40px; font-weight:600; }
        .manquante { background:#fee2e2; border-left:5px solid #dc2626; }
        .nonresolue { background:#fff1e6; border-left:5px solid #ed8936; }
        .avertissement { background:#fef9e3; border-left:5px solid #eab308; }
        .bloquants { background:#fff4ed; margin:20px 30px; padding:15px 20px; border-radius:20px; border-left:5px solid #dd6b20; }
        .badge-id { display:inline-block; background:#f3e5d8; padding:4px 12px; margin:4px 6px 4px 0; border-radius:30px; font-family:monospace; font-size:0.8rem; }
        .section { font-size:1.4rem; font-weight:700; margin:25px 30px 10px 30px; }
        .table-wrapper { overflow-x:auto; margin:0 30px 30px 30px; border:1px solid #e2e8f0; border-radius:16px; }
        table { width:100%; border-collapse:collapse; font-size:0.85rem; }
        th { background:#f1f5f9; padding:12px; text-align:left; }
        td { padding:10px 12px; border-bottom:1px solid #edf2f7; vertical-align:top; }
        .type-label { display:inline-block; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.7rem; }
        .type-VALEUR_MANQUANTE { background:#fecaca; color:#991b1b; }
        .type-CATEGORIE_NON_RESOLUE { background:#fed7aa; color:#9c4221; }
        .type-AVERTISSEMENT { background:#fef9c3; color:#854d0e; }
        .value-cell { font-family:monospace; background:#fef7e0; max-width:250px; word-break:break-all; }
        footer { text-align:center; padding:20px; font-size:0.75rem; color:#6c757d; border-top:1px solid #e2e8f0; }
      </style>
    </head>
    <body>
    <div class="wrapper">
      <xsl:variable name="r" select="/r:rapport_erreurs"/>
      <div class="entete">
        <h1>Rapport de validation ETL <span style="background:#c2410c; padding:4px 12px; border-radius:40px; font-size:0.8rem;"><xsl:value-of select="$r/@statut"/></span></h1>
        <div><xsl:value-of select="$r/r:entete/r:projet"/> – <xsl:value-of select="$r/r:entete/r:auteur"/></div>
        <div>Généré le <xsl:value-of select="$r/@date_generation"/> | Fichier : <xsl:value-of select="$r/r:entete/r:fichier_analyse"/></div>
      </div>
      
      <div class="stats">
        <div class="stat-card"><div class="stat-nb"><xsl:value-of select="$r/@nb_produits"/></div><div>Produits analysés</div></div>
        <div class="stat-card"><div class="stat-nb"><xsl:value-of select="$r/@nb_erreurs"/></div><div>Total anomalies</div></div>
        <div class="stat-card"><div class="stat-nb"><xsl:value-of select="$r/@nb_bloquants"/></div><div>Produits bloquants</div></div>
        <div class="stat-card"><div class="stat-nb"><xsl:value-of select="format-number($r/@nb_bloquants div $r/@nb_produits * 100, '0')"/>%</div><div>Taux blocage</div></div>
      </div>
      
      <div class="resume-types">
        <xsl:for-each select="$r/r:resume_par_type/r:type_erreur">
          <div class="type-badge {translate(@code, '_', '-')}"><xsl:value-of select="@code"/> : <strong><xsl:value-of select="@count"/></strong></div>
        </xsl:for-each>
      </div>
      
      <div class="bloquants">
        <strong>Produits bloquants (<xsl:value-of select="$r/@nb_bloquants"/>) :</strong><br/>
        <xsl:for-each select="$r/r:produits_bloquants/r:produit_id">
          <span class="badge-id">ID <xsl:value-of select="."/></span>
        </xsl:for-each>
      </div>
      
      <div class="section">Détail des erreurs</div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr><th>#</th><th>Produit</th><th>Champ</th><th>Type</th><th>Message</th><th>Valeur</th></tr>
          </thead>
          <tbody>
            <xsl:for-each select="$r/r:detail_erreurs/r:anomalie">
              <tr>
                <td><xsl:value-of select="@numero"/></td>
                <td><xsl:value-of select="r:produit_id"/></td>
                <td><code><xsl:value-of select="r:champ"/></code></td>
                <td><span class="type-label type-{r:type}"><xsl:value-of select="r:type"/></span></td>
                <td><xsl:value-of select="r:message"/></td>
                <td class="value-cell"><xsl:value-of select="r:valeur"/></td>
              </tr>
            </xsl:for-each>
          </tbody>
        </table>
      </div>
      <footer>Rapport généré par l'ETL – ENSIAS 2025/2026</footer>
    </div>
    </body>
  </html>
</xsl:template>
</xsl:stylesheet>