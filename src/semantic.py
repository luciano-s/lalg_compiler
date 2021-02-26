class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {"global": {}}
        self.current_scope = "global"
        self.IDENTIFIER = "<IDENTIFIER>"
        self.PROCEDURES = "<PROCEDURES>"
        self.SIMPLE_TYPE = "<SIMPLE_TYPE>"
        self.symbol_table["global"][self.IDENTIFIER] = []
        self.symbol_table["global"].update({"FATHER": None})
        self.errors = []

    def is_identifier(self, lexem):
        if lexem[1] == self.IDENTIFIER:
            return lexem[0]

    def insert_identifiers_generic(self, identifiers, variable_type):

        final_identifiers = []
        for identifier in identifiers:
            # print(identifier)
            # input()
            final_identifiers.append(
                {
                    identifier[0]: [
                        {"type": f"<{variable_type.upper()}>"},
                        {"used": False},
                        {"value": None},
                    ]
                }
            )

        for identifier in final_identifiers:

            if identifier not in self.symbol_table[self.current_scope][self.IDENTIFIER]:
                self.symbol_table[self.current_scope][self.IDENTIFIER].append(
                    identifier
                )
            else:
                self.dispatch_semantic_error(
                    [
                        f"Variable {identifier} arealdy exists!",
                        "Do not apply",
                        "Do not apply",
                    ]
                )

    def insert_identifiers(self, value, variable_type):
        identifiers = list(map(lambda t: t, list(filter(self.is_identifier, value))))

        self.insert_identifiers_generic(identifiers, variable_type)

    def dispatch_semantic_error(self, error):
        if error not in self.errors:
            self.errors.append(error)

    def is_type(self, lexem):
        if lexem[1] == "<SIMPLE_TYPE>":
            return lexem

    def get_identifiers_of_a_type(self, lexems):
        identifiers = []
        index = 0

        for lexem in lexems:
            if lexem[1] == self.SIMPLE_TYPE:
                return {lexem[0]: identifiers}
            if lexem[1] == self.IDENTIFIER:
                identifiers.append(lexem[0])
            index += 1

    def get_all_identifiers_in_parameters(self, token):
        lim = 0
        identifiers_in_declaration = []

        for x in token.lexem:
            if x[1] == "<CLOSE_PARENTHESIS>":
                break
            lim += 1
        search_lexems = token.lexem[2:lim]
        len_set_of_identifiers = len(list(filter(self.is_type, search_lexems)))
        index = 0

        while index < len_set_of_identifiers:
            identifiers = self.get_identifiers_of_a_type(search_lexems)
            identifiers_in_declaration.append(identifiers)
            index += 1
        return identifiers_in_declaration

    def declare_procedure(self, procedure):
        if procedure in self.symbol_table.keys():
            self.dispatch_semantic_error(
                [f"Procedure {procedure} already exists!", procedure[3], procedure[4]]
            )
        else:
            father = {"FATHER": self.current_scope}

            self.symbol_table.update({procedure: {}})
            self.symbol_table[procedure][self.IDENTIFIER] = []
            self.symbol_table[procedure].update(father)
            self.symbol_table[procedure]["PARAMETERS"] = []

    def set_scope(self, name="FATHER"):
        if name == "FATHER":
            self.current_scope = self.symbol_table[self.current_scope]["FATHER"]
            return
        self.current_scope = name

    # TODO: REMOVE METHOD
    def procedure_declaration(self, token):

        identifiers_in_declaration = self.get_all_identifiers_in_parameters(token)

        for ident_dict in identifiers_in_declaration:
            key = list(ident_dict.keys())[0]

            self.symbol_table[self.current_scope]["PARAMETERS"].append(
                f"<{key.upper()}>"
            )

            self.insert_identifiers_generic(
                identifiers=ident_dict[key], variable_type=f"<{key.upper()}>"
            )

    def insert_parameters(self, value, variable_type):
        self.insert_identifiers(value=value, variable_type=variable_type)

        [
            self.symbol_table[self.current_scope]["PARAMETERS"].append(
                f"<{variable_type.upper()}>"
            )
            for i in range(len(list(filter(self.is_identifier, value))))
        ]

    def validate_procedure_call(self, procedure, parameters):
        if len(self.symbol_table[procedure]["PARAMETERS"]) == len(parameters):
            i = 0
            while i < len(parameters):
                if self.symbol_table[procedure]["PARAMETERS"][i] != parameters[i]:
                    self.dispatch_semantic_error(
                        [
                            f"Type error: expected {self.symbol_table[procedure]['PARAMETERS'][i]}, got {parameters[i]}",
                            parameters[3],
                            parameters[4],
                        ]
                    )

    def get_identifier_type(self, identifier, scope=None):
        if scope is None:
            scope = self.current_scope
        while scope is not None:
            for var in self.symbol_table[scope][self.IDENTIFIER]:
                if identifier in list(var.keys()):
                    return var[identifier][0]["type"]
            scope = self.symbol_table[scope]["FATHER"]
        return None

    def is_bool(self, expression):
        if expression[0] in ["<", ">", "<>", "<=", ">=", "and", "or"]:
            return True

    def get_expression_type(self, expression):

        i = 0
        current_type = None
        OP_SIGNAL = [
            "<PLUS_SIGN>",
            "<MULTIPLICATION_SIGN>",
            "<MINUS_SIGN>",
            "<RELATION>",
            "<KEYWORD_OR>",
            "<KEYWORD_AND>",
            "<KEYWORD_NOT>",
        ]
        BOOLEAN_EXPRESSION = [
            "<KEYWORD_OR>",
            "<KEYWORD_AND>",
            "<KEYWORD_NOT>",
        ]
        has_bool = False
        has_float = False
        if len(expression) == 1:
            first_therm = expression[0]
            if first_therm[1] == self.IDENTIFIER:
                type = self.get_identifier_type(identifier=first_therm[0])
                self.update_variable_used(variable=first_therm)
                return type
            else:
                if first_therm[1] == "<NUMBER>":
                    if first_therm[0].find(".") == 1:
                        return "<REAL>"
                    return "<INT>"
                return "<BOOLEAN>"
        while i + 1 < len(expression):
            if expression[i][1] in OP_SIGNAL:
                if expression[i][1] == "<RELATION>":
                    has_bool = True
                if current_type is None:
                    first_therm = expression[i - 1]
                    second_therm = expression[i + 1]
                    if first_therm[1] == self.IDENTIFIER:
                        self.update_variable_used(variable=first_therm)
                        first_therm = (
                            first_therm[0],
                            self.get_identifier_type(identifier=first_therm[0]),
                            first_therm[2],
                            first_therm[3],
                            first_therm[4],
                        )
                    else:
                        type_first = first_therm[1]
                        if first_therm[1] == "<NUMBER>":
                            if first_therm[0].find(".") == 1:
                                type_first = "<REAL>"
                                has_float = True
                            else:
                                type_first = "<INT>"
                        first_therm = (
                            first_therm[0],
                            type_first,
                            first_therm[2],
                            first_therm[3],
                            first_therm[4],
                        )
                    if second_therm[1] == self.IDENTIFIER:
                        self.update_variable_used(variable=second_therm)
                        second_therm = (
                            second_therm[0],
                            self.get_identifier_type(identifier=second_therm[0]),
                            second_therm[2],
                            second_therm[3],
                            second_therm[4],
                        )
                    else:
                        type_second = second_therm[1]
                        if second_therm[1] == "<NUMBER>":
                            if second_therm[0].find(".") == 1:
                                type_second = "<REAL>"
                                has_float = True
                            else:
                                type_second = "<INT>"
                        second_therm = (
                            second_therm[0],
                            type_second,
                            second_therm[2],
                            second_therm[3],
                            second_therm[4],
                        )
                    if first_therm[1] == second_therm[1]:
                        current_type = first_therm[1]
                        if expression[i][1] in BOOLEAN_EXPRESSION:
                            print(expression[i][1])
                            # input()
                            if "<BOOLEAN>" != first_therm[1]:
                                self.dispatch_semantic_error(
                                    [
                                        f"Operator {expression[i][1]} expect type Boolean, got {first_therm[1]}",
                                        first_therm[3],
                                        first_therm[4],
                                    ]
                                )
                            if "<BOOLEAN>" != second_therm[1]:

                                self.dispatch_semantic_error(
                                    [
                                        f"Operator {expression[i][1]} expect type Boolean, got {second_therm[1]}",
                                        second_therm[3],
                                        second_therm[4],
                                    ]
                                )
                        else:
                            if first_therm[1] not in ["<REAL>", "<INT>"]:
                                self.dispatch_semantic_error(
                                    [
                                        f"Operator {expression[i][1]} expect type Real or Int, got {first_therm[1]}",
                                        first_therm[3],
                                        first_therm[4],
                                    ]
                                )
                            if second_therm[1] not in ["<REAL>", "<INT>"]:
                                self.dispatch_semantic_error(
                                    [
                                        f"Operator {expression[i][1]} expect type Real or Int, got {second_therm[1]}",
                                        second_therm[3],
                                        second_therm[4],
                                    ]
                                )
                        i += 2
                    else:
                        self.dispatch_semantic_error(
                            [
                                f"Type error: expected {first_therm[1]} got {second_therm[1]}",
                                second_therm[3],
                                second_therm[4],
                            ]
                        )
                        i += 2
                else:
                    second_therm = expression[i + 1]
                    if second_therm[1] == self.IDENTIFIER:
                        self.update_variable_used(variable=second_therm)
                        second_therm[1] = self.get_identifier_type(
                            identifier=second_therm[0]
                        )
                    else:
                        type_second = second_therm[1]
                        if second_therm[1] == "<NUMBER>":
                            if second_therm[0].find(".") == 1:
                                type_second = "<REAL>"
                                has_float = True
                            else:
                                type_second = "<INT>"
                        second_therm = (
                            second_therm[0],
                            type_second,
                            second_therm[2],
                            second_therm[3],
                            second_therm[4],
                        )
                    if current_type == second_therm[1]:
                        if expression[i][1] in BOOLEAN_EXPRESSION:
                            print(expression[i][1])
                            # input()
                            if "<BOOLEAN>" != current_type:
                                self.dispatch_semantic_error(
                                    [
                                        f"Operator {expression[i][1]} expect type Boolean, got {current_type}",
                                        second_therm[3],
                                        second_therm[4],
                                    ]
                                )
                            if "<BOOLEAN>" != second_therm[1]:
                                self.dispatch_semantic_error(
                                    [
                                        f"Operator {expression[i][1]} expect type Boolean, got {second_therm[1]}",
                                        second_therm[3],
                                        second_therm[4],
                                    ]
                                )
                        else:
                            if current_type not in ["<REAL>", "<INT>"]:
                                self.dispatch_semantic_error(
                                    [
                                        f"Operator {expression[i][1]} expect type Real or Int, got {current_type}",
                                        second_therm[3],
                                        second_therm[4],
                                    ]
                                )
                            if second_therm[1] not in ["<REAL>", "<INT>"]:
                                self.dispatch_semantic_error(
                                    [
                                        f"Operator {expression[i][1]} expect type Real or Int, got {second_therm[1]}",
                                        second_therm[3],
                                        second_therm[4],
                                    ]
                                )
                        i += 2
                    else:
                        self.dispatch_semantic_error(
                            [
                                f"Type error: expected {current_type} got {second_therm[1]}",
                                second_therm[3],
                                second_therm[4],
                            ]
                        )
                        i += 2
            else:
                i += 1

        if has_bool:
            return "<BOOLEAN>"
        elif has_float:
            return "<REAL>"
        return "<INT>"

    def validate_assignment(self, variable, expression):
        identifier = variable[0]

        result = self.validate_variable_declaration(
            variable=variable, scope=self.current_scope
        )
        if result[0]:
            for dic in self.symbol_table[self.current_scope][self.IDENTIFIER]:
                var_structure = dic.get(identifier)
                if var_structure is not None:
                    var_structure = dic
                    break
            expression_type = self.get_expression_type(expression)

            identifier_type = self.get_identifier_type(
                identifier=identifier[0], scope=result[1]
            )
            # print("expressoin: ", expression_type)
            # print("identifier: ", identifier_type)
            # input()

            # print("identifier type: ", identifier_type)
            # print("expression type: ", expression_type)

            if expression_type != identifier_type:
                self.dispatch_semantic_error(
                    [
                        f"Type error, expected {identifier_type}, got {expression_type}",
                        variable[3],
                        variable[4],
                    ]
                )
            else:
                self.update_variable_initialized(variable, scope=result[1])
        else:
            self.dispatch_semantic_error(
                [f"Variable {variable[0]} was not declared", variable[3], variable[4]]
            )

    def show_symbol_table(self):
        print(self.symbol_table)

    def validate_variable_declaration(self, variable, scope):

        if scope == "global" and not self.is_variable_in_scope(variable[0], scope):
            self.dispatch_semantic_error(
                [f"Variable {variable[0]} was not declared", variable[3], variable[4]]
            )
            return False, False
        else:
            if self.is_variable_in_scope(variable[0], scope):
                return True, scope
            else:
                self.validate_variable_declaration(
                    variable=variable, scope=self.symbol_table[scope]["FATHER"]
                )

    def is_variable_in_scope(self, variable, scope):
        variables_in_scope = self.symbol_table[scope][self.IDENTIFIER]
        if (
            len(
                list(
                    filter(
                        lambda x: x is True,
                        list(
                            map(
                                lambda d: variable in list(d.keys()), variables_in_scope
                            )
                        ),
                    )
                )
            )
            > 0
        ):
            return True
        return False

    def update_variable_used(self, variable, scope=None):
        if scope is None:
            scope = self.current_scope
        while scope is not None:
            for identifier in self.symbol_table[scope][self.IDENTIFIER]:
                if variable[0] in list(identifier.keys()):
                    if identifier[variable[0]][2]["value"] is not None:
                        identifier[variable[0]][1]["used"] = True
                        return
                    else:
                        self.dispatch_semantic_error(
                            [
                                f"Variable {variable[0]} was not initialized!",
                                variable[3],
                                variable[4],
                            ]
                        )
                        return
            scope = self.symbol_table[scope]["FATHER"]
        self.dispatch_semantic_error(
            [
                f"Variable {variable[0]} was not declared!",
                variable[3],
                variable[4],
            ]
        )

    def update_variable_initialized(self, variable, scope=None):
        if scope is None:
            scope = self.current_scope
        while scope is not None:
            for identifier in self.symbol_table[scope][self.IDENTIFIER]:
                if variable[0] in list(identifier.keys()):
                    identifier[variable[0]][2]["value"] = True
                    return
            scope = self.symbol_table[scope]["FATHER"]

        self.dispatch_semantic_error(
            [f"Variable {variable[0]} was not declared!", variable[3], variable[4]]
        )

    def search_for_non_used_variables(self):
        for scope in self.symbol_table.keys():
            for var in self.symbol_table[scope][self.IDENTIFIER]:
                key = list(var.keys())[0]
                if not var[key][1]["used"]:
                    self.dispatch_semantic_error(
                        [
                            f"Variable {key} was declared but not used",
                            "Do no apply",
                            "Do not apply",
                        ]
                    )

    def get_errors(self):
        return self.errors
