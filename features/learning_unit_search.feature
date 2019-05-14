Feature: Recherche des unités d'enseignements.

  Background:
    Given La base de données est dans son état initial.
    And L'utilisateur est loggé en tant que gestionnaire facultaire ou central
    And Aller sur la page /learning_units/by_activity/
    And Réinitialiser les critères de recherche

  Scenario Outline: En tant que gestionnaire facultaire ou central, je recherche une UE par <search_field>.

    When Sélectionner <anac> dans la zone de saisie « Anac. »
    And Encoder la valeur <search_value> dans la zone de saisie <search_field>
    And Cliquer sur le bouton Rechercher (Loupe)

    Then Le nombre total de résultat est <result_count>
    And Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien <results>.

    Examples:
      | anac    | results                             | search_field       | search_value | result_count |
      | 2019-20 | WSBIM1203                           | acronym            | WSBIM1203    | 1            |
      | 2019-20 | LCRIM2101,LCRIM2103                 | requirement_entity | DRT          | 441          |
      | 2019-20 | LACTU2950                           | container_type     | Stage        | 556          |
      | 2019-20 | LCHM1111,LCHM1211,LCHM1331,LCHM2130 | tutor              | Devillers    | 4            |
