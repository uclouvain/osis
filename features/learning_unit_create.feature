Feature: Création de d'unité d'enseignement.

  Background:
    Given La base de données est dans son état initial.

  Scenario: En tant que gestionnaire facultaire, je dois pouvoir créer un nouveau partim.
    Given La période de modification des programmes est en cours
    And L’utilisateur est dans le groupe « faculty manager »
    And L’utilisateur est attaché à l’entité MED
    Given Aller sur la page de detail de l'ue: WPEDI2190
    When Cliquer sur le menu « Actions »
    And Cliquer sur le menu « Nouveau partim »
    And Encoder 3 comme Code dédié au partim
    And Cliquer sur le bouton « Enregistrer »

    Then Vérifier que le partim WPEDI21903 a bien été créé de 2019-20 à 2024-25.
    When Cliquer sur le lien WPEDI2190
    Then Vérifier que le cours parent WPEDI2190 contient bien 3 partims.

#  Scenario: En tant que gestionnaire central, je dois pouvoir mettre à jour une UE.
#  Description : en particulier les crédits et la périodicité + vérifier que les UE peuvent
#  être mises à jour par la gestionnaire central en dehors de la période de modification des programmes.
#    Given La période de modification des programmes n’est pas en cours
#    And L’utilisateur est dans le groupe « central manager »
#    And Aller sur la page de detail de l'ue: LDROI1004
#
#    When Cliquer sur le menu « Actions »
#    And Cliquer sur le menu « Modifier »
#    And Décocher la case « Actif »
#    And Encoder 12 comme Crédits
#    And Encoder bisannuelle paire comme Périodicité
#    And Cliquer sur le bouton « Enregistrer »
#    And A la question, « voulez-vous reporter » répondez « oui »
#
#    Then Vérifier que le Crédits est bien 12
#    And Vérifier que la Périodicité est bien bisannuelle paire
#    And Rechercher LDROI1004 en 2020-21
#    And Vérifier que le Crédits est bien 12
#    And Vérifier que la Périodicité est bien bisannuelle paire
