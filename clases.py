#Andy Castillo

import graphviz
import re as regex
# from retree import RETree


class Estado:
    def __init__(self, val, anul, prima_pos, ult_pos, next_pos):
        self.val = val
        self.anul = anul
        self.prima_pos = prima_pos
        self.ult_pos = ult_pos
        self.next_pos = next_pos


class AFD:
    def __init__(self, re, draw=False, print_tree=False):
        self.data = {}
        self.tree = None
        self.alfabeto = []
        self.transiciones = {}
        self.print_tree = print_tree
        self.construct_tree(re)
        self.init_estados()
        self.get_transiciones()

        if draw:
            self.draw()

    def construct_tree(self, re):
        re = '«' + re + '»#'
        retree = RETree(re)
        self.tree = retree.get_tree()
        if self.print_tree:
            print(self.tree)

    def init_estados(self):
        cont = 1

        # Se inicializa el diccionario de estados
        for i in self.tree.postorder:
            self.data[str(cont)] = Estado(chr(i.value), None, None, None, [])
            i.value = cont
            cont += 1

        # Extraigo letras de la expresion
        for hoja in self.tree.leaves:
            if regex.match(r'[a-zA-Z"\'/*=.|()[\]{} ]', self.data[str(hoja.value)].val) and self.data[str(hoja.value)].val not in self.alfabeto:
                self.alfabeto.append(self.data[str(hoja.value)].val)

        self.alfabeto.sort()

        for node in self.tree.postorder:
            self.anul(node)
            self.prima_y_ult(node)
            self.next_pos(node)

    def accepts(self, word, characters):
        return self.simulacion(word, characters)

    def simulacion(self, word, characters):
        for char in word:
            belongs_to = False
            for key in self.alfabeto:
                if characters.get(key):
                    if char in characters[key]:
                        belongs_to = True
                        break
                else:
                    return False
            if not belongs_to:
                return False

        current_state = 'S0'

        for char in word:
            llave = ''
            alfabeto_key = None

            for key in self.alfabeto:
                if char in characters[key]:
                    alfabeto_key = key

            for key, value in self.transiciones.items():
                if value['name'] == current_state and value[alfabeto_key] is not None:
                    llave = key
                elif value['name'] == current_state and value[alfabeto_key] is None:
                    return False

            current_state = self.transiciones[llave][alfabeto_key]

        for key, value in self.transiciones.items():
            if value['name'] == current_state:
                states = key
                for specialChar in ['[', ']', ' ']:
                    states = states.replace(specialChar, '')
                states = states.split(',')

                return True if str(self.tree.right.value) in states else False

    def get_transiciones(self):
        # Se genera la tabla de transiciones
        cont = 0

        # El primer valor de la tabla son las primeras posiciones de la raiz del arbol
        self.transiciones[str(self.data[str(self.tree.value)].prima_pos)] = {
            'name': 'S' + str(cont),
        }

        for letra in self.alfabeto:
            self.transiciones[str(self.data[str(self.tree.value)].prima_pos)][letra] = None

        cont += 1
        continuar = True
        while (continuar):
            initial_size = len(self.transiciones)
            keys = list(self.transiciones.keys())

            for key in keys:
                for letra in self.alfabeto:
                    if self.transiciones[key][letra] is None:
                        new_state = []
                        state = key

                        for specialChar in ['[', ']', ' ']:
                            state = state.replace(specialChar, '')
                        state = state.split(',')

                        for i in state:
                            if self.data[str(i)].val == letra: new_state.append(self.data[str(i)].next_pos)

                        new_state = [item for sublist in new_state for item in sublist]
                        new_state = list(set(new_state))
                        new_state.sort()

                        if len(new_state) > 0:
                            if str(new_state) not in self.transiciones:
                                self.transiciones[str(new_state)] = {
                                    'name': 'S' + str(cont)
                                }

                                for letter in self.alfabeto:
                                    self.transiciones[str(new_state)][letter] = None

                                cont += 1
                                self.transiciones[key][letra] = self.transiciones[str(new_state)]['name']
                            else:
                                self.transiciones[key][letra] = self.transiciones[str(new_state)]['name']

            final_size = len(self.transiciones)

            if initial_size == final_size:
                continuar = not all(self.transiciones.values())

    def anul(self, node):
        # Es anul si te puede devolver Epsilon (~)
        if self.data[str(node.value)].val == '¦' and node.left and node.right:
            self.data[str(node.value)].anul = self.data[str(node.left.value)].anul or self.data[str(node.right.value)].anul
        elif self.data[str(node.value)].val == '.' and node.left and node.right:
            self.data[str(node.value)].anul = self.data[str(node.left.value)].anul and self.data[str(node.right.value)].anul
        elif self.data[str(node.value)].val in ['±', '?', '~']:
            self.data[str(node.value)].anul = True
        else:
            self.data[str(node.value)].anul = False

    def prima_y_ult(self, node):
        if self.data[str(node.value)].val in ['¦', '?'] and node.left and node.right:
            # Se obtienen todas las primeras posiciones de ambos hijos
            self.data[str(node.value)].prima_pos = [item for sublist in [self.data[str(node.left.value)].prima_pos, self.data[str(node.right.value)].prima_pos] for item in sublist]
            self.data[str(node.value)].ult_pos = [item for sublist in [self.data[str(node.left.value)].ult_pos, self.data[str(node.right.value)].ult_pos] for item in sublist]
        elif self.data[str(node.value)].val == '.' and node.left and node.right:
            if self.data[str(node.left.value)].anul:
                # Si el hijo izquierdo es anul, se obtiene la primera posición de sus hijos
                self.data[str(node.value)].prima_pos = [item for sublist in [self.data[str(node.left.value)].prima_pos, self.data[str(node.right.value)].prima_pos] for item in sublist]
            else:
                # Si el hijo izquierdo no es anul, se obtiene la primera posición del hijo izquierdo
                self.data[str(node.value)].prima_pos = [item for sublist in [self.data[str(node.left.value)].prima_pos] for item in sublist]

            if self.data[str(node.right.value)].anul:
                self.data[str(node.value)].ult_pos = [item for sublist in [self.data[str(node.left.value)].ult_pos, self.data[str(node.right.value)].ult_pos] for item in sublist]
            else:
                self.data[str(node.value)].ult_pos = [item for sublist in [self.data[str(node.right.value)].ult_pos] for item in sublist]
        elif self.data[str(node.value)].val in ['±', '+']:
            # Se obtiene la primera posición de su hijo
            self.data[str(node.value)].prima_pos = [item for sublist in [self.data[str(node.left.value)].prima_pos] for item in sublist]
            self.data[str(node.value)].ult_pos = [item for sublist in [self.data[str(node.left.value)].ult_pos] for item in sublist]
        elif self.data[str(node.value)].val == '~':
            self.data[str(node.value)].prima_pos = []
            self.data[str(node.value)].ult_pos = []
        else:
            self.data[str(node.value)].prima_pos = [node.value]
            self.data[str(node.value)].ult_pos = [node.value]

    def next_pos(self, node):
        # Para cada una de las ultimas posiciones se agregan las ultimas posiciones de sus hijos de la derecha
        if self.data[str(node.value)].val == '.' and node.left and node.right:
            for ult_pos in self.data[str(node.left.value)].ult_pos:
                for prim_pos in self.data[str(node.right.value)].prima_pos:
                    if prim_pos not in self.data[str(node.left.value)].next_pos:
                        self.data[str(ult_pos)].next_pos.append(prim_pos)

        # Para cada ultima posicion de su hijo se agregan las ultimas posiciones de sus hijos de la derecha
        elif self.data[str(node.value)].val == '±':
            for ult_pos in self.data[str(node.left.value)].ult_pos:
                for prim_pos in self.data[str(node.left.value)].prima_pos:
                    if prim_pos not in self.data[str(node.left.value)].next_pos:
                        self.data[str(ult_pos)].next_pos.append(prim_pos)

    def draw(self):
        canvas = graphviz.Digraph(comment='AFD')
        canvas.attr(rankdir='LR')

        for key in self.transiciones.keys():
            states = key
            for specialChar in ['[', ']', ' ']:
                states = states.replace(specialChar, '')
            states = states.split(',')

            if str(self.tree.right.value) in states:
                canvas.node(self.transiciones[key]['name'], self.transiciones[key]['name'], shape='doublecircle')
            else:
                canvas.node(self.transiciones[key]['name'], self.transiciones[key]['name'])

        for key, value in self.transiciones.items():
            for c in self.alfabeto:
                if value['name'] is not None and value[c] is not None:
                    canvas.edge(value['name'], value[c], c)

        canvas.view()

import re as regex
from binarytree import Node as BinaryTreeNode

class Node:
    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

    @staticmethod
    def convert_to_binary_tree(parent_node, binary_tree_parent=None):
        if binary_tree_parent is None:
            binary_tree_parent = BinaryTreeNode(ord(parent_node.data))

        if parent_node.left is not None and parent_node.left.data is not None:
            binary_tree_parent.left = BinaryTreeNode(ord(parent_node.left.data))
            Node.convert_to_binary_tree(parent_node.left, binary_tree_parent.left)

        if parent_node.right is not None and parent_node.right.data is not None:
            binary_tree_parent.right = BinaryTreeNode(ord(parent_node.right.data))
            Node.convert_to_binary_tree(parent_node.right, binary_tree_parent.right)

        return binary_tree_parent


class RETree:
    def __init__(self, initial_regular_expression):
        self.current_node_head = None
        self.temp_roots = []
        self.get_nodes(initial_regular_expression, None)

    def get_tree(self):
        return Node.convert_to_binary_tree(self.current_node_head)

    def add_node(self, temp_root_index, content, left, right, use_head_for):
        if temp_root_index is None:
            self.current_node_head = Node(content, left, right) if self.current_node_head is None else (Node(content, self.current_node_head, right) if use_head_for == 'l' else Node(content, left, self.current_node_head))
        else:
            if temp_root_index == len(self.temp_roots):
                self.temp_roots.append(Node(content, left, right))
            elif temp_root_index < len(self.temp_roots):
                self.temp_roots[temp_root_index] = Node(content, left, right) if self.temp_roots[temp_root_index] is None else (Node(content, self.temp_roots[temp_root_index], right) if use_head_for == 'l' else Node(content, left, self.temp_roots[temp_root_index]))

    @staticmethod
    def get_final_of_expression(partial_expression):
        i = 0
        while i < len(partial_expression):
            if partial_expression[i] == '«':
                parentheses_counter = 1
                for j in range(i+1, len(partial_expression)):
                    if partial_expression[j] in ['«', '»']: parentheses_counter = parentheses_counter + 1 if partial_expression[j] == '«' else parentheses_counter - 1

                    if parentheses_counter == 0 and partial_expression[j] == '»':
                        extra = 2 if j + 1 < len(partial_expression) and partial_expression[j+1] in ['±', '+', '?'] else 0
                        fin = j + extra
                        return fin

            elif regex.match(r'[a-zA-Z±"\'/*=.|()[\]{} ]', partial_expression[i]):
                fin = i
                for j in range(i + 1, len(partial_expression)):
                    if not regex.match(r'[a-zA-Z±"\'/*=.|()[\]{} ]', partial_expression[j]): break
                    fin = j
                return fin
            i += 1


    def get_nodes(self, partial_expression, temp_root_index):
        # print('Partial expression:', temp_root_index, partial_expression)

        i = 0
        while i < len(partial_expression):
            if partial_expression[i] == '«':
                if i == 0:
                    parentheses_counter = 1
                    for j in range(i+1, len(partial_expression)):
                        if partial_expression[j] in ['«', '»']: parentheses_counter = parentheses_counter + 1 if partial_expression[j] == '«' else parentheses_counter - 1

                        if parentheses_counter == 0:
                            extra = 2 if partial_expression[j] == '»' and j + 1 < len(partial_expression) and partial_expression[j+1] in ['±', '+', '?'] else 0
                            fin = j + extra
                            self.get_nodes(partial_expression[i+1:fin], temp_root_index)
                            i = j
                            break
                else:
                    if partial_expression[i-1] in ['»', '±', '+', '?'] or regex.match(r'[a-zA-Z"\'/*=.|()[\]{} ]', partial_expression[i-1]):
                        fin_sub_re = self.get_final_of_expression(partial_expression[i:])
                        fin = i + 1 + fin_sub_re
                        self.get_nodes(partial_expression[i:fin], len(self.temp_roots))

                        sub_tree_root = self.temp_roots.pop() if temp_root_index is None else self.temp_roots.pop(temp_root_index + 1)
                        if sub_tree_root is not None: self.add_node(temp_root_index, '.', None, sub_tree_root, 'l')
                        i = i + fin + 1

            elif regex.match(r'[a-zA-Z#"\'/*=.|()[\]{} ]', partial_expression[i]):
                if ((temp_root_index is None and self.current_node_head is None) or i == 0) and i + 1 < len(partial_expression) and regex.match(r'[a-zA-Z#"\'/*=.|()[\]{} ]', partial_expression[i+1]):
                    if i + 2 < len(partial_expression) and partial_expression[i+2] in ['±', '+', '?']:
                        self.add_node(temp_root_index, '.', Node(partial_expression[i]), Node(partial_expression[i+2], Node(partial_expression[i+1]), None), 'l')
                        i += 2
                    else:
                        self.add_node(temp_root_index, '.', Node(partial_expression[i]), Node(partial_expression[i+1]), 'l')
                        i += 1
                elif (temp_root_index is None and self.current_node_head is not None) or i != 0:
                    self.add_node(temp_root_index, '.', None, Node(partial_expression[i]), 'l')
                else:
                    self.add_node(temp_root_index, partial_expression[i], None, None, 'l')

                if i + 1 < len(partial_expression):
                    if partial_expression[i+1] in ['±', '+', '?']:
                        self.add_node(temp_root_index, partial_expression[i+1], Node(partial_expression[i]), None, 'l')
                    elif partial_expression[i+1] == '»':
                        if i + 2 < len(partial_expression) and partial_expression[i+2] in ['±', '+', '?']:
                            self.add_node(temp_root_index, partial_expression[i+2], Node(partial_expression[i]), None, 'l')

            elif partial_expression[i] in ['¦']:
                fin_sub_re = self.get_final_of_expression(partial_expression[i+1:])
                fin = i + 1 + fin_sub_re + 1
                self.get_nodes(partial_expression[i+1:fin], len(self.temp_roots))

                sub_tree_root = self.temp_roots.pop() if temp_root_index is None else self.temp_roots.pop(temp_root_index + 1)
                if sub_tree_root is not None: self.add_node(temp_root_index, partial_expression[i], Node(partial_expression[i-1]), sub_tree_root, 'l')

                if fin < len(partial_expression) and partial_expression[fin] == '»':
                    if fin + 1 < len(partial_expression) and partial_expression[fin+1] in ['±', '+', '?']:
                        self.add_node(temp_root_index, partial_expression[fin+1], Node(partial_expression[fin+1]), None, 'l')

                i = i + fin + 1
            else:
                pass
                # print('-', partial_expression[i])
            i += 1

class Log:
    _BLUE = '\033[94m'
    _CYAN = '\033[96m'
    _GREEN = '\033[92m'
    _YELLOW = '\033[93m'
    _RED = '\033[91m'
    _BOLD = '\033[1m'
    _UNDERLINE = '\033[4m'
    _END = '\033[0m'

    def OKBLUE(*attr):
        print(Log._BLUE, *attr, Log._END)

    def OKGREEN(*attr):
        print(Log._GREEN, *attr, Log._END)

    def INFO(*attr):
        print(Log._CYAN, *attr, Log._END)

    def WARNING(*attr):
        print(Log._YELLOW, *attr, Log._END)

    def FAIL(*attr):
        print(Log._RED, *attr, Log._END)

    def N(*attr):
        print(*attr)

    def BOLD(*attr):
        print(Log._BOLD, *attr, Log._END)

    def UNDERLINE(*attr):
        print(Log._UNDERLINE, *attr, Log._END)


import os
# from log import Log
# from compiler_def import CompilerDef

class LexGenerator:
    def __init__(self):
        self.compiler_def = None
        self.FILE_LINES = []
        self.extract_compiler_def()
        self.lex_analyzer_construction()
        self.run_lex_analyzer()

    def add_header(self):
        self.FILE_LINES.append('# Andy Castillo')
    def add_enter(self):
        self.FILE_LINES.append('')

    def add_line(self, line):
        self.FILE_LINES.append(line)

    def extract_compiler_def(self):
        # -------------------------------------------------------
        # Extracting content from compiler definition file
        # -------------------------------------------------------

        try:
            archivo = input('Escriba el nombre del archivo de COCOL: ')
            entry_file = open(archivo, 'r')
        except IOError:
            Log.FAIL('\nArchivo no encontrado')
            exit()

        Log.N('\nAnalizando el contenido del archivo...')

        entry_file_lines = entry_file.readlines()
        entry_file.close()

        self.compiler_def = CompilerDef(entry_file_lines)

        Log.OKGREEN('\nContenido analizado!\n')

    def lex_analyzer_construction(self):
        # -------------------------------------------------------
        # Writing the lexical analyzer file
        # -------------------------------------------------------
        try:
            os.system('cp analizador.template.py analizador.py')

            characters_to_replace = ''
            characters_to_replace += 'CHARACTERS = {\n'
            for key, value in self.compiler_def.CHARACTERS.items():
                characters_to_replace += f"    '{key}': '{value}',\n"
            characters_to_replace += '}'

            keywords_to_replace = ''
            keywords_to_replace += 'KEYWORDS = {\n'
            for key, value in self.compiler_def.KEYWORDS.items():
                keywords_to_replace += f"    '{key}': '{value}',\n"
            keywords_to_replace += '}'

            tokens_re_to_replace = ''
            tokens_re_to_replace += 'TOKENS_RE = {\n'
            for key, value in self.compiler_def.TOKENS_RE.items():
                tokens_re_to_replace += f"    '{key}': '{value}',\n"
            tokens_re_to_replace += '}'

            with open('analizador.py', 'r') as file:
                data = file.read().replace('{{COMPILER_NAME}}', self.compiler_def.COMPILER_NAME)
                data = data.replace('{{CHARACTERS}}', characters_to_replace)
                data = data.replace('{{KEYWORDS}}', keywords_to_replace)
                data = data.replace('{{TOKENS_RE}}', tokens_re_to_replace)

            with open('analizador.py', 'w') as file:
                file.write(data)

            Log.OKGREEN('\nAnalizador lexico generado.\n')
        except:
            Log.FAIL('\nError al generar analizador.\n')
            exit()

    def run_lex_analyzer(self):
        try:
            Log.N('\n\n\n\n\n# -------------------------------------------------------')
            Log.N('\nCorriendo analizador lexico')
            os.system('python3 analizador.py')
        except:
            Log.FAIL('\nError al correr analizador.')
            exit()


# from afd import AFD
# from log import Log

ANY_BUT_QUOTES = '«««««««««««««««l¦d»¦s»¦o»¦ »¦(»¦)»¦/»¦*»¦=»¦.»¦|»¦[»¦]»¦{»¦}»'

# CHARACTERS
CHARACTERS = {
    ' ': ' ',
    '"': '"',
    '\'': '\'',
    '/': '/',
    '*': '*',
    '=': '=',
    '.': '.',
    '|': '|',
    '(': '(',
    ')': ')',
    '[': '[',
    ']': ']',
    '{': '{',
    '}': '}',
    'o': '+-',
    's': '@~!#$%^&_;:,<>?',
    'l': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'd': '0123456789',
}

# KEYWORDS
KEYWORDS = {
    'COMPILER': 'COMPILER',
    'CHARACTERS': 'CHARACTERS',
    'KEYWORDS': 'KEYWORDS',
    'TOKENS': 'TOKENS',
    'PRODUCTIONS': 'PRODUCTIONS',
    'END': 'END',
    'EXCEPT': 'EXCEPT',
    'ANY': 'ANY',
    'CONTEXT': 'CONTEXT',
    'IGNORE': 'IGNORE',
    'PRAGMAS': 'PRAGMAS',
    'IGNORECASE': 'IGNORECASE',
    'WEAK': 'WEAK',
    'COMMENTS': 'COMMENTS',
    'FROM': 'FROM',
    'NESTED': 'NESTED',
    'SYNC': 'SYNC',
    'IF': 'IF',
    'out': 'out',
    'TO': 'TO',
    'NEWLINE': '\\n',
}

# TOKENS RE
TOKENS_RE = {
    'semantic_action': '«(.««a¦"»¦\'»±.»)',
    'comment_block': '«/*««a¦"»¦\'»±*»/',
    'comment': '//««««l¦d»¦s»¦o»¦ »±',
    'char': '«\'«a¦"»±»\'',
    'string': '"«a¦\'»±"',
    'number': 'd«d»±',
    'ident': 'l«l¦d»±',
    'operator': 'o',
    'iteration': '{¦}',
    'option': '[¦]',
    'group': '(¦)',
    'or': '|',
    'final': '.',
    'assign': '=',
    'space': ' ',
}

# PRODUCTIONS
PRODUCTIONS = {
    'program': [
        {
            'type': 'KEYWORD',
            'value': 'COMPILER',
        }, {
            'type': 'ident',
        }, {
            'type': 'PRODUCTION',
            'value': 'ScannerSpecification',
        }, {
            'type': 'PRODUCTION',
            'value': 'ParserSpecification',
        }, {
            'type': 'KEYWORD',
            'value': 'END',
        }, {
            'type': 'ident',
        }, {
            'type': 'final',
        }
    ],
    'ScannerSpecification': [
        {
            'type': 'PRODUCTION',
            'value': 'CHARACTERS_SET',
            'optional': True,
        }, {
            'type': 'PRODUCTION',
            'value': 'KEYWORDS_SET',
            'optional': True,
        }, {
            'type': 'PRODUCTION',
            'value': 'TOKENS_SET',
            'optional': True,
        }
    ],
    'CHARACTERS_SET': [
        {
            'type': 'KEYWORD',
            'value': 'CHARACTERS',
            'optional': True,
        }, {
            'type': 'PRODUCTION',
            'value': 'SetDecl',
            'ocurrences': '+',
        }
    ],
    'KEYWORDS_SET': [
        {
            'type': 'KEYWORD',
            'value': 'KEYWORDS',
        }, {
            'type': 'PRODUCTION',
            'value': 'KeywordDecl',
            'ocurrences': '+',
        }
    ],
    'TOKENS_SET': [
        {
            'type': 'KEYWORD',
            'value': 'TOKENS',
        }, {
            'type': 'PRODUCTION',
            'value': 'TokenDecl',
            'ocurrences': '+',
        }
    ],
    'SetDecl': [
        {
            'type': 'ident',
        }, {
            'type': 'assign',
        }, {
            'type': 'PRODUCTION',
            'value': 'Set',
        }, {
            'type': 'final',
        }
    ],
    'Set': [
        {
            'type': 'PRODUCTION',
            'value': 'BasicSet',
        }, {
            'type': 'PRODUCTION',
            'value': 'BasicSetConvination',
            'ocurrences': '+',
        }
    ],
    'BasicSet': [
        {
            'type': 'OPTIONS',
            'options': [
                {
                    'type': 'PRODUCTION',
                    'value': 'CharCalculation',
                }, {
                    'type': 'char',
                }, {
                    'type': 'string',
                }, {
                    'type': 'ident',
                }
            ]
        }
    ],
    'BasicSetConvination': [
        {
            'type': 'operator',
        }, {
            'type': 'PRODUCTION',
            'value': 'BasicSet',
        }
    ],
    'CharCalculation': [
        {
            'type': 'ident',
            'match': 'CHR',
        }, {
            'type': 'group',
        }, {
            'type': 'number',
        }, {
            'type': 'group',
        }
    ],
    'KeywordDecl': [
        {
            'type': 'ident',
        }, {
            'type': 'assign',
        }, {
            'type': 'string',
        }, {
            'type': 'final',
        }
    ],
    'TokenDecl': [
        {
            'type': 'ident',
        }, {
            'type': 'PRODUCTION',
            'value': 'AssignTokenExpr',
            'optional': True,
        }, {
            'type': 'string',
            'match': 'EXCEPT',
            'optional': True,
        }, {
            'type': 'string',
            'match': 'KEYWORDS',
            'optional': True,
        }, {
            'type': 'final',
        }
    ],
    'AssignTokenExpr': [
        {
            'type': 'assign',
        }, {
            'type': 'PRODUCTION',
            'value': 'TokenExpr',
        }
    ],
    'TokenExpr': [
        {
            'type': 'PRODUCTION',
            'value': 'TokenTerm',
        }, {
            'type': 'PRODUCTION',
            'value': 'TokenExprConvination',
            'ocurrences': '+',
        }
    ],
    'TokenExprConvination': [
        {
            'type': 'or',
        }, {
            'type': 'PRODUCTION',
            'value': 'TokenTerm',
        }
    ],
    'TokenTerm': [
        {
            'type': 'PRODUCTION',
            'value': 'TokenFactor',
        }, {
            'type': 'PRODUCTION',
            'value': 'TokenFactor',
            'ocurrences': '+',
        }
    ],
    'TokenFactor': [
        {
            'type': 'OPTIONS',
            'options': [
                {
                    'type': 'PRODUCTION',
                    'value': 'TokenExprGroup',
                }, {
                    'type': 'PRODUCTION',
                    'value': 'TokenExprOption',
                }, {
                    'type': 'PRODUCTION',
                    'value': 'TokenExprIteration',
                }, {
                    'type': 'PRODUCTION',
                    'value': 'Symbol',
                }
            ]
        }
    ],
    'Symbol': [
        {
            'type': 'OPTIONS',
            'options': [
                {
                    'type': 'ident',
                }, {
                    'type': 'string',
                }, {
                    'type': 'char',
                }
            ]
        }
    ],
    'TokenExprGroup': [
        {
            'type': 'group',
        }, {
            'type': 'PRODUCTION',
            'value': 'TokenExpr',
        }, {
            'type': 'group',
        }
    ],
    'TokenExprOption': [
        {
            'type': 'option',
        }, {
            'type': 'PRODUCTION',
            'value': 'TokenExpr',
        }, {
            'type': 'option',
        }
    ],
    'TokenExprIteration': [
        {
            'type': 'iteration',
        }, {
            'type': 'PRODUCTION',
            'value': 'TokenExpr',
        }, {
            'type': 'iteration',
        }
    ],
    'ParserSpecification': [
        {
            'type': 'PRODUCTION',
            'value': 'PRODUCTIONS_SET',
            'optional': True,
        },
    ],
    'PRODUCTIONS_SET': [
        {
            'type': 'KEYWORD',
            'value': 'PRODUCTIONS',
        # }, {
        #     'type': 'PRODUCTION',
        #     'value': 'ProdDecl',
        #     'ocurrences': '+',
        }
    ],
}
# ParserSpecification = "PRODUCTIONS" {Production}.
# Production = ident [Attributes] [SemAction] '=' Expression '.'.
# Expression = Term{'|'Term}.
# Term = Factor {Factor}
# Factor = Symbol [Attributes] | '(' Expression ')' | '[' Expression ']' | '{' Expression '}' | SemAction.
# Attributes = "<." {ANY} ".>"
# SemAction = "(." {ANY} ".)"

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


class CompilerDef():
    def __init__(self, file_lines):
        self.file_lines = file_lines
        self.lexical_errors = False
        self.sintax_errors = False
        self.tokens = []
        self.tokens_clean = []
        self.COMPILER_NAME = ''
        self.CHARACTERS = {}
        self.KEYWORDS = {}
        self.TOKENS_RE = {}
        self.PRODUCTIONS = {}
        self.symbols = {}
        self.current_token_index = 0

        self.get_tokens()
        self.has_lexical_errors()

        self.clean_tokens()
        # self.check_sintax()
        # self.has_sintax_errors()

        self.get_definitions()
        self.has_sintax_errors()

    def get_tokens(self):
        # Gramatica Regular
        # Se extraen los tokens por linea
        line_index = 0
        while line_index < len(self.file_lines):
            line = self.file_lines[line_index].replace('\n', '\\n')
            analyzed_lines = self.eval_line(line, line_index)
            line_index += analyzed_lines

        # Log.OKGREEN('\n\nTokens found:')
        # for token in self.tokens:
        #     if token.type == 'ERROR':
        #         Log.WARNING(token)
        #     else:
        #         Log.INFO(token)

    def eval_line(self, line, line_index):
        # Se extraen los tokens por linea
        analyzed_lines = 1
        line_position = 0
        current_line_recognized_tokens = []
        while line_position < len(line):
            current_token = None
            next_token = None
            avance = 0
            continuar = True

            while continuar: # Ciclo del centinela

                # Se evalua si el siguiente posible token es valido
                # Si no es valido, se acepta current_token como el ultimo token valido
                if current_token and next_token:
                    if current_token.type != 'ERROR' and next_token.type == 'ERROR':
                        avance -= 1 # Se retrocede una posicion
                        # Se termina el ciclo
                        continuar = False
                        break

                # Se termina el ciclo si se llega al final de la linea
                if line_position + avance > len(line):
                    continuar = False
                    break

                # Se evalua el token actual
                if line_position + avance <= len(line):
                    current_token = Token(line[line_position:line_position + avance], line_index, line_position)

                avance += 1

                # Se evalua el siguiente token si no se llego al final de la linea
                if line_position + avance <= len(line):
                    next_token = Token(line[line_position:line_position + avance], line_index, line_position)

                # Log.WARNING(current_token)

            # Se actualiza la posicion en la linea
            line_position = line_position + avance


            if current_token and current_token.type != 'ERROR':
                # Si el token es valido se guarda en los tokens reconocidos de la linea actual
                # Log.INFO(current_token)
                self.tokens.append(current_token)
                current_line_recognized_tokens.append(current_token)
            else:
                # Log.FAIL(current_token)

                # Si se llega al final de la linea y no se reonocio ningun token valido en la linea,
                # se guarda un token de tipo error
                if line_position == len(line) + 1 and len(current_line_recognized_tokens) != 0:
                    self.tokens.append(current_token)

                # Si se llega al final de la linea y no se reconoce ningun token,
                # se agrega la siguiente linea y se vuelve a intentar.
                if line_position == len(line) + 1 and len(current_line_recognized_tokens) == 0:
                    if line_index < len(self.file_lines) - 1:
                        new_line = line.replace('\\n', ' ') + ' ' + self.file_lines[line_index + 1].replace('\n', '\\n')
                        line_index += 1
                        Log.INFO('Trying: ', new_line)
                        analyzed_lines += self.eval_line(new_line, line_index)

        return analyzed_lines

    def has_lexical_errors(self):
        # Log.OKBLUE('\n\nErrores:')
        for token in self.tokens:
            if token.type == 'ERROR':
                Log.WARNING(f'Error en la linea {token.line} columna {token.column}: {token.value}')
                self.lexical_errors = True

        if self.lexical_errors:
            Log.FAIL('\tErrores en el archivo COCOL')
            Log.WARNING('\nPlease fix errors before continuing')
            exit()

    def clean_tokens(self):
        # for token in self.tokens:
        token_index = 0
        while token_index < len(self.tokens):
            token = self.tokens[token_index]
            token_index += 1
            if token.type == 'space' or token.type == 'comment' or token.type == 'comment_block':
                continue
            elif token.type == 'KEYWORD' and token.value == '\\n':
                continue
            if token.value == 'EXCEPT':
                token_index += 2
                continue
            else:
                self.tokens_clean.append(token)

    def get_definitions(self):
        # Gramaticas libres de contexto - Analisis Sintactico
        # Adding Mandatory Tokens
        self.CHARACTERS = {}

        self.KEYWORDS = {
            'NEWLINE': '\\\\n',
        }

        self.TOKENS_RE = {}

        # --------------------------------------------------

        token_index = 0
        while token_index < len(self.tokens_clean):
            token = self.tokens_clean[token_index]
            if token.type == 'KEYWORD':
                if token.value == 'COMPILER':
                    # Get Compiler Name
                    self.COMPILER_NAME = self.tokens_clean[token_index + 1].value
                elif token.value == 'END':
                    # Validate Compiler Name
                    if self.COMPILER_NAME != self.tokens_clean[token_index + 1].value:
                        self.sintax_errors = True
                elif token.value == 'CHARACTERS':
                    # Get Characters
                    count = 0
                    character_definition_tokens = []
                    character_section_definitions = []
                    while True:
                        # Iterate until end of characters section tokens
                        temp_token = self.tokens_clean[token_index + count + 1]

                        if temp_token.type == 'final':
                            # If final token is reached, means that the characters definition is finished
                            character_section_definitions.append(character_definition_tokens)
                            character_definition_tokens = []
                        else:
                            character_definition_tokens.append(temp_token)
                        count += 1

                        if temp_token.value in ['KEYWORDS', 'TOKENS', 'PRODUCTIONS', 'END']:
                            token_index -= count
                            break
                    token_index += count

                    for definition_tokens in character_section_definitions:
                        value = ''
                        for token in definition_tokens[2::]:
                            if token.type == 'ident':
                                if token.value == 'CHR':
                                    value += chr(int(definition_tokens[definition_tokens.index(token) + 2].value))
                                else:
                                    value += self.CHARACTERS[token.value]
                            elif token.type == 'string':
                                value += token.value.replace('"', '')

                        self.CHARACTERS[definition_tokens[0].value] = value

                elif token.value == 'KEYWORDS' and self.tokens_clean[token_index + 1].type != 'final':
                    count = 0
                    keyword_definition_tokens = []
                    keyword_section_definitions = []
                    while True:
                        temp_token = self.tokens_clean[token_index + count + 1]

                        if temp_token.type == 'final':
                            keyword_section_definitions.append(keyword_definition_tokens)
                            keyword_definition_tokens = []
                        else:
                            keyword_definition_tokens.append(temp_token)
                        count += 1

                        if temp_token.value in ['KEYWORDS', 'TOKENS', 'PRODUCTIONS', 'END']:
                            token_index -= count
                            break
                    token_index += count

                    for definition_tokens in keyword_section_definitions:
                        value = ''
                        for token in definition_tokens[2::]:
                            # if token.type == 'ident':
                            #     value += self.KEYWORDS[token.value]
                            if token.type == 'string':
                                value += token.value.replace('"', '')

                        self.KEYWORDS[definition_tokens[0].value] = value
                elif token.value == 'TOKENS':
                    count = 0
                    token_re_definition_tokens = []
                    token_re_section_definitions = []
                    while True:
                        temp_token = self.tokens_clean[token_index + count + 1]

                        if temp_token.type == 'final':
                            token_re_section_definitions.append(token_re_definition_tokens)
                            token_re_definition_tokens = []
                        else:
                            token_re_definition_tokens.append(temp_token)
                        count += 1

                        if temp_token.value in ['TOKENS', 'PRODUCTIONS', 'END']:
                            token_index -= count
                            break
                    token_index += count

                    for definition_tokens in token_re_section_definitions:
                        value = []
                        for token in definition_tokens[2::]:
                            if token.type == 'ident':
                                if token.value not in ['EXCEPT', 'KEYWORDS']:
                                    value.append(token)
                            elif token.type == 'string':
                                value.append(token)
                            elif token.type in ['iteration', 'option', 'group', 'or']:
                                value.append(token)

                        self.TOKENS_RE[definition_tokens[0].value] = value
            token_index += 1

        self.CHARACTERS = self.parse_CHARACTERS(self.CHARACTERS)
        self.CHARACTERS[' '] = ' '

        self.TOKENS_RE = self.parse_TOKENS_RE(self.TOKENS_RE)
        self.TOKENS_RE['space'] = ' '

    def check_sintax(self):
        # Analizar flujo de tokens
        has_valid_sintax = self.has_valid_sintax(PRODUCTIONS['program'])

        if not has_valid_sintax:
            self.sintax_errors = True

        if self.current_token_index < len(self.tokens_clean):
            # if self.tokens_clean[self.current_token_index] != self.tokens_clean[-1]:
            #     self.sintax_errors = True
            Log.FAIL('\n\nError en la linea ', self.tokens_clean[self.current_token_index].line, ' columna ', self.tokens_clean[self.current_token_index].column, ': ', self.tokens_clean[self.current_token_index].value)

    def has_valid_sintax(self, productions):
        valid_production = False
        current_sintax_index = 0
        while current_sintax_index < len(productions):
            sintax_token = productions[current_sintax_index]
            ocurrences = False
            optional = False

            if sintax_token.get('ocurrences') == '+':
                # This means that the token could be 0 to n times repetead
                ocurrences = True

            if sintax_token.get('optional'):
                # This means that the token could be 0 times
                optional = True

            if sintax_token['type'] == 'PRODUCTION':
                valid_sub_production = self.has_valid_sintax(PRODUCTIONS[sintax_token['value']])

                valid_production = valid_sub_production

                if not valid_sub_production:
                    if optional and not ocurrences:
                        valid_production = True

            else:
                if self.current_token_index < len(self.tokens_clean):
                    current_token = self.tokens_clean[self.current_token_index]

                    matches = self.matches(sintax_token, current_token)

                    Log.INFO(matches, current_token, sintax_token)

                    valid_production = matches

                    if matches:
                        self.current_token_index += 1
                    else:
                        if optional and not ocurrences:
                            valid_production = True

            if ocurrences:
                while True:
                    valid_repited_sub_production = self.has_valid_sintax(PRODUCTIONS[sintax_token['value']])

                    if not valid_repited_sub_production:
                        break

            current_sintax_index += 1

        return valid_production

    def matches(self, sintax_token, current_token):
        # Se valida si el token actual es un token valido para la sintaxis
        if sintax_token['type'] == 'KEYWORD':
            if sintax_token['type'] == current_token.type:
                if sintax_token['value'] == current_token.value:
                    # Log.OKGREEN(f'\t{current_token.type} {current_token.value} {sintax_token}')
                    return True
        elif sintax_token['type'] == 'OPTIONS':
            for option in sintax_token['options']:
                if self.matches(option, current_token):
                    # Log.OKGREEN(f'\t{current_token.type} {current_token.value} {option}')
                    return True
            return False
        elif sintax_token['type'] == 'PRODUCTION':
            return self.matches(PRODUCTIONS[sintax_token['value']][0], current_token)
        else:
            if sintax_token['type'] == current_token.type:
                if sintax_token.get('match'):
                    if  sintax_token.get('match') == current_token.value:
                        # Log.OKGREEN(f'\t{current_token.type} {current_token.value} {sintax_token}')
                        return True
                    else:
                        return False

                # Log.OKGREEN(f'\t{current_token.type} {current_token.value} {sintax_token}')
                return True

        return False

    def parse_CHARACTERS(self, CHARACTERS):
        options = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']
        cont = 0
        keys = list(CHARACTERS.keys())
        for i in range(len(CHARACTERS)):
            # self.symbols[options[cont]] = keys[i]
            self.symbols[keys[i]] = options[cont]
            CHARACTERS[options[cont]] = CHARACTERS.pop(keys[i])
            cont += 1

        return CHARACTERS

    def parse_TOKENS_RE(self, TOKENS_RE):
        # 'letter {letter|digit} EXCEPT KEYWORDS' ---> 'A«A¦B»±'
        options = ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

        for key, val in TOKENS_RE.items():
            value = ''
            for token in val:
                if token.value in self.symbols:
                    value += self.symbols[token.value]
                else:
                    if token.type in ['iteration', 'option', 'group', 'or']:
                        value += token.value
                    else:
                        # TODO: Add support for strings
                        for o in options:
                            if o not in list(self.symbols.values()):
                                self.symbols[token.value] = o
                                value += o
                                self.CHARACTERS[o] = token.value.replace('"', '')
                                break
                        # value += token.value
                        # print(token)

            TOKENS_RE[key] = self.changeExp(value)

        return TOKENS_RE

    def changeExp(self, re):
        cont = 0
        closeK = []
        for pos, char in enumerate(re):
            if char == '{':
                cont += 1
            elif char == '}':
                closeK.append(pos)
                cont -= 1

        if cont != 0:
            return False

        re = re.replace('{', '«')
        re = re.replace('}', '»')
        re = re.replace('|', '¦')

        for i in range(len(closeK)):
            re = re[:closeK[i]+1+i] + '±' + re[closeK[i]+1+i:]

        return re

    def has_sintax_errors(self):
        if self.sintax_errors:
            Log.FAIL('\nErrores en archivo de COCOL')
            exit()
