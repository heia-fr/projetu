# Projetu

Système de publication des projets d'étudiants (projets de semestre et travaux de diplômes)
à la Haute école d'ingénierie et d'architecture de Fribourg.

# Marche à suivre

Voici la marche à suivre pour proposer des projets:

- Créer un projet sur https://gitlab.forge.hefr.ch/, dans votre "namespace" (prénom.nom), avec le nom communiqué par le responsable de filière (par exemple `ps6-2019-2020`)
- Pour chaque projet, rédiger un fichier avec l'extension `.md`. Ce fichier se compose de deux parties:
  - Un "front matter" en _YAML_ avec les méta données du projet. Cette partie doit respecter le schéma [Kwalify](http://www.kuwata-lab.com/kwalify/) suivant : https://gitlab.forge.hefr.ch/jacques.supcik/projetu/-/blob/master/projetu/schemas/meta.yml
  - La donnée du projet en markdown avec des sections telles que "Contexte", "Objectifs", "Contraintes".
  
  Voici un exemple pour un tel fichier

  ```
  ---
  version: 1
  titre: Mon super projet
  filières:
    - Informatique
    - Télécommunications
  nombre d'étudiants: 1
  professeurs co-superviseurs:
    - Philippe Joye
  mots-clé: [IoT, Réseaux, Machine Learning]
  langue: F
  confidentialité: non
  suite: non
  ---
  ## Contexte

  Sit sint sit adipisicing excepteur cillum ullamco velit qui fugiat
  occaecat. Voluptate aliqua ex commodo aliqua commodo exercitation quis
  minim exercitation qui minim dolor. 
  
  ## Objectifs

  - Lorem ipsum
  - Dolor sit
  - Consectetuer
  - Adipiscing elit

  
  ## Contraintes

  - Diam
  - Nonummy nibh
  - Tincidunt
  ```

  Pour insérer une image, ajoutez l'image à votre projet et faites-y
  référence de la manière suivante (par exemple ici avec une image qui prendra 70% de la largeur du texte):

      ```{=tex}
      \begin{center}
      \includegraphics[width=0.7\textwidth,height=\textheight]{img/pro.jpg}
      \end{center}
      ```

- Définissez un fichier `.gitlab-ci.yml` avec le contenu suivant:

```yaml
image: "registry.forge.hefr.ch/jacques.supcik/projetu:latest"

build:
  script:
    ls *.md | grep -v README | xargs projetu --author="$GITLAB_USER_NAME" --template=ps.md --config /app/ps6-2019-2020.yml
    artifacts:
    paths:
      - ./*.pdf
```
  - A chaque fois que vous ferez un `git commit` et que vous enverrez les changements sur gitlab (avec un `git push`), le CI/CD de gitlab produira les PDFs correspondants à vous fichiers. Assurez-vous que la compilation ne produise pas d'erreur.
  
# Exemple

le projet https://gitlab.forge.hefr.ch/jacques.supcik/ps6-2019-2020 montre
comment le système fonctionne.

Il y a la description de deux projets avec des images.

Pour voir le résultat, allez sur https://gitlab.forge.hefr.ch/jacques.supcik/ps6-2019-2020/pipelines, puis cliquez sur le "vu" vert, puis sur "build":

![](doc/readme1.png)

Ensuite cliquez sur "browse":

![](doc/readme2.png)

Et vous verrez le résultat (pdf) de vos fichiers:

![](doc/readme3.png)
