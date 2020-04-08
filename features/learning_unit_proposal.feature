Feature: Propositions d’UE

  Background:
    Given La base de données est dans son état initial.
    And les flags d'éditions des UEs sont désactivés.
    And La période de modification des unités d'enseignement est en cours

  Scenario: En tant que gestionnaire central, je dois pouvoir consolider une proposition de création
    Given L'utilisateur est loggé en tant que gestionnaire central
    And Aller sur la page de recherche des propositions
    And Réinitialiser les critères de recherche
    And Rechercher propositions de création
    Then Sélectionner une proposition

    When Cliquer sur le menu « Actions »
    And Cliquer sur « Modifier la proposition »
    And Proposition encoder l'état Accepté
    And Proposition Cliquer sur le bouton « Enregistrer »
    Then Vérifier que la proposition est en état Accepté

    When Cliquer sur le menu « Actions »
    And Cliquer sur « Consolider »
    And Cliquer sur « Oui » pour consolider
    Then Vérifier que la proposition a été consolidée avec succès


#  Scenario Outline: En tant que gestionnaire central, je dois pouvoir consolider une proposition.
#    Given L'utilisateur est loggé en tant que gestionnaire central
#    Given L'ue LDROI1234 est en proposition de création
#    Given L'ue LDROI1006 est en proposition de modification
#    Given L'ue LSINF1121 est en proposition de suppression
#
#    And Aller sur la page de detail de l'ue: <acronym>
#    When Cliquer sur le menu « Actions »
#    And Cliquer sur « Modifier la proposition »
#    And Proposition Encoder Accepté comme Etat
#    And Proposition Cliquer sur le bouton « Enregistrer »
#
#    And Aller sur la page de recherche d'UE
#    And Sélectionner l’onglet « Propositions »
#    And Réinitialiser les critères de recherche
#
#    When Encoder année suivante
#    And Recherche proposition Encoder <acronym> comme Code
#    And Cliquer sur le bouton Rechercher (Loupe)
#
#    Then Vérifier que le dossier <acronym> est bien Accepté
#    When Sélectionner le premier résultat
#    And Cliquer sur « Consolider »
#    And Cliquer sur « Oui » pour consolider
#    Then Vérifier que la proposition <acronym> a été consolidée avec succès.
#
#    And Aller sur la page de recherche d'UE
#    And Réinitialiser les critères de recherche
#
#    When Encoder année suivante
#    And Recherche proposition Encoder <acronym> comme Code
#    And Cliquer sur le bouton Rechercher (Loupe)
#    Then Vérifier que <acronym> n'est pas en proposition.
#
#    Examples:
#      | acronym   |
#      | LDROI1234 |
#      | LDROI1006 |
#      | LSINF1121 |
