Feature: Modification des unités d'enseignement.
  Background:
    Given La base de données est dans son état initial.
    And La période de modification des programmes est en cours
    And L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité DRT

    Scenario: En tant que gestionnaire facultaire, je ne peux pas modifier uniquement les UE d'une autre fac.
      Given Aller sur la page de detail de l'ue: LLSMS2000
      When Cliquer sur le menu « Actions »
      Then L’action « Modifier » est désactivée.

    Scenario: En tant que gestionnaire facultaire, je peux modifier uniquement les UE de ma FAC.
      Given Aller sur la page de detail de l'ue: LDROI1004
      When Cliquer sur le menu « Actions »
      Then L’action « Modifier » est activée.



