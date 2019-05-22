Feature: Consultation des Unités d'enseignement.

  Background:
    Given La base de données est dans son état initial.
    And L’utilisateur est dans le groupe « faculty manager »

  Scenario: En tant que gestionnaire facultaire, je ne peux pas modifier uniquement les UE d'une autre fac.
    Given Aller sur la page de detail de l'ue: LCHM1211 en 2018-19
    When Cliquer sur l'onglet Formations
    Then Vérifier que l'unité d'enseignement est incluse dans LBBMC365R, LBBMC951R, LCHIM501F, LCHIM971R
    Then Vérifier que BIOL1BA à la ligne 1 a 88 inscrits dont 4 à l'ue
    Then Vérifier que CHIM11BA à la ligne 2 a 63 inscrits dont 1 à l'ue
    Then Vérifier que CHIM1BA à la ligne 3 a 53 inscrits dont 34 à l'ue

  Scenario: En tant que gestionnaire facultaire, je dois pouvoir consulter l’onglet « Enseignants ».
    Given Aller sur la page de detail de l'ue: LCHM1211 en 2018-19
    When Cliquer sur l'onglet Enseignant·e·s

