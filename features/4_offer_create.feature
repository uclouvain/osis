Feature: Création d'offre

  Background:
    Given La base de données est dans son état initial.
    And L'utilisateur est loggé en tant que gestionnaire central.
    And L’utilisateur est attaché à l’entité UCL

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
    And Encoder <entite_de_gestion> comme Entité de gestion
    And Encoder <entite_dadministration> comme Entité d’administration
    And Cliquer sur l'onglet Diplômes/Certificats
    And Encoder <intitule_du_diplome> comme Intitulé du diplôme
    And Cliquer sur le bouton « Enregistrer »
    And Si une modal d'avertissement s'affiche, cliquer sur « oui »
    Then Vérifier que la formation <acronym> à bien été créée de 2018 à 2024
    And Vérifier que le champ Sigle/Intitulé abrégé est bien <acronym>
    And Vérifier que le champ Code est bien <code>
    And Vérifier que le champ Entité de gestion est bien <entite_de_gestion>
    And Vérifier que le champ Entité d'administration est bien <entite_dadministration>

    When Ouvrir l'arbre
    Then Vérifier que le(s) enfant(s) de <code> sont bien <children>


    Examples:
      | acronym    | code      | type_de_formation                            | entite_de_gestion | entite_dadministration | intitule_du_diplome | children            |
      | DROI2MS/TT | LDROI200S | Master en 120 crédits à finalité spécialisée | DRT               | DRT                    | Diplome en droit    | LDROI101T,LDROI300G |
      | CUIS2FC    | LCUIS100Q | Certificat d’université 2ème cycle           | AGRO              | AGRO                   | Diplome en cuisine  | LCUIS100T           |

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
    And Encoder CAMG comme Entité de gestion
    And Cliquer sur le bouton « Enregistrer »

    Then Vérifier que la formation OPTIONENTF à bien été créée de 2018 à 2024
    And Vérifier que le champ Sigle/Intitulé abrégé est bien OPTIONENTF
    And Vérifier que le champ Code est bien LSIPS100O
    And Vérifier que le champ Entité de gestion est bien CAMG

    When Ouvrir l'arbre
    Then Vérifier que le(s) enfant(s) de LSIPS100O sont bien LSIPS100T
