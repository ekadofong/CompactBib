# CompactBib
A workaround to get a very compact • separated Latex bibliography. Latex wizardry framework for the pseudobib.tex file found here: https://tex.stackexchange.com/questions/165000/condense-non-numbered-bibliography-into-one-line

Usage:
Like compiling a normal bibtex file, you first add the citations to both the .tex and .bib files.
Then, run
> python3 bib_to_pseudobib.py mwe.tex mwe.bib
> 
This will generate pseudobib.tex. Now, instead of calling \bibliography{mwe.bib}, we call \input{pseudobib}. 
Your tex file should now compile with the bibliography as normal (compile twice as usual to link the \cite commands to the updated bibliography)!
