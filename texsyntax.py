'''Modulis kuriame aprasytos skirtinga sintaksine prasem turincios 
komandos'''
import string, os, sys

# SIMBOLIAI VISADA RODO I OPCIJA
# GAL TO NEPRIREIKS, TACIAU PALIEKU GALIMYBE 
# PAKEISTI SINTAKSE IR KEICIANT PRIDETI OPCIJAS
# JOS PAGAL NUTYLEJIMA YRA None

#################### METACHARAI IR SPACE'AI

# METACHARAI, TURINTYS SINTAKSINE PRASME
METACHARACTERS={'#','$','%','^','{','}','_','~','\\'}
# METACHARO ESKEIPAS
METACHAR_ESC={'\\':None}
     
# EILUTES Whitespace'ai  
WHITESPACE={' ','\t'}

########## KOMANDOS 

# METACHARAS REISKIANTIS KOMANDOS PAVADINIMO PRADZIA
START_OF_CMD={'\\':None}
    
# Komanda sudarantys simboliai, * priskirima prie komandos pav 
COMMAND_CHARS=list(string.ascii_letters)
COMMAND_CHARS.append('*')

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
          '\\subsubsubparagraph':(0,1),
          '\\index':(1,),
          '\\commentinarg':(1,),
          '\\def':(1,1)}

############### KOMANDU ARGUMENTAI
    
# SKIRTUKAI APGAUBIANTYS PAGRINDINI ARGUMENTA
ARG_DELIMS={'{':'}'}

# KAS BUS ARGUMENTU, JEI TAI NE KOMANDA IR NE APSKLIAUSTAS
# REISKINYS
ARGUMENT=set(string.ascii_letters+string.digits)
# ARGUMENTO PRADZIOS SIMBOLIAI
BEGIN_OF_ARG=ARGUMENT
BEGIN_OF_ARG.update(set(START_OF_CMD.keys()))
BEGIN_OF_ARG.update(set(ARG_DELIMS.keys()))
# CHARAI KURIUOS SUTIKUS AISKU, KAD 


############### KOMENTARAI

# NUMATANT SINTAKSES KEITIMA
# METAJUNGIGLIS: (ISJUNGIKLIS, (SAVYBES,))
# w -- reiskia, kad po isjungimo bus suvalgomi whitespace
COMMENT={'%':('\n',('w',))}



# ENVIROMENTU PRADZIOS, GALI BUTI PERAPIBREZTOS
# TODEL REIKIA NUMATYTI GALIMYBE PAPILDYTI SITA LISTA
# ENV_START IR END NESUSIJE, NES GALIMA ABIBREZTI 
# \\be ir uzbaigti \\end{equation}                                      
ENV_START={'\\begin'}
ENV_END={'\\end'}

# ENVIROMENTAI GALI BUTI APIBREZTI KAIP 
# GRIEZTI SWITCHAI
E_SWITCH={'\\be':'\\ee'}

# ENVIROMENTAI SU OPCIONALIAIS ARGUMENTAIS
# IR JU PATTERNAI
ENVIROMENTS={'equation':(0,),
             'verbatim':(0,),
             'comment':(0,),
             'pf':(0,),
             'pf*':(1,0)}

# Griezti switchai, reikalaujantys isjungtuko
STRICT_SWITCH={'\\iffalse':'\\fi',
               '\\comment':'\\endcomment'}
STRICT_SWITCH.update(E_SWITCH)

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
# R_TYPE={'iverb':['\\verb'],
#        'nocomment':['\\index',],
#        'package':['\\usepackage'],
#        'syntax':['\\newcommand','\\def']
#        'env':['\\begin','\\end'],
#        'switch':['\\it','\\bf','\\em'],    # switchai neturi nei vieno argumento
#        'math':['\\frac','\\sin','\\leq']
#        'msymbol':['\\alpha','\\beta'],
#        'tsymbol':['\textmu','\textbackslash']}

##### R_TYPE APVERTIMAS #####
# kad galetume gauti komandos tipa
# GRAZINAMAS: TYPE
# TYPE={}
# LIST=[]
# for i in R_TYPE.keys():
#     LIST.append([i,R_TYPE[i]])
# for i,j in LIST:
#     for k in j: TYPE[k]=i 
# del LIST
# del R_TYPE
##############################

### Papildom COMMANDS is R_TYPE #####
# for i in R_TYPE['switch']:
#     COMMANDS[i]=None
######################################
    
# VERB APIBREZIMAI
# inline verbatimas
# argumento skirtukai -- bet kokie simboliai
VERB={'\\verb'}
# komandos turincios verbatiminius argumentus 
# verbatiminiais argumentais vadinsime
# visus argumentus, kuriu viduje keiciasi TeX sintakse
# Jei pagrindinis argumentas V, jei opcionalus v, jei ne verb None
VERB_CMD={'\\index':('V')}
VERB_ENV={'Verbatim','verbatim'}          # \begin{Verbatim}[commentchar=!]

        


COMMENT_CHAR={'%'}

########## NEAISKU AR REIKES ##################
# FIKCINE KOMANDA
COMMENT_CMD={'\commentinarg':('V')}
VERB_ARGS=VERB_CMD
# KOL KAS KOMENTARO TIPO ARGUMENTAI SUTAMPA SU VERBATIMO
VERB_ARGS.update(COMMENT_CMD)
###############################################

# KADA MESTI PARSE ERRORA
BAISUS_PAKETAI={'fancyvrb','listings'}
BAISIOS_KOMANDOS={'\\DefineShortVerb',     #\DefineShortVerb{ \|} -> |%labas%|
                  '\\UndefineShortVerb',
                  '\\newif',
                  '\\includecomment',
                  '\\excludecomment',
                  '\\specialcomment'}
