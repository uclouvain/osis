Feature: Modification des unités d'enseignement.

  Background:
    Given La base de données est dans son état initial.

  Scenario: En tant que gestionnaire facultaire, je ne peux pas modifier uniquement les UE d'une autre fac.
    Given La période de modification des programmes est en cours
    And L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité DRT
    Given Aller sur la page de detail de l'ue: LLSMS2000
    When Cliquer sur le menu « Actions »
    Then L’action « Modifier » est désactivée.

  Scenario: En tant que gestionnaire facultaire, je peux modifier uniquement les UE de ma FAC.
    Given La période de modification des programmes est en cours
    And L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité DRT
    Given Aller sur la page de detail de l'ue: LDROI1004
    When Cliquer sur le menu « Actions »
    Then L’action « Modifier » est activée.

  Scenario: En tant que gestionnaire facultaire, je dois pouvoir mettre à jour une UE.
    Given La période de modification des programmes est en cours
    And L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité DRT
    Given Aller sur la page de detail de l'ue: LDROI1004
    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Modifier »
    And Décocher la case « Actif »
    And Encoder Q1 et Q2 comme Quadrimestre
    And Encoder 1 comme Session dérogation
    And Encoder 30 comme volume Q2 pour la partie magistrale
    And Encoder 30 comme volume Q1 pour la partie magistrale
    And Encoder 6 comme volume Q1 pour la partie pratique
    And Encoder 6 comme volume Q2 pour la partie pratique
    And Cliquer sur le bouton « Enregistrer »
    And A la question, « voulez-vous reporter » répondez « non »

    Then Vérifier que le cours est bien Inactif
    And Vérifier que le Quadrimestre est bien Q1 et Q2
    And Vérifier que la Session dérogation est bien 1
    And Vérifier que le volume Q1 pour la partie magistrale est bien 30
    And Vérifier que le volume Q2 pour la partie magistrale est bien 30
    And Vérifier que le volume Q1 pour la partie pratique est bien 6
    And Vérifier que la volume Q2 pour la partie pratique est bien 6


  Scenario: En tant que gestionnaire central, je dois pouvoir mettre à jour une UE.
  Description : en particulier les crédits et la périodicité + vérifier que les UE peuvent
  être mises à jour par la gestionnaire central en dehors de la période de modification des programmes.
    Given La période de modification des programmes n’est pas en cours
    And L’utilisateur est dans le groupe « central manager »
    And Aller sur la page de detail de l'ue: LDROI1004

    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Modifier »
    And Décocher la case « Actif »
    And Encoder 12 comme Crédits
    And Encoder bisannuelle paire comme Périodicité
    And Cliquer sur le bouton « Enregistrer »
    And A la question, « voulez-vous reporter » répondez « oui »

    Then Vérifier que le Crédits est bien 12
    And Vérifier que la Périodicité est bien bisannuelle paire
    And Rechercher LDROI1004 en 2020-21
    And Vérifier que le Crédits est bien 12
    And Vérifier que la Périodicité est bien bisannuelle paire
