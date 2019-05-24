Feature: Propositions d’UE

  Background:
    Given La base de données est dans son état initial.

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
    Then Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien LCHIM1141,LCHIM1391.

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
#  Encoder la valeur « LDROI1234 » dans la zone « Code »
#  Encoder la valeur « Cours » dans la zone « Type »
#  Encoder la valeur « 5 » dans la zone « Crédits »
#  Encoder la valeur « Cours de droit » dans la zone « Intitulé commun »
#  Encoder la valeur « Louvain-la-Neuve » dans la zone « Lieu d’enseignement »
#  Encoder la valeur « DRT » dans la zone « Entité resp. cahier des charges »
#  Encoder la valeur « DRT » dans la zone « Entité d’attribution »
#  Encoder la valeur « 2019-20 » dans la zone « Année académique »
#  Encoder la valeur « DRT1234 » dans la zone « Dossier »
#  Vérifier que la zone « Etat » est bien grisée et que la valeur est bien « Faculté »
#  Cliquer sur le bouton « Enregistrer »
#  Vérifier les valeurs ci-dessous.

  Scenario: 24 : En tant que gestionnaire facultaire, je dois pouvoir faire une proposition de modification.

  Scenario: 25 : En tant que gestionnaire facultaire, je dois pouvoir faire une proposition de fin d’enseignement.

  Scenario: 26 : En tant que gestionnaire facultaire, je dois pouvoir modifier une proposition.

  Scenario: 27 : En tant que gestionnaire facultaire, je dois pouvoir annuler une proposition.

  Scenario: 28 : En tant que gestionnaire central, je dois pouvoir consolider une proposition.
