Feature: Modification d'offre

  Background:
    Given La base de données est dans son état initial.
    And les flags d'éditions des offres sont désactivés.


  Scenario: En tant que gestionnaire central, je dois pouvoir mettre une fin d’enseignement
    Given L'utilisateur est loggé en tant que gestionnaire central
    Given Aller sur la page de detail d'une formation en année académique courante
    When Cliquer sur le menu « Actions »
    When Cliquer sur « Modifier »
    And Encoder année de fin
    And Cliquer sur le bouton « Enregistrer »
    And Si une modal d'avertissement s'affiche, cliquer sur « oui »

    Then Vérifier que la dernière année d'organisation de la formation a été mis à jour

  Scenario: En tant que gestionnaire facultaire, je dois pouvoir ajouter une UE de type mémoire dans les mémoires du tronc commun d’une offre.
    Given L’utilisateur est dans le groupe faculty manager
    And L’utilisateur est attaché à l’entité DRT

    Given Aller sur la page de detail de la formation: DROI2M en 2018-2019
    When Ouvrir l'arbre
    And Ouvrir LDROI200M dans l’arbre
    And Ouvrir LDROI220T dans l’arbre
    And Ouvrir LDRMM900R dans l’arbre

    And Cliquer sur la recherche rapide
    And Selectionner l'onglet d'unité d'enseignement
    And Encoder LCOMU2900 comme Code
    And Cliquer sur le bouton Rechercher (Loupe)
    And Cliquer sur « Sélectionner »
    And Fermer la modal

    And Dans l'arbre, cliquer sur Attacher sur LDRMM900R.
    And Cliquer sur Copier dans la modal
    And Cliquer sur « Enregistrer » dans la modal

    Then Vérifier que LCOMU2900 a été mis à jour
    And LCOMU2900 se trouve bien dans l'arbre sous LDRMM900R


  Scenario: En tant que gestionnaire facultaire, je dois pouvoir attacher un groupe au tronc commun d’une offre.036

  Pour pouvoir réaliser ce scénario, l'utilisateur doit être lié à AGRO pour selectionner le groupe.

    Given L’utilisateur est dans le groupe faculty manager
    And L’utilisateur est attaché à l’entité DRT
    And L’utilisateur est attaché à l’entité AGRO

    Given Aller sur la page de detail de la formation: CCCADRÉCOMPL.OPTION7E en 2018-2019
    When Cliquer sur le menu « Actions »
    And Cliquer sur « Sélectionner »

    Given Aller sur la page de detail de la formation: DROI2M en 2018-2019

    When Ouvrir l'arbre
    And Ouvrir LDROI200M dans l’arbre
    And Ouvrir LDROI220T dans l’arbre
    And Dans l'arbre, cliquer sur Attacher sur LDROI220T.
    And Cliquer sur Copier dans la modal
    And Encoder Référence comme Type de lien
    And Cliquer sur « Enregistrer » dans la modal

    Then Vérifier que LBIRE914R a été mis à jour
    And LBIRE914R se trouve bien dans l'arbre sous LDROI220T

  Scenario: En tant que gestionnaire facultaire, je dois pouvoir déplacer une UE d’un groupe vers un autre groupe.
    Given L’utilisateur est dans le groupe faculty manager
    And L’utilisateur est attaché à l’entité DRT
    Given Aller sur la page de detail de la formation: DROI2M en 2018-2019
    When Ouvrir l'arbre
    And Ouvrir LDROI200M dans l’arbre
    And Ouvrir LDROI220T dans l’arbre
    And Ouvrir LDRCC900R dans l’arbre
    And Dans l'arbre, cliquer sur Sélectionner sur LDROI2108.

    And Ouvrir LDRMM900R dans l’arbre
    And Dans l'arbre, cliquer sur Attacher sur LDRMM900R.
    And Cliquer sur Copier dans la modal
    And Cliquer sur « Enregistrer » dans la modal

    And Dans l'arbre et dans LDRCC900R, cliquer sur Retirer sur LDROI2108.
    And Cliquer sur « Enregistrer » dans la modal
    And Ouvrir LDRMM900R dans l’arbre
    And LDROI2108 se trouve bien dans l'arbre sous LDRMM900R
    And LDROI2108 ne se trouve plus bien dans l'arbre sous LDRCC900R

