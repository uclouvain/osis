Feature: Recherche des unités d'enseignements.

  Background:
    Given La base de données est dans son état initial.
    And L'utilisateur est loggé en tant que gestionnaire facultaire ou central
    And Aller sur la page de recherche d'UE
    And Réinitialiser les critères de recherche

  Scenario Outline: En tant que gestionnaire facultaire ou central, je recherche une UE par <search_field>.

    When Sélectionner <anac> dans la zone de saisie « Anac. »
    And Encoder la valeur <search_value> dans la zone de saisie <search_field>
    And Cliquer sur le bouton Rechercher (Loupe)

#    Then Le nombre total de résultat est <result_count>
    Then Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien <results>.

    Examples:
      | anac    | results                             | search_field       | search_value | result_count |
      | 2019-20 | WSBIM1203                           | acronym            | WSBIM1203    | 1            |
      | 2019-20 | LCRIM2101,LCRIM2103                 | requirement_entity | DRT          | 441          |
      | 2019-20 | LACTU2950                           | container_type     | Stage        | 556          |
      | 2019-20 | LCHM1111,LCHM1211,LCHM1331,LCHM2130 | tutor              | Devillers    | 4            |

  Scenario: En tant que gestionnaire facultaire ou central, je recherche des UE pour produire un Excel
    When Sélectionner 2019-20 dans la zone de saisie « Anac. »
    And Encoder la valeur Stage dans la zone de saisie container_type
    And Encoder la valeur LSM dans la zone de saisie requirement_entity
    And Cliquer sur le bouton Rechercher (Loupe)
    Then Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien LCEMS2915.

    When Ouvrir le menu « Exporter »
    And Sélection « Liste personnalisée des unités d’enseignement »
    And Cocher les cases « Programmes/regroupements » et « Enseignant(e)s »
    And Cliquer sur « Produire Excel »

    Scenario: UE externes (champs supplémentaires)
      Une centaine de gestionnaires pour les 3 premières ; pas de calendrier.

