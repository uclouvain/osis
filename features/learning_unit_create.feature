Feature: Création de d'unité d'enseignement.

  Background:
    Given La base de données est dans son état initial.

  Scenario: En tant que gestionnaire facultaire, je dois pouvoir créer un nouveau partim.
    Given La période de modification des programmes est en cours
    And L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité MED
    Given Aller sur la page de detail de l'ue: WPEDI2190 en 2019-20
    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Nouveau partim »
    And Encoder 3 comme Code dédié au partim
    And Cliquer sur le bouton « Enregistrer »

    Then Vérifier que le partim WPEDI21903 a bien été créé de 2019-20 à 2024-25.
    When Cliquer sur le lien WPEDI2190
    Then Vérifier que le cours parent WPEDI2190 contient bien 3 partims.

  Scenario: Un tant que gestionnaire facultaire, je dois pouvoir créer un autre collectif
    Given La période de modification des programmes est en cours
    And L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité MED

    Given Aller sur la page de recherche d'UE
    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Nouvelle UE »

    And Encoder WMEDI1234 comme Code
    And Encoder Autre collectif comme Type
    And Encoder 5 comme Crédit
    And Encoder Louvain-la-Neuve comme Lieu d’enseignement
    And Encoder MED comme Entité resp. cahier des charges
    And Encoder MED comme Entité d’attribution
    And Encoder Test comme Intitulé commun
    And Cliquer sur le bouton « Enregistrer »

    Then Vérifier que le partim WMEDI1234 a bien été créé de 2019-20 à 2024-25.

