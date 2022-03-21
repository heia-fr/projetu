\BLOCK{ extends "base.md" }
\BLOCK{ block meta }
## Méta-données

\BLOCK{ if meta.mandants }
- Mandant(s) : \VAR{ meta.mandants | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta["confidentiality"] == "oui" }
- **Projet confidentiel**
\BLOCK{ endif }
\BLOCK{ if meta.departments }
- Filière(s) : \VAR{ meta.departments | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.orientations }
- Orientation(s) : \VAR{ meta.orientations | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.instituts }
- Instituts(s) : \VAR{ meta.instituts | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.language }
- Langue : \VAR{ meta.language | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta["number of students"] }
- Nombre maximum d'étudiant(s) : \VAR{ meta["number of students"] }
\BLOCK{ endif }
\BLOCK{ if meta["assigned to"] }
- Attribué à : \VAR{ meta["assigned to"] | join(", ") }
\BLOCK{ endif }
- Professeur : \VAR{ author }
\BLOCK{ if meta["co-supervising professors"] }
- Co-superviseur(s): \VAR{ meta["co-supervising professors"] | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.assistants }
- Assistants: \VAR{ meta.assistants | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.continuation == "oui" }
- Ce projet de bachelor est la suite d'un travail de semestre réalisée par le même étudiant
\BLOCK{ endif }

\BLOCK{ if meta["keywords"] }
Mots clés: \VAR{ meta["keywords"] | join(", ") }
\BLOCK{ endif }
\BLOCK{ endblock }
