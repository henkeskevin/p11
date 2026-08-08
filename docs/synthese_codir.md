# Synthèse CODIR — octobre

## Ce que disent les données

- En octobre, **5 751 unités** ont généré **143 680,10 € de chiffre d’affaires TTC**. Le calcul est réconcilié par une seconde méthode, sans écart.
- La **marge brute d’octobre est de 44 660,65 € HT**, avec une TVA supposée à **20 %**. Elle ne doit pas être comparée directement au chiffre d’affaires TTC.
- Le chiffre d’affaires est diffus : les **20 premières références pèsent 11,02 %** du total et **435 références sur 714** sont nécessaires pour atteindre 80 % du chiffre d’affaires.
- Le stock ERP brut signé au 31 octobre représente **17 811 unités** et **298 555,76 € au coût d’achat HT**. En excluant les stocks négatifs à contrôler, il représente **17 822 unités** et **298 627,66 € au coût d’achat HT**.
- Sur le seul catalogue rapproché et hors stock négatif, le stock représente **16 740 unités**, soit **277 328,07 € au coût d’achat HT**. Sa valeur théorique au prix de vente est **494 637,90 € TTC** : ce n’est ni du chiffre d’affaires acquis, ni une marge, ni une valeur de stock comparable au coût HT.

Sources : [indicateurs clés](../reports/tables/indicateurs_cles.json), [20 premières références](../reports/tables/top20_ca_octobre.csv).

## Décisions proposées

| Priorité | Décision | Motif factuel | Propriétaire indicatif |
|---|---|---|---|
| Protéger les ventes | Vérifier les ruptures, puis décider les réassorts au cas par cas. | **22 références** ont vendu en octobre mais sont à zéro en stock au 31 octobre. | Approvisionnement, avec Commerce |
| Réduire le stock lent | Examiner les références, puis choisir maintien, transfert ou action commerciale. Ne pas solder automatiquement. | **24 références**, valorisées **95 011,92 € au coût d’achat HT**, dépassent douze mois de couverture si le rythme d’octobre se répétait. | Achats et Stocks, avec Finance |
| Qualifier le stock sans vente | Confirmer le statut commercial et l’existence d’une demande avant toute décision. | **3 références** sans vente en octobre immobilisent **14 959,40 € au coût d’achat HT**. Un seul mois ne suffit pas à conclure qu’elles sont invendables. | Commerce et Finance |
| Fiabiliser le catalogue | Corriger les liaisons manquantes et les identifiants devenus introuvables, sans inventer de correspondance. | **91 références ERP** n’ont pas d’identifiant Web et **20 identifiants renseignés** n’ont pas de ligne produit Web correspondante. | E-commerce et responsable des données |
| Sécuriser les indicateurs | Traiter d’abord les erreurs certaines et faire confirmer les anomalies par les équipes sources. | Le registre contient **7 erreurs certaines**, **125 anomalies probables** et **33 prix inhabituels mais plausibles**. | Responsables ERP/Web, avec Finance |

Sources : [indicateurs clés](../reports/tables/indicateurs_cles.json), [priorités de stock](../reports/tables/priorites_stock.csv), [audit des rapprochements](../reports/tables/audit_jointures.csv), [registre qualité](../reports/tables/registre_qualite.csv).

## Garde-fou de décision

Les ventes couvrent uniquement octobre et le stock est une photographie au 31 octobre ; l'année et l'horodatage d'extraction restent à confirmer. Les couvertures de stock prolongent le rythme d’octobre : elles servent à ordonner une revue, pas à prévoir la demande annuelle. La prochaine étape de pilotage est de reproduire ce suivi chaque mois avant de fixer des politiques durables d’achat ou de déstockage.
