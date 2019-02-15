### Commits : 
- Ajouter un message explicite à chaque commit
- Commiter souvent = diff limité = facilité d'identification de commits amenant une régression = facilité de revert

### Lisibilité du code :
- Séparation des classes: deux lignes vides
- Séparation des methodes de class: une ligne vide
- Séparation des fonctions: deux lignes vides
- Le nom d'une fonction doit être explicite et claire sur ce qu'elle fait (un 'get_' renvoie un élément, un 'search_' renvoie une liste d'élements...)

### Coding style :
On se conforme au [guide PEP8](https://www.python.org/dev/peps/pep-0008/#indentation)

Dans la mesure du possible, on essaie de tenir compte des conseils suivants : 
- Pour représenter une structure de données (list, dict, etc.), on peut passer une ligne entre chaque élément, ainsi qu'après l'ouverture de la structure et avant sa fermeture, si la liste est longue et/ou contient de longs éléments et/ou s'étend sur plusieurs lignes.
```python
# Mauvais
fruits = ['banane', 'pomme', 'poire', 'long_element_in_list_1', 'long_element_in_list_2', 'long_element_in_list_3', 'long_element_in_list_4'] 
légumes = {'1': 'carotte', '2': 'courgette', 
    '3': 'salade'}
            
# Bon
fruits = [
    'banane',
    'pomme',
    'poire',
    'long_element_in_list_1',
    'long_element_in_list_2',
    'long_element_in_list_3',
    'long_element_in_list_4'
]
légumes = {
    '1': 'carotte', 
    '2': 'courgette', 
    '3': 'salade',
}
```

- Le dernier élément de la structure a également une virgule. Cela permet d'éviter que cette ligne apparaisse dans le diff de git quand on rajoute un élément à la fin de structure.
```python
# Mauvais
fruits = [
    'banane',
    'pomme',
    'poire'
]
# Bon
légumes = {
    '1': 'carotte', 
    '2': 'courgette', 
    '3': 'salade',
}
```

- Lors d'un appel de fonction à plusieurs paramètres, si tous les paramètres ne tiennent pas sur une ligne, on passe une ligne entre chaque paramètre, ainsi qu'après l'ouverture de la liste de paramètres et avant sa fermeture.
```python
# Mauvais
result = my_function(first_long_parameter, second_parameter_which_has_a_really_really_long_name, third_parameter_which_has_an_even_longer_name)

result = my_function(first_parameter, 
                     second_parameter, 
                     third_parameter)
# Bon
result = my_function(
    first_parameter,
    second_parameter,
    third_parameter
)
```

- Les règles précédentes sont cumulatives : 
```python
# Mauvais
return render(request, "template.html", {
        'students': students, 'faculties': faculties,
        'teacher': teacher
        })

# Bon
return render(
    request,
    "template.html",
    {
        'students': students,
        'faculties': faculties,
        'teacher': teacher,
    }
)
```
- Voir en plus le [Coding Style de Django](https://docs.djangoproject.com/en/1.11/internals/contributing/writing-code/coding-style/).

### Documentation du code :
- Documenter les fonctions (paramètres, fonctionnement, ce qu'elle renvoie)
- Ne pas hésiter à laisser une ligne de commentaire dans le code, décrivant brièvement le fonctionnement d'algorithme plus compliqué/plus longs

### Traductions :
- Voir https://github.com/uclouvain/osis/blob/dev/doc/technical-manual.adoc#internationalization
- Les "Fuzzy" doivent être supprimés si la traduction du développeur diffère de la traduction proposée (le "fuzzy" signifiant que GetText a tenté de traduire la clé en retrouvant une similitude dans une autre clé).

### Réutilisation du code :
- Ne pas créer de fonctions qui renvoient plus d'un seul paramètre (perte de contrôle sur ce que fait la fonction et perte de réutilisation du code)
- Ne pas faire de copier/coller ; tout code dupliqué ou faisant la même chose doit être implémenté dans une fonction documentée qui est réutilisable
- Ne pas utiliser de 'magic_number' (constante non déclarée dans une variable). Par exemple, pas de -1, 1994, 2015 dans le code, mais déclarer en haut du fichier des variables sous la forme LIMIT_START_DATE=1994, LIMIT_END_DATE=2015, etc.

### Performance :
- Ne pas faire d'appel à la DB (pas de queryset) dans une boucle 'for' :
    - Récupérer toutes les données nécessaires en une seule requête avant d'effectuer des opérations sur les attributs renvoyés par le Queryset
    - Si la requête doit récupérer des données dans plusieurs tables, utiliser le select_related fourni par Django (https://docs.djangoproject.com/en/1.9/ref/models/querysets/#select-related)
    - Forcer l'évaluation du Queryset avant d'effectuer des récupération de données avec *list(a_queryset)* 

### Modèle :
- Chaque fichier décrivant un modèle doit se trouver dans le répertoire *'models'*
- Chaque fichier contenant une classe du modèle ne peut renvoyer que des instances du modèle qu'elle déclare. Autrement dit, un fichier my_model.py contient une classe MyModel() et des méthodes qui ne peuvent renvoyer que des records venant de MyModel
- Un modèle ne peut pas avoir un champs de type "ManyToMany" ; il faut toujours construire une table de liaison, qui contiendra les FK vers les modèles composant la relation ManyToMany.
- Lorsqu'un nouveau modèle est créé (ou que de nouveaux champs sont ajoutés), il faut penser à mettre à jour l'admin en conséquence (raw_id_fields, search_fields, list_filter...). 
- Ne pas créer de **clé étrangère** vers le modèle auth.User, mais vers **base.Person**. Cela facilite la conservation des données du modèe auth lors des écrasements des DB de Dev, Test et Qa.

### Business :
- Les fonctions propres à des fonctionnalités business (calculs de crédits ou volumes, etc.) doivent se trouver dans un fichier business. Ces fichiers sont utilisés par les Views et peuvent appeler des fonctions du modèle (et non l'inverse !). 
- Les fonctions business ne peuvent pas recevoir l'argument 'request', qui est un argument propre aux views.

### Migration :
- Ne pas utiliser le framework de persistence de Django lorsqu'il y a du code à exécuter dans les fichiers de migration. Il faut plutôt utiliser du SQL natif (voir https://docs.djangoproject.com/fr/1.10/topics/db/sql/ et https://docs.djangoproject.com/fr/1.10/ref/migration-operations/)

### Dépendances entre applications : 
- Ne pas faire de références des applications principales ("base" et "reference") vers des applications tierces (Internship, assistant...)
- Une application peut faire référence à une autre app' en cas de dépendance business (exemple: 'assessments' a besoin de 'attribution').

### Vue :
- Ne pas faire appel à des méthodes de queryset dans les views (pas de MyModel.filter(...) ou MyModel.order_by() dans les vues). C'est la responsabilité du modèle d'appliquer des filtres et tris sur ses queryset. Il faut donc créer une fonction dans le modèle qui renvoie une liste de records filtrés sur base des paramètres entrés (find_by_(), search(), etc.).
- Ajouter les annotations pour sécuriser les méthodes dans les vues (user_passes_tests, login_required, require_permission)
- Les vues servent de "proxy" pour aller chercher les données nécessaires à la génération des pages html, qu'elles vont chercher dans la couche "business" ou directement dans la couche "modèle". Elles ne doivent donc pas contenir de logique business

### Formulaire :
- Utiliser les objets Forms fournis par Django (https://docs.djangoproject.com/en/1.9/topics/forms/)

### Template (HTML)
- Privilégier l'utilisation Django-Bootstrap3
- Tendre un maximum vers la réutilisation des blocks ; structure :
```
[templates]templates                                  # Root structure
├── [templates/blocks/]blocks                                # Common blocks used on all 
│   ├── [templates/blocks/forms/]forms
│   ├── [templates/blocks/list/]list
│   └── [templates/blocks/modal/]modal
├── [templates/layout.html]layout.html                      # Base layout 
└── [templates/learning_unit/]learning_unit
    ├── [templates/learning_unit/blocks/]blocks                        # Block common on learning unit
    │   ├── [templates/learning_unit/blocks/forms/]forms
    │   ├── [templates/learning_unit/blocks/list/]list
    │   └── [templates/learning_unit/blocks/modal/]modal
    ├── [templates/learning_unit/layout.html]layout.html               # Layout specific for learning unit
    ├── [templates/learning_unit/proposal/]proposal
    │   ├── [templates/learning_unit/proposal/create.html]create_***.html
    │   ├── [templates/learning_unit/proposal/delete.html]delete_***.html
    │   ├── [templates/learning_unit/proposal/list.html]list.html
    │   └── [templates/learning_unit/proposal/update.html]update_***.html
    └── [templates/learning_unit/simple/]simple
        ├── [templates/learning_unit/simple/create.html]create_***.html
        ├── [templates/learning_unit/simple/delete.html]delete_***.html
        ├── [templates/learning_unit/simple/list.html]list.html
        └── [templates/learning_unit/simple/update.html]update_***.html
```

### Sécurité :
- Ne pas laisser de données sensibles/privées dans les commentaires/dans le code
- Dans les URL (url.py), on ne peut jamais passer l'id d'une personne en paramètre (par ex. '?tutor_id' ou '/score_encoding/print/34' sont à éviter! ). 
- Dans le cas d'insertion/modification des données venant de l'extérieur (typiquement fichiers excels), s'assurer que l'utilisateur qui injecte des données a bien tous les droits sur ces données qu'il désire injecter. Cela nécessite une implémentation d'un code de vérification.

### Permissions :
- Lorsqu'une view nécessite des permissions d'accès spécifiques (en dehors des permissions frounies par Django), créer un décorateur dans le dossier "perms" des "views". Le code business propre à la permission devra se trouver dans un dossier "perms" dans "business". Voir "base/views/learning_units/perms/" et "base/business/learning_units/perms/".

### Pull request :
- Ne fournir qu'un seul fichier de migration par issue/branche (fusionner tous les fichiers de migrations que vous avez en local en un seul fichier)
- Ajouter la référence au ticket Jira dans le titre de la pull request (format = "OSIS-12345")
- Utiliser un titre de pull request qui identifie son contenu (facilite la recherche de pull requests et permet aux contributeurs du projet d'avoir une idée sur son contenu)

### Pull request de màj de la référence d'un submodule :
Quand la PR correspond à la mise-à-jour de la référence pour un submodule, indiquer dans la description de la PR les références des tickets Jira du submodule qui passent dans cette mise-à-jour de référence (format : "IUFC-123").

Pour les trouver : 
1) Une fois la PR ouverte, cliquer sur l'onglet "Files Changed"
2) Cliquer sur "x files" dans le texte "Submodule xyz updated x files"
3) Cela ouvre la liste des commits qui vont passer dans la mise-à-jour de référence -> les références des tickets Jira sont indiquées dans les messages de commits.

### Ressources et dépendances :
- Ne pas faire de référence à des librairie/ressources externes ; ajouter la librairie utilisée dans le dossier 'static'

### Emails
- Utiliser la fonction d'envoi de mail décrite dans `osis_common/messaging/send_mail.py`. Exemple:
```python
from osis_common.messaging import message_config, send_message as message_service
from base.models.person import Person

def send_an_email(receiver: Person):
    receiver = message_config.create_receiver(receiver.id, receiver.email, receiver.language)
    table = message_config.create_table(
        'Table title', 
        ['column 1', 'column 2'], 
        ['content col 1', 'content col 2']
    )
    context = {
        'variable_used_in_template': 'value',
    }
    subject_context = {
        'variable_used_in_subject_context': 'value',
    }
    message_content = message_config.create_message_content(
        'template_name_as_html', 
        'template_name_as_txt', 
        [table], 
        [receiver],
        context,
        subject_context
    )
    return message_service.send_messages(message_content)

```

### PDF : 
- Utiliser WeasyPrint pour la création de documents PDF (https://weasyprint.org/).


### Tests : 
#### Vues :
Idéalement lorsqu'on teste une view, on doit vérifier :
- Le template utilisé (assertTemplateUsed)
- Les redirections en cas de succès/erreurs
- Le contenu du contexte utilisé dans le render du template
- Les éventuels ordres de listes attendus
