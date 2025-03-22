grammar = r"""
?statements : statement*

?statement : design_op
           | set_variable
           | import
           | from_import

?set_variable : variable "=" expr

?import : "import" module_access "as" IDENTIFIER
        | "import" module_access

?from_import : "from" module_access "import" IDENTIFIER ("," IDENTIFIER)*

?module : IDENTIFIER

?design_op : variable "=" variable "." ADD_MOTIF "(" expr "," expr "," expr ")"
           | variable "." REMOVE_MOTIF "(" expr ")"
           | variable "=" variable "." MOTIFIFY "(" expr "," expr "," expr "," expr ")"
           | size_op

?size_op : variable "=" variable "." ADD_ROW "(" add_exprs? ")"
         | variable "," variable "=" variable "." REMOVE_ROW "(" expr? ")"
         | variable "=" variable "." ADD_COLUMN "(" add_exprs? ")"
         | variable "," variable "=" variable "." REMOVE_COLUMN "(" expr? ")"

?add_exprs : expr "," expr
           | expr


?expr : literal
      | variable
      | object_init
      | attr_access
      | module_ref
      | module_access
      | object_access
      | object_method_call
      | keyword_arg

?literal : int
         | float
         | str
         | list

?int : INT_NUMBER

?float : FLOAT_NUMBER

?str : STRING

?list : "[" literal_list "]"

?literal_list : [ expr ("," expr)*]

variable : IDENTIFIER

?object_init : class_name "(" args_list ")"

args_list : [expr ("," expr)*]

?attr_access : expr "[" expr "]"

module_ref :  IDENTIFIER

?module_access : module_access "." IDENTIFIER
               | module_ref

?object_access : expr "." IDENTIFIER

?object_method_call : expr "." IDENTIFIER "(" args_list ")"

?keyword_arg : IDENTIFIER "=" expr

?class_name : CAPITAL_IDENTIFIER



ADD_MOTIF : "add_motif"
REMOVE_MOTIF : "remove_motif"
ADD_ROW : "add_row"
ADD_COLUMN : "add_column"
REMOVE_ROW : "remove_row"
REMOVE_COLUMN : "remove_column"
MOTIFIFY : "motifify"

IDENTIFIER : CNAME

CAPITAL_IDENTIFIER : /[A-Z][a-zA-Z0-9_]*/

COMMENT: "#" /[^\n]*/ NEWLINE

NEWLINE: /[\n]/
INT_NUMBER : /-?\d+/
FLOAT_NUMBER : /-?\d+\.\d+/

%import common.ESCAPED_STRING   -> STRING


%import common.CNAME
%import common.WS

%ignore WS
%ignore COMMENT
%ignore NEWLINE

"""
