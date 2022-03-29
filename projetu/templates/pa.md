\BLOCK{ extends "standard.md" }
\BLOCK{ block title }
```{=latex}
\includegraphics[width=7cm]{\VAR{ basedir }/resources/mse.pdf}
\hfill
\includegraphics[width=8.5cm]{\VAR{ basedir }/resources/heia.pdf}

```

# \VAR{ meta.title } \BLOCK{ if meta.assigned_to } (assigné)\BLOCK{ endif }

```{=latex}
\begin{center}
{\Large\textbf{\VAR{type_full} - \VAR{meta.academic_year}}} 
\end{center}
\medskip

```
\BLOCK{ endblock }