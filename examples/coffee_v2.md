---
version: 2
type de projet: Projet d'approfondissement
année scolaire: 2020/2021
titre: Système IoT/Cloud pour la gestion de la machine à café
filières:
  - Informatique
  - Télécommunications
nombre d'étudiants: 1
mandants:
  - Grégory Marthe
professeurs co-superviseurs:
  - Philippe Joye
mots-clé: [IoT, Systèmes embarqués, Cloud]
langue: [F]
confidentialité: non
suite: non
---
```{=tex}
\begin{center}
\includegraphics[width=0.7\textwidth]{img/coffee.jpg}
\end{center}
```

## Description

La machine à café est bien souvent le matériel le plus important de l'ingénieur (et de l'étudiant eni ingénierie).
Dans la filière télécommunications, nous mettons à disposition deux machines Nespresso et une machine à thé dans
le labo C10.16. Les professeurs et les collaborateurs notent leur consommation de café sur une feuille A4 et les
étudiants payent directement en monnaie.

Le but de ce projet est de remplacer les décomptes de café par une solution informatique.

## Contraintes (négociables)

- Le système doit reconnaître l'utilisateur grâce à son badge
- Le lecteur de badge doit envoyer le numéro du badge vers un serveur à l'aide d'un système de type "publisher - subscriber"
- L'interface utilisateur (près de la machine à café) doit être un smartphone ou une tablette avec une "progressive web app".
- Le service doit être hébergé sur le cluster Kubernetes / Rancher de l'école
- Le back-end peut être écrit en Python, Javascript, TypeScript, Go ou Rust
- Le système doit offrir une interface d'administration simple et intuitive

## Objectifs/Tâches

- Elaboration d'un cahier des charges
- Analyse détaillée des frameworks, des langages et des outils, puis choix de la solution la plus appropriée pour le service
- Réalisation du back-end et du front-end (utilisateur final et admin)
- Tests et validation du système.
- Rédaction d'une documentation adéquate.
