Feature: Modification d'offre

  Background:
    Given La base de données est dans son état initial.
    And La formation DROI2MS/TT doit exister en 2018
    And La formation DROI2MS/TT doit exister en 2019
    And La période de modification des programmes est en cours


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
    When Cliquer sur le menu « Actions »
    When Cliquer sur « Modifier »
    And Encoder 2021 comme  Fin
    And Cliquer sur le bouton « Enregistrer »
    And Si une modal d'avertissement s'affiche, cliquer sur « oui »

    Then Vérifier que la formation DROI2MS/TT a bien été mise à jour de 2019 à 2021

    Given Aller sur la page Catalogue de formations / Formation
    And Réinitialiser les critères de recherche
    And Encoder Tous comme Anac
    And Encoder DROI2MS/TT comme Sigle/Intitulé abrégé
    And Cliquer sur le bouton Rechercher (Loupe)
    And Vérifier qu'il n'y a que 4 résultats.

  Scenario: 33 : En tant que gestionnaire facultaire, je dois pouvoir ajouter une finalité dans une offre.

  Description : Ajouter DROI2MS/TT dans DROI2M
  -> BUG : on doit pouvoir attacher DROI2MS/TT dans les finalités de DROI2M
  -> OSIS-2990

  Scenario: 34 : En tant que gestionnaire facultaire, je dois pouvoir ajouter une UE de type mémoire dans les mémoires du tronc commun d’une offre.
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


  Scenario: 35 : En tant que gestionnaire facultaire, je dois pouvoir attacher un groupe au tronc commun d’une offre.036

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

  Scenario: 36 : En tant que gestionnaire facultaire, je dois pouvoir déplacer une UE d’un groupe vers un autre groupe.
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

    And Dans l'arbre et dans LDRCC900R, cliquer sur Détacher sur LDROI2108.
    And Cliquer sur « Enregistrer » dans la modal
    And LDROI2108 se trouve bien dans l'arbre sous LDRMM900R
    And LDROI2108 ne se trouve plus bien dans l'arbre sous LDRCC900R


  Scenario: 37 : En tant que gestionnaire facultaire, je ne dois pas pouvoir supprimer une option de la liste des options si cette option est toujours présente dans la liste des finalités.
  Description :
  Essayer de détacher une option de la liste d’option alors qu’elle est présente dans la liste des finalités (ex. LDROP2410O / OPTDROI2M/CP)

  Scenario: 38 : En tant que gestionnaire facultaire, je dois pouvoir déplacer une option d’un groupe vers un autre groupe.
  Déplacer une option dans GEST2M
  Détacher LGEST557O dans LGEST202G/LGEST202A/LGEST562G Le retrouver dans LGEST203G (ouvrir tout)
  Sélectionner LGEST557O
  Le rattacher dans LGEST202G/LGEST202A/LGEST562G
  Améliorations :
  a) Recherche rapide pour UE + OFFRE
  b) Actuellement Copier / Coller, il faudrait Couper / Coller

  Informations textuelles (alias générales)
  Gestion des attendus sur les diplômes
  Onglet et accès différents ; on peut modifier dans le passé ; principal accès en gestionnaire facultaire
  Programme type
  Recopier le programme de l’année précédente Modifier un programme existant
  Créer un nouveau programme type
  Candidature en ligne
  Pour le moment hors scope ; vue prof uniquement

