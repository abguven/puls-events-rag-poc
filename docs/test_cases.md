### 🧪 Le Protocole de Test "Puls-Events"

#### Catégorie 1 : Les pièges Géographiques (Le "Scope")

*Le modèle doit comprendre qu'il ne connaît QUE Paris et sa banlieue proche.*

1.  **Le Test "Hors-Piste" :** *"Quels sont les concerts prévus à Lyon ce week-end ?"*
    *   *Réponse attendue :* "Désolé, je ne gère que les événements à Paris. Mais voici ce qui se passe à Paris..." (Il ne doit PAS sortir un concert rue de Lyon à Paris en prétendant que c'est à Lyon).
2.  **Le Test "Précision Quartier" :** *"Je cherche une expo sympa à Montmartre."*
    *   *Réponse attendue :* Il doit trouver des événements avec le zipcode `75018` ou le mot "Montmartre" dans le lieu.

#### Catégorie 2 : Les pièges Temporels (Le plus dur)

*Le modèle a besoin de connaître la date d'aujourd'hui pour répondre.*

3.  **Le Test "Relatif Court" :** *"Qu'est-ce qu'on peut faire ce week-end ?"*
    *   *Défi :* Transformer "ce week-end" en dates précises (ex: samedi 18 et dimanche 19).
4.  **Le Test "Relatif Long" :** *"Y a-t-il des festivals le mois prochain ?"*
    *   *Défi :* Comprendre le changement de mois.
5.  **Le Test "Date Explicite" :** *"Des idées de sortie pour le 14 juillet ?"*
    *   *Défi :* Filtrer exactement sur cette date.

#### Catégorie 3 : Les pièges de Contraintes (Filtres)

6.  **Le Test "Radin" :** *"Je veux sortir ce soir mais j'ai 0 budget."*
    *   *Réponse attendue :* Uniquement des événements `price_type: gratuit` ou `combined_price` contenant "gratuit".
7.  **Le Test "Enfants" :** *"Un atelier pour occuper mes gosses mercredi après-midi."*
    *   *Réponse attendue :* Recherche sémantique sur "Enfant", "Jeune public", "Famille".

#### Catégorie 4 : Les Hallucinations & Refus

8.  **Le Test "Inexistant" :** *"Où se déroule le concert des Rolling Stones à la Tour Eiffel demain ?"*
    *   *Réponse attendue :* "Je ne trouve aucune information sur cet événement." (Il ne doit pas inventer).
9.  **Le Test "Hors-Sujet" :** *"Donne-moi la recette de la quiche lorraine."*
    *   *Réponse attendue :* Refus poli. "Je suis un assistant événementiel..."

#### Catégorie 5 : La question "Combo" (Le Boss Final)

10. **Le Test Ultime :** *"Je cherche un concert de Jazz gratuit dans le marais pour la semaine prochaine."*
    *   *Défi :* Sémantique (Jazz) + Filtre Prix (Gratuit) + Filtre Lieu (75003/75004) + Filtre Date (Semaine pro).