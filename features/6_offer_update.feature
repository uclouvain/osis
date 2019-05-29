Feature: Modification d'offre

  Background:
    Given La base de données est dans son état initial.
    And La formation DROI2MS/TT doit exister

  Scenario: 32 : En tant que gestionnaire central, je dois pouvoir mettre une fin d’enseignement
  Rechercher OPES2M
  Essayer de mettre une date de fin
  -> Message d’avertissement
  Retrouver la finalité dans l’arbre OPES2MS/ES
  Mettre une date de fin sur OPES2M/ES
  Mettre une date de fin sur OPES2M
  Scénario 35 Remettre une date de fin indéterminée pour OPES2M (puis sur OPES2M/ES)
    And L'utilisateur est loggé en tant que gestionnaire central.
    And L’utilisateur est attaché à l’entité UCL
    Given Aller sur la page de detail de la formation: DROI2MS/TT en 2019-2020
    When Cliquer sur « Actions / Modifier »
    And Encoder 2021 comme  Fin
    And Cliquer sur le bouton « Enregistrer »
    Then Vérifier que la formation DROI2MS/TT à bien été mise à jour de 2019 à 2021
    Then Vérifier que la formation DROI2MS/TT à bien été supprimée de 2022 à 2024

    Given Aller sur la page Catalogue de formations / Formation
    And Vérifier qu'il n'y a que 4 résultats.

  Scenario: 33 : En tant que gestionnaire facultaire, je dois pouvoir ajouter une finalité dans une offre.

  Description : Ajouter DROI2MS/TT dans DROI2M
  -> BUG : on doit pouvoir attacher DROI2MS/TT dans les finalités de DROI2M
  -> OSIS-2990

  Scenario: 34 : En tant que gestionnaire facultaire, je dois pouvoir ajouter une UE de type mémoire dans les mémoires du tronc commun d’une offre.
    Given L’utilisateur est dans le groupe faculty manager
    And L’utilisateur est attaché à l’entité DRT

    Given Aller sur la page de detail de la formation: DROI2M en 2018-2019
    When Ouvrir « LDROI2M » dans l’arbre
    And Ouvrir « LDROI220T » dans l’arbre
    And Ouvrir « LDRMM900R » dans l’arbre
    And Cliquer sur la recherche rapide
    And Encoder la valeur « LCOMU2900 »
    And Cliquer sur « Rechercher »
    And Cliquer sur « Sélectionner »
    And Cliquer sur « Attacher »
    And Cliquer sur « Enregistrer »

    Then Vérifier que LCOMU2900 a été mis à jour
    And LCOMU2900 se trouve bien dans l'arbre sous LDRMM900R


  Scenario: 35 : En tant que gestionnaire facultaire, je dois pouvoir attacher un groupe au tronc commun d’une offre.
    Given L’utilisateur est dans le groupe faculty manager
    And L’utilisateur est attaché à l’entité DRT

    Given Aller sur la page de detail de la formation: CCCADRÉCOMPL.OPTION7E en 2018-2019
    And Cliquer sur « Actions / Sélectionner »

    Given Aller sur la page de detail de la formation: DROI2M en 2018-2019
    When Sélectionner « LDROI220T » dans l'arbre
    And Cliquer sur « Attacher »
    And Encoder Référence comme Type de lien
    And Cliquer sur le bouton « Enregistrer »

    Then Vérifier que LBIRE14R a été mis à jour
    And LBIRE14R se trouve bien dans l'arbre sous LDROI220T

  Scenario: 36 : En tant que gestionnaire facultaire, je dois pouvoir déplacer une UE d’un groupe vers un autre groupe.
    Given L’utilisateur est dans le groupe faculty manager
    And L’utilisateur est attaché à l’entité DRT

  Scenario: 37 : En tant que gestionnaire facultaire, je ne dois pas pouvoir supprimer une option de la liste des options si cette option est toujours présente dans la liste des finalités.

  Scenario: 38 : En tant que gestionnaire facultaire, je dois pouvoir déplacer une option d’un groupe vers un autre groupe.
