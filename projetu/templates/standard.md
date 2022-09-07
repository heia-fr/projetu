\BLOCK{ extends "base.md" }
\BLOCK{ block meta }
## Méta-données

\BLOCK{ if meta.mandantors }
- Mandant(s) : \VAR{ meta.mandantors | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.confidential }
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
\BLOCK{ if meta.max_students }
- Nombre maximum d'étudiant(s) : \VAR{ meta.max_students }
\BLOCK{ endif }
\BLOCK{ if meta.weight }
- Poids : \VAR{ meta.weight }
\BLOCK{ endif }
\BLOCK{ if meta.assigned_to }
- Attribué à : \VAR{ meta.assigned_to | join(", ") }
\BLOCK{ endif }
- Professeur : \VAR{ author }
\BLOCK{ if meta.professors }
- Co-superviseur(s): \VAR{ meta.professors | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.assistants }
- Assistants: \VAR{ meta.assistants | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.continuation }
- Ce projet de bachelor est la suite d'un travail de semestre réalisée par le même étudiant
\BLOCK{ endif }

\BLOCK{ if meta.keywords }
Mots clés: \VAR{ meta.keywords | join(", ") }
\BLOCK{ endif }
\BLOCK{ endblock }
