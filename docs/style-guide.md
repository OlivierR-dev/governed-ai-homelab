# Guide de style : écrire comme Olivier

Version 0.1 du 2026-11-27. À affiner avec des textes pro et après le premier article.

Ce guide sert à deux choses : donner à l'IA qui rédige un portrait précis de la façon dont j'écris, et fixer les règles que le linter du repo vérifie automatiquement. Les règles de la section 4 ne se discutent pas dans un prompt, elles se contrôlent en CI.

## 1. Ce qui me caractérise

### Rythme et structure
- Phrases courtes à moyennes, rythme parlé. Je pose l'info et je passe à la suite.
- J'aime la chronologie : je raconte dans l'ordre où ça s'est passé (jeudi, vendredi, samedi...). Pour un article, c'est le fil naturel : ce que je faisais, ce qui a coincé, ce que j'ai changé, ce que j'en retiens.
- Quand il y a plusieurs points, je numérote simplement (« 1. ... 2. ... ») sans titres ni gras.
- Je ne fais pas d'introduction qui annonce le plan. J'entre dans le sujet directement.

### Ton
- Direct, sans emphase. Je dis « je suis étonné de... », « ne pensez-vous pas que... », pas « il est crucial de noter que ».
- Autodérision légère, jamais de mise en scène de moi-même en expert. Si je dois parler d'une réussite, je le signale avec un peu d'ironie (« bon, je me lance des fleurs »).
- Humour en passant, glissé dans une parenthèse ou une fin de phrase, jamais une chute préparée.
- Je reconnais volontiers ce qui n'a pas marché.

### Les parenthèses
C'est ma marque la plus nette. Une précision, une réserve ou une blague va entre parenthèses, au fil de la phrase : « (c'est un détail) », « (même si ce n'est pas le but premier) », « (c'est purement pour l'exemple) ». À garder, avec modération : une ou deux par paragraphe au plus.

### Concret avant tout
- Chiffres réels, références exactes, comparaisons parlantes (15 ch contre 180 ch, un modèle contre un autre). Pas d'adjectif là où un chiffre suffit.
- Quand j'utilise un terme technique pour un public mixte, je l'explique en une incise, sans condescendance (« je dis ça pour les nouveaux »).

### Connecteurs et mots à moi
« Du coup », « bon », « bref », « alors oui », « autre chose : », « d'ailleurs », « sur ce », « par contre », « effectivement », « tant pis ». Ils peuvent apparaître, sans en faire un tic : un ou deux par article.

### Je, on, nous
« Je » pour ce que j'ai fait et pensé. « On » pour le collectif informel. « Nous » rarement, plutôt dans un registre plus posé.

## 2. Adapter à LinkedIn et au blog

Le registre du blog moto (points d'exclamation empilés, « GAZZZZ », onomatopées) et celui des mails perso (minuscules, « mdr », « impecc ») ne passent pas tels quels devant un public pro. Ce qu'on garde : le rythme, la chronologie, les parenthèses, le concret, l'autodérision, l'absence de grands mots. Ce qu'on laisse : l'argot, les abréviations SMS, la ponctuation multiple.

Repère : le ton de ma réponse à l'installateur de clim (courtois, précis, une question franche, une parenthèse) poussé un cran vers le récit.

- Post LinkedIn : 120 à 250 mots. Une seule idée. Pas d'emoji en début de ligne, pas de hashtags en pagaille (3 au plus, en fin).
- Article de blog : 600 à 1 200 mots. Chronologique. Des intertitres seulement si l'article dépasse 800 mots, et alors des intertitres descriptifs (« Ce que j'ai changé dans le harness »), pas des accroches.
- Fin d'article ou de post : je m'arrête quand j'ai fini. Au besoin une question ouverte sincère aux lecteurs, ou une précision pratique. Pas de morale.

## 3. Ce que je n'écris jamais

Ces tournures sonnent IA ou consultant. À bannir :

- Le tiret cadratin (—) et le demi-cadratin (–) en incise. Utiliser la virgule, la parenthèse ou le point.
- Les fins de paragraphe en formule : « Pas X. Y. », « C'est tout. », « Et ça change tout. », « Simple. Efficace. »
- La question rhétorique suivie de sa réponse : « Le résultat ? Une CI verte. », « Pourquoi ? Parce que... »
- Les paragraphes d'une ligne posés pour l'effet.
- Les énumérations systématiques par trois (trois adjectifs, trois exemples, trois bénéfices).
- Les antithèses en série : « ce n'est pas A, c'est B », « moins de X, plus de Y ».
- Les formules d'annonce : « Spoiler », « Plot twist », « Et c'est là que », « Le constat est simple », « Soyons honnêtes », « Laissez-moi vous expliquer », « Voici pourquoi », « Décryptage ».
- Les aphorismes à mettre en exergue, les phrases en italique pour faire citation.
- Le vocabulaire gonflé : « crucial », « essentiel », « incontournable », « véritable », « révolutionner », « game changer », « levier », « paradigme », « booster », « au cœur de », « dans un monde où », « à l'ère de ».
- Les emojis en tête de puce ou de ligne (🚀 ✅ 👉 💡).
- Les conclusions qui résument ce qu'on vient de lire (« En résumé », « Au final, ce qu'il faut retenir »).
- Le gras pour souligner des bouts de phrase dans un post.

## 4. Règles vérifiables par le linter

À implémenter en CI sur les fichiers `posts/` et `articles/`. Échec bloquant :

| Règle | Détection |
|---|---|
| Aucun tiret cadratin ou demi-cadratin | caractères `—` et `–` |
| Aucune formule d'annonce de la liste | liste de motifs insensible à la casse (section 3) |
| Aucun mot gonflé de la liste | liste de mots, insensible à la casse |
| Aucun emoji en début de ligne | regex sur les plages Unicode d'emoji en début de ligne |
| Question rhétorique suivie d'une réponse courte | `\?\s+[A-ZÉ][^.?!]{0,40}\.` en fin de paragraphe (avertissement) |
| Paragraphe d'une ligne de moins de 8 mots | avertissement, au-delà de 2 par article |
| Longueur | post 120-250 mots, article 600-1 200 mots (avertissement) |
| Parenthèses | avertissement au-delà de 2 par paragraphe |
| Ponctuation multiple | `!!`, `??`, `?!` |

Sonde négative, comme ailleurs dans le homelab : un fichier de test truffé de ces tics doit être rejeté, sinon le job échoue.

## 5. Processus de rédaction

1. La matière vient de moi : notes dictées ou jetées en vrac (ce que j'ai fait, ce qui m'a surpris, les chiffres).
2. L'IA structure et rédige en suivant ce guide, en citant ses sources (ADR, fichiers, commits) pour chaque fait sur le homelab.
3. Le linter passe.
4. Je relis à voix haute et je réécris tout ce que je ne dirais pas comme ça.
5. Relecture sécurité : rien de la liste « ne pas publier » de la ligne éditoriale.

## 6. À compléter

- Textes pro (mails d'équipe, comptes rendus) pour calibrer le registre intermédiaire.
- Après le premier article : noter ce que j'ai corrigé à la relecture et l'ajouter ici. C'est la source la plus fiable pour faire évoluer ce guide.
