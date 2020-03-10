![]({{ basedir }}/resources/heia.eps){ width=10cm }

# {{ title }}

```{=latex}
\begin{center}
{\Large\textbf{Projet de semestre 6}}
\end{center}
\medskip

```

{{body}}

## Méta-données

{% if mandator %}
- Proposé par : {{ mandator }}{% endif -%}
{%- if faculty %}
- Filière : {{ faculty | join(", ") }}{% endif -%}
{%- if maxStud %}
- Nombre d'étudiant(s) : {{ maxStud }}{% endif -%}
{%- if students %}
- Etudiant(s) inscrit(s) : {{ students | join(", ") }}{% endif -%}
{%- if professors %}
- Professeur(s) : {{ professors | join(", ") }}{% endif %}

{% if keywords %}Mots clés: {{ keywords }}{% endif %}