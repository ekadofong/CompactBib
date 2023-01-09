import sys
import bibtexparser
import re

journal_mapping = {'\\aj':'AJ, ', '\\apj':'ApJ, ', '\\apjs': 'ApJS, ', '\\apjl':'ApJl, ', '\\aap': 'A\&A, ', '\\araa': 'ARA\&A, ', '\\mnras':'MNRAS, ',
                   'arXiv e-prints':'arXiv:', '\\pasp':'PASP, ', 'Science': 'Science, ', '\\pasj':'PASJ',
                   'Classical and Quantum Gravity': 'Classical and Quantum Gravity, '}
# \\ EXAMPLE OUTPUT
# \\ \bibitem[{Kado-Fong {et~al.}(2021b)}]{kadofong2021b}
# \\ Kado-Fong et al. 2021b, arXiv:2109.05034
def parse ( cd, suffix=None ):
    '''
    Convert bibtex entry to pseudobib entry
    '''
    varname = cd['ID']
    authors = cd['author'].replace('\n', '')
    auth_count = authors.count(' and ')+1
    if auth_count == 1:
        auth_name = authors.split(',')[0]
    elif auth_count == 2:
        auth_name = authors.split(',')[:2]
        auth_name[1] = auth_name[1].split(' and ')[1]
        auth_name = " \& ".join(auth_name)
    else:
        auth_name = "%s {et~al.}" % authors.split(',')[0]
    
    if suffix is None:
        if varname[-1].isdigit():
            suffix = ''
        else:
            suffix = varname[-1]
    
    if 'journal' in cd.keys():
        ref_type = 'journal'
    elif 'booktitle' in cd.keys():
        ref_type = 'booktitle'
    elif 'title' in cd.keys():
        ref_type = 'title'
    else:
        ref_type = None

    if ref_type is not None:
        # \\ separate format for e-prints
        if (cd['journal'] == 'arXiv e-prints' if ref_type=='journal' else False):
            ref = cd['pages']
        elif ref_type in ['journal', 'booktitle']:
            ref = (journal_mapping[cd[ref_type]] if ref_type=='journal' else (cd[ref_type]+', '))+ \
                  (cd['volume']+', ' if 'volume' in cd.keys() else '')+(cd['pages'] if 'pages' in cd.keys() else '')
        else:
            ref = cd[ref_type]
    else:
        ref = ''

    output = r'''\bibitem[{%s(%s%s)}]{%s}
%s %s%s, %s
''' % (auth_name, cd['year'], suffix, varname, auth_name, cd['year'], suffix, ref )
    return output

def make_biblist ( texfile ):
    '''
    Get list of used citations from .tex file
    '''
    with open(texfile, 'r') as f:  
        contents = re.sub(r"%.*\n", r"\n", f.read())        
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
        bib_data = bibtexparser.load(f)
        for varname in citations:
            if varname not in bib_data.entries_dict.keys():
                print('[WARNING] no entry for %s. Skipping.' % varname)
                continue
            else:
                print(f'{varname} found' )

            entry = bib_data.entries_dict[varname]
            ref = parse ( entry )
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
        print ( 'usage: python3 bib_to_pseudobib.py PATH/TO/TEXFILE PATH/TO/BIBFILE <opt PATH/TO/OUTPUTNAME>' )
        sys.exit(0)
    compile (*sys.argv[1:])
    
