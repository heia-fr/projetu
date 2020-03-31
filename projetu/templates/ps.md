![](\VAR{ basedir }/resources/heia.eps){ width=10cm }

# \VAR{ meta.titre }

```{=latex}
\begin{center}
{\Large\textbf{\VAR{config.type}}}
\end{center}
\medskip

```

\VAR{body}

## Méta-données

\BLOCK{ if meta.mandants }
- Mandant(s) : \VAR{ meta.mandants | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta["proposé par étudiant"] }
- Proposé par : \VAR{ meta["proposé par étudiant"] }
\BLOCK{ endif }
\BLOCK{ if meta.filières }
- Filière(s) : \VAR{ meta.filières | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.orientations }
- Orientation(s) : \VAR{ meta.orientations | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.instituts }
- Instituts(s) : \VAR{ meta.instituts | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.langue }
- Langue : \VAR{ meta.langue }
\BLOCK{ endif }
\BLOCK{ if meta["nombre d'étudiants"] }
- Nombre maximum d'étudiant(s) : \VAR{ meta["nombre d'étudiants"] }
\BLOCK{ endif }
\BLOCK{ if meta.students }
- Etudiant(s) inscrit(s) : \VAR{ meta.students | join(", ") }
\BLOCK{ endif }
- Professeur : \VAR{ author }
\BLOCK{ if meta["professeurs co-superviseurs"] }
- Co-superviseur(s): \VAR{ meta["professeurs co-superviseurs"] | join(", ") }
\BLOCK{ endif }
\BLOCK{ if meta.assistants }
- Assistants: \VAR{ meta.assistants | join(", ") }
\BLOCK{ endif }

\BLOCK{ if meta["mots-clé"] }
Mots clés: \VAR{ meta["mots-clé"] | join(", ") }
\BLOCK{ endif }