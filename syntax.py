'''Modulis kuriame aprasytos skirtinga sintaksine prasem turincios 
komandos'''

# METACHARAI, TURINTYS SINTAKSINE PRASME
METACHARACTERS={'#','$','%','^','{','}','_','~','\\'}
# Whitespace'ai kurie yra ne newline 
WHITESPACE={' ','\t'}
# komanda sudarantys simboliai, * priskirima prie komandos pav 
COMMAND_CHARS=list(string.ascii_letters)
COMMAND_CHARS.append('*')
# KAS BUS ARGUMENTU, JEI TAI NE KOMANDA IR NE APSKLIAUSTAS
# REISKINYS
ARGUMENT=list(string.ascii_letters+string.digits)

# SARASAS NURODANTIS KIEK PAGRINDINIU IR OPCIONALIU ARGUMENTU TURI KOMANDA
# NURODOMAS PATTERNAS 1--pagr argumentas 0--opcionalus 
COMMANDS={'\\begin':(1,0),
          '\\end':(1,),
          '\\frac':(1,1),
          '\\usepackage':(0,1),
          '\\rule':(0,1,1),
          '\\footnote':(0,1),
          '\\newcommand':(1,0,0,1),
          '\\renewcommand':(1,0,0,1),
          '\\label':(1,),
          '\\part':(0,1),
          '\\chapter':(0,1),
          '\\section':(0,1),
          '\\subsection':(0,1),
          '\\subsubsection':(0,1),
          '\\paragraph':(0,1),
          '\\subparagraph':(0,1),
          '\\subsubparagraph':(0,1),
          '\\subsubsubparagraph':(0,1)}

# ENVIROMENTAI SU OPCIONALIAIS ARGUMENTAIS
# IR JU PATTERNAI
ENVIROMENTS={'equation':(0,),
             'verbatim':(0,),
             'comment':(0,),
             'pf':(0,),
             'pf*':(1,0)}

# Griezti switchai, reikalaujantys isjungtuko
STRICT_SWITCH={{'\\iffalse':'\\fi'},
               {'\\comment':'\\endcomment'}}

# Negriezti switchai: ju gyvavimo sritis
# yra esama aplinka
SWITCH={'\\it','\\tt','\\em'}

# PAGRINDINIAI KOMANDU TIPAI 
#     * iverb -- inline verbatimas (skirtukai--bet kokie nonalpha symboliai)
#     * nocomment -- komandos kuriu argumentuose % nereiskia komentaro pradzios
#     * package -- \usepackage
#     * env -- enviromentu tagai \begin \end
#     * switch -- jungiklis
#     * math -- matematines komandos
#     * covered -- komandos kuriu argumentai apgaubia komanda is abieju pusiu

# GREITESNIAM TIPO SUZINOJIMUI
R_TYPE={'iverb':['\\verb'],
       'nocomment':['\\index',],
       'package':['\\usepackage'],
       'syntax':['\\newcommand','\\def']
       'env':['\\begin','\\end'],
       'switch':['\\it','\\bf','\\em'],    # switchai neturi nei vieno argumento
       'math':['\\frac','\\sin','\\leq']
       'msymbol':['\\alpha','\\beta'],
       'tsymbol':['\textmu','\textbackslash']}

##### R_TYPE APVERTIMAS #####
# kad galetume gauti komandos tipa
# GRAZINAMAS: TYPE
TYPE={}
LIST=[]
for i in R_TYPE.keys():
    LIST.append([i,R_TYPE[i]])
for i,j in LIST:
    for k in j: TYPE[k]=i 
del LIST
del R_TYPE
##############################

### Papildom COMMANDS is R_TYPE #####
for i in R_TYPE['switch']:
    COMMANDS[i]=None
######################################
    
BAISUS_PAKETAI={'fancyvrb','listings'}
BAISIOS_KOMANDOS={'\\DefineShortVerb',     #\DefineShortVerb{ \|} -> |%labas%|
                  '\\UndefineShortVerb',
                  '\\newif',
                  '\\includecomment',
                  '\\excludecomment',
                  '\\specialcomment'}

### Verbatimo enviromentai
VERB_ENV={'Verbatim','verbatim'}          # \begin{Verbatim}[commentchar=!]
