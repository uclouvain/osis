Feature: Recherche des unités d'enseignements.

  Background:
    Given La base de données est dans son état initial.
    And L'utilisateur est loggé en tant que gestionnaire
    And Aller sur la page de recherche d'UE
    And Réinitialiser les critères de recherche

  Scenario: En tant que gestionnaire, je recherche une UE par code
  When Encoder le code d'une UE
  And Cliquer sur le bouton Rechercher (Loupe)
  Then Dans la liste de résultat, l'UE doit apparaître

# TODO Generate UE of different container types
#  Scenario: En tant que gestionnaire facultaire ou central, je recherche des UEs par type
#    When Encoder le type d'UE
#    And Cliquer sur le bouton Rechercher (Loupe)
#    Then Dans la liste de résultat, seul ce type doit apparaître


  Scenario: En tant que gestionnaire facultaire ou central, je recherche des UEs par entité
    When Encoder l'entité d'UE
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Dans la liste de résultat, seul cette entité doit apparaître

  Scenario: En tant que gestionnaire facultaire ou central, je recherche des UEs par enseignant
    When Encoder l'enseignant d'UE
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Dans la liste de résultat, seul les UEs de l'enseignant doivent apparaître

  Scenario: En tant que gestionnaire facultaire ou central, je recherche des UE pour produire un Excel
    When Encoder le code d'une UE
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Dans la liste de résultat, l'UE doit apparaître
    When Ouvrir le menu « Exporter »
    And Sélection « Liste personnalisée des unités d’enseignement »
    And Cocher les cases « Programmes/regroupements » et « Enseignant(e)s »
    And Cliquer sur « Produire Excel »
    Then Le fichier excel devrait être présent