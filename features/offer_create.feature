Feature: Création d'offre

  Background:
    Given La base de données est dans son état initial.
    And les flags d'éditions des offres sont désactivés.
    And L'utilisateur est loggé en tant que gestionnaire central

    # TODO vérification au niveau de l'arbre. Ajout de authorized relationship
  Scenario Outline: 29 : En tant que gestionnaire central, je dois pouvoir créer une offre de type « formation ».
  Description :
  « Master 120 à finalité spécialisée »
  DROI2MS/TT LDROI200S DRT DRT
  + vérifier la structure Partie de base + Liste au choix
  « Certificat université 2ième cycle » CUIS2FC LCUIS100Q AGRO AGRO
  + vérifier la structure Partie de base

    Given Aller sur la page Catalogue de formations / Formation
    When Cliquer sur le menu « Actions »
    And Cliquer sur « Nouvelle Formation »
    And Encoder <type_de_formation> comme type de formation
    And Cliquer sur « Oui, je confirme »
    And Encoder <acronym> comme  Sigle/Intitulé abrégé
    And Encoder <code> comme Code
    And Encoder Entité de gestion
    And Encoder Entité d’administration
    And Encoder intitulé français
    And Encoder intitulé anglais
    And Cliquer sur l'onglet Diplômes/Certificats
    And Encoder <intitule_du_diplome> comme Intitulé du diplôme
    And Cliquer sur le bouton « Enregistrer »
    And Si une modal d'avertissement s'affiche, cliquer sur « oui »
    Then Vérifier que la formation <acronym> à bien été créée
    And Vérifier que le champ Sigle/Intitulé abrégé est bien <acronym>
    And Vérifier que le champ Code est bien <code>

    Examples:
      | acronym    | code      | type_de_formation                            | intitule_du_diplome |
      | DROI2MS/TT | LDROI200S | Master en 120 crédits à finalité spécialisée | Diplome en droit    |
      | CUIS2FC    | LCUIS100Q | Certificat d’université 2ème cycle           | Diplome en cuisine  |

  Scenario: 30 : En tant que gestionnaire central, je dois pouvoir créer une offre de type « mini- formation ».
  OPTIONENTF LSIPS100O CAMG CAMG
    Given Aller sur la page Catalogue de formations / Formation
    When Cliquer sur le menu « Actions »
    And Cliquer sur « Nouvelle Mini-Formation »
    And Encoder Option comme type de formation
    And Cliquer sur « Oui, je confirme »
    And Encoder OPTIONENTF comme  Sigle/Intitulé abrégé
    And Encoder LSIPS100O comme Code
    And Encoder Option en cuisine comme Intitulé en français
    And Encoder Entité de gestion
    And Cliquer sur le bouton « Enregistrer »

    Then Vérifier que la formation OPTIONENTF à bien été créée
    And Vérifier que le champ Sigle/Intitulé abrégé est bien OPTIONENTF
    And Vérifier que le champ Code est bien LSIPS100O
