# Andy Castillo

from clases import AFD
from clases import Log

ANY_BUT_QUOTES = '«««««««««««««««l¦d»¦s»¦o»¦ »¦(»¦)»¦/»¦*»¦=»¦.»¦|»¦[»¦]»¦{»¦}»'

# CHARACTERS
{{CHARACTERS}}

# KEYWORDS
{{KEYWORDS}}

# TOKENS RE
{{TOKENS_RE}}


# PRODUCTIONS


TOKENS = []

# -------------------------------------------------------

class Token():
    def __init__(self, value, line, column):
        self.value = value
        self.line = line + 1
        self.column = column + 1
        self.type = Token.get_type_of(value)

    def __str__(self):
        return f'Token({self.value}, {self.type}, {self.line}, {self.column})'

    @classmethod
    def get_type_of(cls, word):
        if word in KEYWORDS.values():
            return 'KEYWORD'
        else:
            for token_type, re in TOKENS_RE.items():
                if AFD(re.replace('a', ANY_BUT_QUOTES)).accepts(word, CHARACTERS):
                    return token_type
        return 'ERROR'

# -------------------------------------------------------

def line_eval(entry_file_lines, line, line_index):
    analyzed_lines = 1
    line_position = 0
    current_line_recognized_tokens = []
    while line_position < len(line):
        current_token = None
        next_token = None
        avance = 0
        continuar = True
        while continuar:
            if current_token and next_token:
                if current_token.type != 'ERROR' and next_token.type == 'ERROR':
                    avance -= 1
                    continuar = False
                    break

            if line_position + avance > len(line):
                continuar = False
                break

            if line_position + avance <= len(line):
                current_token = Token(line[line_position:line_position + avance], line_index, line_position)

            avance += 1

            if line_position + avance <= len(line):
                next_token = Token(line[line_position:line_position + avance], line_index, line_position)

            # Log.WARNING(current_token)

        line_position = line_position + avance


        if current_token and current_token.type != 'ERROR':
            # Log.INFO(current_token)
            TOKENS.append(current_token)
            current_line_recognized_tokens.append(current_token)
        else:
            # Log.FAIL(current_token)

            if line_position == len(line) + 1 and len(current_line_recognized_tokens) != 0:
                TOKENS.append(current_token)

            # Si se llega al final de la linea y no se reconoce ningun token,
            # se agrega la siguiente linea y se vuelve a intentar.
            if line_position == len(line) + 1 and len(current_line_recognized_tokens) == 0:
                if line_index < len(entry_file_lines) - 1:
                    new_line = line + ' ' + entry_file_lines[line_index + 1].replace('\n', '\\n')
                    line_index += 1
                    Log.INFO('Trying: ', new_line)
                    analyzed_lines += line_eval(entry_file_lines, new_line, line_index)

    return analyzed_lines

# -------------------------------------------------------

def run():
    try:
        archivo = input("Ingrese el nombre del archivo de entrada: ")
        entry_file = open(archivo, 'r')
    except IOError:
        print('No se encontro el archivo')
        exit()

    entry_file_lines = entry_file.readlines()
    entry_file.close()

    # -------------------------------------------------------
    # GET TOKENS
    # -------------------------------------------------------
    line_index = 0
    while line_index < len(entry_file_lines):
        line = entry_file_lines[line_index].replace('\n', '\\n')
        analyzed_lines = line_eval(entry_file_lines, line, line_index)
        line_index += analyzed_lines

    # Log.OKGREEN('\n\nTokens:')
    # for token in TOKENS:
    #     if token.type == 'ERROR':
    #         Log.WARNING(token)
    #     else:
    #         Log.INFO(token)

    # -------------------------------------------------------
    # GET TOKENS
    # -------------------------------------------------------
    lexical_errors = False
    # Log.FAIL('\n\nErrores:')
    for token in TOKENS:
        if token.type == 'ERROR':
            Log.FAIL(f'Error en la linea {token.line} columna {token.column}: {token.value}')
            lexical_errors = True

    if lexical_errors:
        Log.FAIL('\nErrores en el archivo')

    # -------------------------------------------------------
    # WRITE TOKEN FLOW FILE
    # -------------------------------------------------------
    try:
        tokens_flow_file = open('flujo-tokens', 'w+')
        cont = 0
        for token in TOKENS:
            if token.type == 'KEYWORD':
                if token.value == '\\n':
                    tokens_flow_file.write('\n')
                else:
                    tokens_flow_file.write(f'{token.value}')
            elif token.type == 'space':
                # tokens_flow_file.write(f'{token.value}')
                continue
            else:
                if token.type == 'numeroDecimal':
                    TOKENS.pop(cont +1)
                tokens_flow_file.write(f'{token.type}')
            tokens_flow_file.write(' ')
            cont +=1

        Log.OKGREEN('\nFlujo de tokens generado')
    except:
        Log.FAIL('\nError en la generacion del flujo de tokens')
        exit()
    finally:
        tokens_flow_file.close()



try:
    run()
except Exception as e:
    # Log.FAIL('Error: ', e)
    print(e)
