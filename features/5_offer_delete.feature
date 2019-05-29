Feature: Suppression d'offre.

  Background:
    Given La base de données est dans son état initial.
    And L'utilisateur est loggé en tant que gestionnaire central.
    And L’utilisateur est attaché à l’entité UCL
    And La formation DROI2MS/TT doit exister

  Scenario: 31 : En tant que gestionnaire central, je dois pouvoir supprimer une offre.
    Given Aller sur la page Catalogue de formations / Formation
    And Réinitialiser les critères de recherche
    And Encoder DROI2MS/TT comme Sigle/Intitulé abrégé
    And Cliquer sur le bouton Rechercher (Loupe)

    And Cliquer sur le sigle DROI2MS/TT dans la liste de résultats
    When Cliquer sur le menu « Actions »
    And Cliquer sur « Supprimer »
    And Cliquer sur « Oui, je confirme »

    Given Aller sur la page Catalogue de formations / Formation
    And Réinitialiser les critères de recherche
    And Encoder DROI2MS/TT comme Sigle/Intitulé abrégé
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Vérifier que la liste est vide.

    And Réinitialiser les critères de recherche
    And Encoder LDROI101T comme Code
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Vérifier que la liste est vide.

    And Réinitialiser les critères de recherche
    And Encoder LDROI300GT comme Code
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Vérifier que la liste est vide.
