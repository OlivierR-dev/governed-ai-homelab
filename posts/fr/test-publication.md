# Test de publication

Jeudi matin, j'ai monté la chaîne qui publiera ces textes (c'est un test, il sera fermé aussitôt). Le brouillon part d'un dépôt privé, passe un contrôle de style et une liste de motifs interdits, puis arrive ici par une pull request.

Rien ne part directement sur la branche principale. Le dépôt public refuse un push direct, et la CI doit passer avant toute fusion : le linter de style, ses tests, une sonde qui doit être rejetée, et un scan de secrets sur tout l'historique.

Du coup, ce texte sert surtout à vérifier que la pull request s'ouvre avec l'article seul, que les contrôles tournent dessus, et que je peux la fermer sans rien fusionner.

Si vous lisez ceci sur le dépôt, c'est que j'ai oublié de la fermer (bon, ça arrive).
