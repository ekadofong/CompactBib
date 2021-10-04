import sys
import re

journal_mapping = {'aj':'AJ, ', 'apj':'ApJ, ', 'mnras':'MNRAS, ','arXiv e-prints':'arXiv:'}
# \\ EXAMPLE OUTPUT
# \\ \bibitem[{Kado-Fong {et~al.}(2021b)}]{kadofong2021b}
# \\ Kado-Fong et al. 2021b, arXiv:2109.05034
def parse ( entry, suffix=None ):
    '''
    Convert bibtex entry to pseudobib entry
    '''
    varname = re.findall( '(?<={).*(?=,)', entry.splitlines()[0])[0]
    lines = (entry.splitlines()[1:])
    cd = {}
    for line in lines:
        if '=' not in line:
            continue
        else:
            key = re.findall ( '.*(?=\=)', line )[0].strip()            
            value = re.findall ( '(?<=\=).*', line )[0]          
            value = value.strip(' {},"\\')  
            cd[key] = value
    lastname = cd['author'].split(',')[0].strip('}')
    
    if suffix is None:
        if varname[-1].isdigit():
            suffix = ''
        else:
            suffix = varname[-1]
            
    # \\ separate format for e-prints
    if cd['journal'] == 'arXiv e-prints':
        ref = cd['pages']
    else:
        ref = '%s%s, %s' % (journal_mapping[cd['journal']], cd['volume'], cd['pages'])

    output = r'''\bibitem[{%s {et~al.}(%s%s)}]{%s}
%s et al. %s%s, %s
''' % (lastname, cd['year'], suffix, varname, lastname, cd['year'], suffix, ref )
    return output

def make_biblist ( texfile ):
    '''
    Get list of used citations from .tex file
    '''
    with open(texfile, 'r') as f:  
        contents = f.read()        
        _citations = re.findall (r'(?<=\\cite).*?(?=})', contents) # \\ python requires fixed-width look-behinds
        _citations = [ cc.split('{')[1] for cc in _citations ] # \\ so I'll just look for the { start 

    # \\ split up entries with \cite{A,B,C}
    citations = []
    for cite in _citations:
        citations.extend ( [cc.strip() for cc in cite.split(',')] )
    return sorted ( list ( set ( citations ) ) )

def get_bibentries ( citations, bibfile ):
    '''
    Look up citations in .bib file
    '''
    references = []
    with open(bibfile, 'r') as f:
        bfile = f.read ()    
        for varname in citations:
            entry = re.findall( '{%s.*?(?=@|$)'%varname, bfile, re.DOTALL )
            if len(entry) == 0:
                print('[WARNING] no entry for %s. Skipping.' % varname)
                continue
            elif len(entry) > 1:
                print ('[WARNING] Duplicate entries for %s? Ignoring duplicates.' % varname )
            else:
                print(f'{varname} found' )

            ref = parse ( entry[0] )
            references.append(ref)
    return '\n'.join(references)


def pseudobib ( texfile, bibfile ):
    '''
    Construct pseudobib file
    '''
    preamble=r'''\begingroup
\small    
\renewcommand{\section}[2]{}%
\begin{thebibliography}{93}
\expandafter\ifx\csname natexlab\endcsname\relax\def\natexlab#1{#1}\fi

'''
    postamble=r'''
\end{thebibliography}
\endgroup'''    
    citations = make_biblist ( texfile=texfile )
    references = get_bibentries ( citations, bibfile )
    return preamble + references + postamble
    
def compile ( texfile, bibfile, pseudobib_name='./pseudobib.tex' ):
    pbib = pseudobib ( texfile, bibfile )
    with open ( pseudobib_name, 'w' ) as f:
        print ( pbib, file=f )
        
if __name__ == '__main__':
    if len(sys.argv) == 1 or (sys.argv[1] == '-h') or (sys.argv[1]=='--help'):
        print ( 'usage: python3 bib_to_pseudobib PATH/TO/TEXFILE PATH/TO/BIBFILE <opt PATH/TO/OUTPUTNAME>' )
        sys.exit(0)
    compile (*sys.argv[1:])
    