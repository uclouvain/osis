Feature: Propositions d’UE

  Background:
    Given La base de données est dans son état initial.
    And LCHIM1141 est en proposition en 2019-20 lié à CHIM

  Scenario: 20 : En tant que gestionnaire facultaire, je dois pouvoir rechercher des propositions par sigle ou numéro de dossier.
    Given L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité MED
    And Aller sur la page de recherche d'UE
    And Sélectionner l’onglet « Propositions »
    And Réinitialiser les critères de recherche

    When Encoder 2019-20 comme Anac.
    And Encoder LCHIM1141 comme Code
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien LCHIM1141.

    Given Réinitialiser les critères de recherche
    When Encoder 2019-20 comme Anac.
    And  Encoder CHIM comme Sigle dossier
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien LCHIM1141.

  Scenario: 21 : En tant que gestionnaire facultaire, je dois pouvoir rechercher des propositions par entité de charge.
    Given L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité DRT
    And Aller sur la page de recherche d'UE
    And Sélectionner l’onglet « Propositions »
    And Réinitialiser les critères de recherche

    When Encoder 2019-20 comme Anac.
    And Encoder DRT comme Ent. charge
    And Cliquer sur le bouton Rechercher (Loupe)

    Then Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien LDRH03401,LDRH03404,LDRH03406,LDROI1003.

  Scenario: 22 : En tant que gestionnaire facultaire, je dois pouvoir rechercher des propositions et produire un Excel.
  Description : Recherche des propositions + produire l’Excel

  Scenario: 23 : En tant que gestionnaire facultaire, je dois pouvoir faire une proposition de création.
    Given L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité DRT
    And Aller sur la page de recherche d'UE

    When  Cliquer sur le menu « Actions »
    And Cliquer sur le menu Proposition de création
    And  Encoder LDROI1234 comme Code
    And  Encoder Cours comme Type
    And  Encoder 5 comme Crédits
    And  Encoder Cours de droit comme Intitulé commun
    And  Encoder Louvain-la-Neuve comme Lieu d’enseignement
    And  Encoder DRT comme Entité resp. cahier des charges
    And  Encoder DRT comme Entité d’attribution
    And  Encoder 2019-20 comme Année académique
    And  Encoder DRT1234 comme Dossier

    Then  Vérifier que la zone Etat est bien grisée
    And la valeur de Etat est bien Faculté
    And Cliquer sur le bouton « Enregistrer »

    Then  Vérifier que la unité d'enseignement LDROI1234 a bien été mise en proposition pour l'année 2019-20

    Given Aller sur la page de recherche d'UE
    And Sélectionner l’onglet « Propositions »
    And Réinitialiser les critères de recherche

    When Encoder 2019-20 comme Anac.
    And Encoder LDROI1234 comme Code
    And Encoder DRT comme Ent. charge
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien LDROI1234.

    Given Aller sur la page de recherche d'UE
    And Réinitialiser les critères de recherche

    When Encoder 2019-20 comme Anac.
    And Encoder LDROI1234 comme Code
    And Encoder DRT comme Ent. charge
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien LDROI1234.

  Scenario: 24 : En tant que gestionnaire facultaire, je dois pouvoir faire une proposition de modification.
    Given L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité DRT
    And Aller sur la page de detail de l'ue: LDROI1006 en 2019-20

    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Mettre en proposition de modification »
    And Encoder 4 comme Crédits
    And Encoder Bisannuelle paire comme Périodicité
    And Encoder DRT4321 comme Dossier
    Then Vérifier que la zone Etat est bien grisée
    And Vérifier que la zone Type est bien grisée
    And Cliquer sur le bouton « Enregistrer »
    Then  Vérifier les valeurs ci-dessous.


  Scenario: 25 : En tant que gestionnaire facultaire, je dois pouvoir faire une proposition de fin d’enseignement.
    Given L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité DRT
    And Aller sur la page de detail de l'ue: LDROI1007 en 2019-20

    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Mettre en proposition de fin d’enseignement »

    When Encoder 2019-20 comme Anac de fin
    When Encoder DRT5678 comme Dossier

    Then Vérifier que la zone Etat est bien grisée
    And Vérifier que la zone Type est bien grisée

    When Cliquer sur le bouton « Oui, je confirme »
    And Vérifier les valeurs ci-dessous.

  Scenario: 26 : En tant que gestionnaire facultaire, je dois pouvoir modifier une proposition.

  Scenario: 27 : En tant que gestionnaire facultaire, je dois pouvoir annuler une proposition.

  Scenario: 28 : En tant que gestionnaire central, je dois pouvoir consolider une proposition.
