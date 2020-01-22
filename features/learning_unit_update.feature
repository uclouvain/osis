Feature: Mise à jour en gestion journalière

  Background:
    Given La base de données est dans son état initial.
    And les flags d'éditions des UEs sont désactivés.
    And La période de modification des unités d'enseignement est en cours

    # TODO Modify cms data + attribution

  Scenario: En tant que gestionnaire facultaire, je ne peux pas modifier les UE d'une autre fac.
    Given L'utilisateur est loggé en tant que gestionnaire facultaire
    And Aller sur la page de detail d'une UE ne faisant pas partie de la faculté
    When Cliquer sur le menu « Actions »
    Then L’action « Modifier » est désactivée.

  Scenario: En tant que gestionnaire facultaire, je dois pouvoir mettre à jour une UE de ma fac.
    Given L'utilisateur est loggé en tant que gestionnaire facultaire
    And Aller sur la page de detail d'une UE faisant partie de la faculté
    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Modifier »
    And Décocher la case « Actif »
    And Encoder 1 comme Session dérogation
    And Encoder Q1 et Q2 comme Quadrimestre
    And Cliquer sur le bouton « Enregistrer »
    And A la question, « voulez-vous reporter » répondez « non »
    Then Vérifier que le cours est bien Inactif
    And Vérifier que le Quadrimestre est bien Q1 et Q2
    And Vérifier que la Session dérogation est bien 1

  Scenario: En tant que gestionnaire central, je dois pouvoir mettre à jour une UE.
  Description : en particulier les crédits et la périodicité + vérifier que les UE peuvent
  être mises à jour par la gestionnaire central en dehors de la période de modification des programmes.
    Given L'utilisateur est loggé en tant que gestionnaire central
    And Aller sur la page de detail d'une UE faisant partie de la faculté

    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Modifier »
    And Décocher la case « Actif »
    And Encoder 12 comme Crédits
    And Encoder bisannuelle paire comme Périodicité
    And Cliquer sur le bouton « Enregistrer »
    And A la question, « voulez-vous reporter » répondez « oui »

    Then Vérifier que le champ Crédits est bien 12
    And Vérifier que la Périodicité est bien bisannuelle paire
    And Rechercher la même UE dans une année supérieure
    And Vérifier que le champ Crédits est bien 12
    And Vérifier que la Périodicité est bien bisannuelle paire

  Scenario: En tant que gestionnaire facultaire, je dois pouvoir créer un nouveau partim.
    Given L'utilisateur est loggé en tant que gestionnaire facultaire
    And Aller sur la page de detail d'une UE faisant partie de la faculté
    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Nouveau partim »
    And Encoder 3 comme Code dédié au partim
    And Cliquer sur le bouton « Enregistrer »

    Then Vérifier que le partim a bien été créé de 2019-20 à 2024-25.
    When Cliquer sur le lien WPEDI2190

  Scenario: En tant que gestionnaire facultaire, je dois pouvoir créer un autre collectif
    Given L'utilisateur est loggé en tant que gestionnaire facultaire

    Given Aller sur la page de recherche d'UE
    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Nouvelle UE »

    And Encoder WMEDI1234 comme Code
    And Encoder Autre collectif comme Type
    And Encoder 5 comme Crédit
    And Encoder Test comme Intitulé commun
    And Encoder Lieu d’enseignement
    And Encoder Entité resp. cahier des charges
    And Encoder Entité d’attribution
    And Cliquer sur le bouton « Enregistrer »

    Then Vérifier que le partim WMEDI1234 a bien été créé de 2019-20 à 2024-25.
