import pandas as pd
import query.dataset as ds
import datetime


# Code header with development details
def codeBrief(metadata: dict) -> str:
    searchName = metadata['Search'][0]
    appName = metadata['Application'][0]
    author = metadata['Author'][0]
    date = datetime.date.today()

    string = ('(:~\n'
              '::\n'
              f':: Application Name: {appName}\n'
              '::\n'
              f':: Search Name: {searchName}\n'
              '::\n'
              '::\n'
              ':: Copyright: Medtronic\n'
              '::\n'
              f':: @author {author}\n'
              f':: @since {date.strftime("%b %d, %Y")}\n'
              ':: @version 1.0\n'
              ':)\n\n')

    return string


# return the namespace definitions
def declareNamespace() -> str:
    string = ('declare namespace ia = (: :) "urn:x-emc:ia:schema:fn";\n'
              'declare namespace table = (: :)  "urn:x-emc:ia:schema:table";\n')
    return string


# declare and define a variable
def declareVariables(variables: list) -> str:
    string = ('declare variable $page external;\n'
              'declare variable $size external;\n')

    for x in variables:
        string += 'declare variable $' + str(x) + ' external := \'\';\n'

    string += '\ndeclare variable $limit := 2000;\n\n'

    return string


# Encryption declaration
def encryptFunction():
    string = 'declare function ia:create-encrypted-condition($expressionStr as xs:string, $operator as xs:string, $columnValue as xs:string*) as xs:string external;\n'

    return string


# Decryption declaration
def decryptFunction():
    string = 'declare function ia:decrypt-value($columnValue as xs:string*) as xs:string* external;\n'

    return string


# return the definition of addClause function
def addClause() -> str:
    string = ('declare function local:addClause($var as xs:string*, $expr as xs:string) as xs:string* {\n'
              '    if (empty($var) or $var = "" or normalize-space($var) = "") then ""\n'
              '    else concat("[", $expr , "]") \n'
              '};\n')

    return string


# return the definition of getResultsPage function
def getResultsPage() -> str:
    string = ('declare function local:getResultsPage($rows, $page, $size) {\n'
              '    let $offset := $page * $size let $total := count($rows)\n'
              '    return   <results total="{ $total }">    {\n'
              '               for $row in subsequence($rows, $offset + 1, $size)\n'
              '                 return $row\n'
              '               }\n'
              '             </results>\n'
              '};\n')

    return string


# return function definition for WildCard
def addClauseWild() -> str:
    string = ("declare function local:addClauseWild($var as xs:string*, $col as xs:string) as xs:string* {\n"
              "    if (empty($var) or $var = '' or normalize-space($var) = '') then ''\n"
              "    else\n"
              "        let $x := concat('[contains(',$col,',\"',$var,'\")]')\n"
              "      return $x\n"
              "};\n")

    return string


# Julina Date fucntion definition
def julianDate() -> str:
    string = ('declare function local:julianDateConversion($value as xs:string*) as xs:string*{\n'
              '    let $returnValue := ""\n'
              '    let $strVal := string-length($value)\n'
              '    let $assertSixDigitsString := if(xs:integer($strVal) = 5) then concat("0",$value) else $value\n'
              '    let $century := (19 + xs:integer(substring($assertSixDigitsString, 1, 1))) * 100\n'
              '    let $year := xs:integer($century) + xs:integer(substring($assertSixDigitsString,2,2))\n'
              '    let $numberOfDays := xs:integer(substring($assertSixDigitsString,4)) - 1\n'
              '    let $startDate := concat($year, "-01-01")\n'
              '    let $timeDuration := concat("P",$numberOfDays,"D")\n'
              '    let $returnValue := xs:string(xs:date(normalize-space(data($startDate))) + xs:dayTimeDuration($timeDuration))\n\n'
              '    return $returnValue\n'
              '};\n')

    return string


# function to create a variable in  XQuery
def createVariable(name: str, value: str) -> str:
    string = "let $" + name + " := " + value

    return string


# create "for loop" part of the query
def queryString(schema: str, tableData: dict, inputFlags: dict, joinData: dict, join: str) -> str:
    string = 'concat(\n'
    string += '\t\t\t\t'

    # generates for loop statements
    for table in tableData:
        string += '" for $' + table + ' in ' + schema + '/' + table + '/ROW'

        # attach join conditions
        stringJoin = ''
        joinTables = {}
        if table in joinData and join == 'y':
            keys = joinData[table]
            stringJoin = '[' + keys[0] + '=' + '$' + keys[1] + '/' + keys[2] + ']'
            joinTables[table] = True

        string += stringJoin + '",\n'
        string += '\t\t\t\t'

        for column in tableData[table]:
            flags = inputFlags[column]
            if flags[0] == 'y' and flags[1] == 'y' and flags[3] == 'y':
                string += 'local:addClause($' + column + '/from, ia:create-encrypted-condition(\'' + column + '\', \'>=\', $' + column + '/from)),\n'
                string += '\t\t\t\t'
                string += 'local:addClause($' + column + '/to, ia:create-encrypted-condition(\'' + column + '\', \'<=\', $' + column + '/to)),\n'
                string += '\t\t\t\t'
            elif flags[1] == 'y' and flags[3] == 'y':
                string += 'local:addClause($' + column + ', ia:create-encrypted-condition(\'' + column + '\', \'>=\', $' + column + ')),\n'
                string += '\t\t\t\t'
                string += 'local:addClause($' + column + ', ia:create-encrypted-condition(\'' + column + '\', \'<=\', $' + column + ')),\n'
                string += '\t\t\t\t'
            elif flags[0] == 'y' and flags[1] == 'y':
                string += 'local:addClause($' + column + '/from, concat("substring(' + column + ',1,10) >= \'", substring($' + column + '/from,1,10), "\'")),\n'
                string += '\t\t\t\t'
                string += 'local:addClause($' + column + '/to, concat("substring(' + column + ',1,10) <= \'", substring($' + column + '/to,1,10), "\'")),\n'
                string += '\t\t\t\t'
            elif flags[1] == 'y':
                string += 'local:addClause($' + column + ', concat("' + column + ' >= \'", $' + column + ', "\'")),\n'
                string += '\t\t\t\t'
                string += 'local:addClause($' + column + ', concat("' + column + ' <= \'", $' + column + ', "\'")),\n'
                string += '\t\t\t\t'
            elif flags[3] == 'y':
                string += 'local:addClause($' + column + ', ia:create-encrypted-condition(\'' + column + '\', \'=\', $' + column + ')),\n'
                string += '\t\t\t\t'
            elif flags[2] == 'y':
                string += 'local:addClauseWild($' + column + ', \'' + column + '\'),\n'
                string += '\t\t\t\t'
            elif flags[0] == 'y':
                string += 'local:addClause($' + column + ', concat("substring(' + column + ',1,10) = \'", substring($' + column + ',1,10), "\'")),\n'
                string += '\t\t\t\t'
            else:
                string += 'local:addClause($' + column + ', concat("' + column + ' = \'", $' + column + ', "\'")),\n'
                string += '\t\t\t\t'

    for table in joinData:
        if table not in joinTables.keys() and join == 'y':
            keys = joinData[table]
            string += '" for $' + table + ' in ' + schema + '/' + table + '/ROW'
            string += '[' + keys[0] + '=' + '$' + keys[1] + '/' + keys[2] + ']'
            string += '",\n' + '\t\t\t\t'


    string += '" return ")'

    return string


# create return part of the query
def returnString(data: dict, outputFlags: dict) -> tuple:
    primaryTable = list(data.keys())[0]
    string = ''

    decryption = False
    columnString = ''
    for table in data:
        columnString = '<row id=\'{string($' + primaryTable + '/@table:id)}\'>\n'
        columnString += '\t\t\t\t'
        for column in data[table]:
            download = list(outputFlags[column])[0]
            decrypt = list(outputFlags[column])[1]

            if decrypt == 'y':
                decryption = True
                break
            elif download == 'y':
                columnString += '<column name=\'' + column + '\'>{$' + table + '/' + column + '/@ref/string()}</column>\n'
                columnString += '\t\t\t\t'

            else:
                columnString += '<column name=\'' + column + '\'>{$' + table + '/' + column + '/string()}</column>\n'
                columnString += '\t\t\t\t'
        if decryption:
            break

    if decryption:
        decryptColumnString = '<result\n\t\t\t\t'

        for table in data:
            for column in data[table]:
                download = list(outputFlags[column])[0]

                if download == 'y':
                    decryptColumnString += column + ' = \'{$' + table + '/' + column + '/@ref/string()}\'\n'
                    decryptColumnString += '\t\t\t\t'

                else:
                    decryptColumnString += column + ' = \'{$' + table + '/' + column + '/string()}\'\n'
                    decryptColumnString += '\t\t\t\t'

        string += decryptColumnString + '/>'
    else:
        string += columnString + '</row>'

    return string, decryption


def decryptReturn(data: dict, outputFlags: dict) -> str:
    string = '(for $x in $results\n'
    string += '\t\t\t\t\t\t  ' + 'return\n'

    for table in data:
        string += '\t\t\t\t\t\t  ' + '<row id=\'{string($x/@table:id)}\'>\n'
        string += '\t\t\t\t\t\t  '
        for column in data[table]:
            download = list(outputFlags[column])[0]
            decrypt = list(outputFlags[column])[1]

            if decrypt == 'y':
                string += '<column name=\'' + column + '\'>{ia:decrypt-value($x/@' + column + '/string())}</column>\n'
                string += '\t\t\t\t\t\t  '

            else:
                string += '<column name=\'' + column + '\'>{$x/@' + column + '/string()}</column>\n'
                string += '\t\t\t\t\t\t  '

    string += '</row>)'
    return string


# Create full Query using above functions
def mainFunction(inputData: pd.DataFrame, outputData: pd.DataFrame, joinData: pd.DataFrame, metadata: dict) -> str:
    schema = inputData['Schema'].tolist()[0]
    join = joinData['Join'].tolist()[0]

    tableData = ds.inputTables(inputData)
    inputFlags = ds.inputFlags(inputData)
    joinData = ds.joinsData(joinData)
    inputColumns = inputData['Input'].tolist()

    wildCardFields = inputData['WildCard'].tolist()
    wildCard = False
    if 'y' in wildCardFields:
        wildCard = True

    encryptionFields = inputData['Encryption'].tolist()
    encryption = False
    if 'y' in encryptionFields:
        encryption = True

    decryptionFields = outputData['Decrypt'].tolist()
    decryption = False
    if 'y' in decryptionFields:
        decryption = True

    julianFields = inputData['JulianDate'].tolist()
    julian = False
    if 'y' in julianFields:
        julian = True

    outputTables = ds.outputTables(outputData)
    downloadFlags = ds.outputFlags(outputData)

    string = ''

    codeHeader = codeBrief(metadata)

    declarationSection = '(: :::::::::::::::::: Declaration and Initialization  of Variables, Namespaces :::::::::::::::::::: :)\n\n'
    declarationSection += declareNamespace() + declareVariables(inputColumns)

    if encryption:
        declarationSection += encryptFunction() + '\n'

    if decryption:
        declarationSection += decryptFunction() + '\n'

    defaultFunctions = '(: :::::::::::::::::::::::::::::::: Function definitions :::::::::::::::::::::::::::::::::::: :)\n\n'
    defaultFunctions += addClause() + '\n'

    if wildCard:
        defaultFunctions += addClauseWild() + '\n'

    if julian:
        defaultFunctions += julianDate() + '\n'

    defaultFunctions += getResultsPage()

    mainSection = '(: :::::::::::::::::::::::::::::::: Main Function definition :::::::::::::::::::::::::::::::::::: :)\n\n'
    mainSection += 'declare function local:MAIN('
    for column in inputColumns:
        mainSection += '$' + column + ', '

    mainSection += '$limit, $page, $size) {\n\n'

    mainSection += ('    let $import := \'declare namespace ia = (: :) "urn:x-emc:ia:schema:fn";\n'
                    '                    declare namespace table = (: :)  "urn:x-emc:ia:schema:table";\'')

    mainSection += '\n\n\t' + createVariable('query',
                                             queryString(schema, tableData, inputFlags, joinData, join))

    returnStr, decryption = returnString(outputTables, downloadFlags)

    mainSection += '\n\n\t' + createVariable('return',
                                             '"' + returnStr + '"')

    mainSection += '\n\n\t' + createVariable('results',
                                             'subsequence(xhive:evaluate(concat($import,$query,$return)),1,$limit)')

    results = 'results'
    if decryption:
        mainSection += '\n\n\t' + createVariable('finalResults', decryptReturn(outputTables, downloadFlags))
        results = 'finalResults'


    mainSection += (f'\n\n\treturn local:getResultsPage(${results}, $page, $size)\n'
                    '};\n\n'
                    '(: :::::::::::::::::::::::::::::::: Main Function Call :::::::::::::::::::::::::::::::::::: :)\n'
                    'local:MAIN(')

    for column in inputColumns:
        mainSection += '$' + column + ', '

    mainSection += '$limit, $page, $size)'

    string += codeHeader + declarationSection + defaultFunctions + '\n\n' + mainSection

    return string
