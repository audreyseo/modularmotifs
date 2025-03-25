
sealed abstract class Syntax {
  def to_code(t:  Target): String
}

sealed abstract class AbstractIdentifier(s: String) extends Syntax

case class Identifier(s: String) extends AbstractIdentifier(s) {
  def to_code(t: Target): String = s
}

sealed abstract class SpecialMethod(py: String, ts: String) extends AbstractIdentifier("special") {
  def to_code(t: Target): String = t match {
    case Python => py
    case TypeScript => ts
  }
}
object SpecialMethod {
  case object ToString extends SpecialMethod("__str__", "toString")
  case object Length extends SpecialMethod("__len__", "length")
  case object Eq extends SpecialMethod("__eq__", "equals")
  case object Hash extends SpecialMethod("__hash__", "")
  case object Representation extends SpecialMethod("__repr__", "")
  case object Constructor extends SpecialMethod("__init__", "constructor")
}

sealed abstract class SyntaxType extends Syntax
case object IntegerType extends SyntaxType {
  def to_code(t: Target): String = {
    t match {
      case Python => "int"
      case TypeScript => "number"
    }
  }
}

case object FloatType extends SyntaxType {
  def to_code(t: Target) : String = {
    t match {
      case Python => "float"
      case TypeScript => "number"
    }
  }
}
case class ListType(T: SyntaxType) extends SyntaxType {
  def to_code(t: Target) : String = {
    t match {
      case Python => s"list[${T.to_code(t)}]"
      case TypeScript => s"${T.to_code(t)}[]"
    }
  }
}

case object StringType extends SyntaxType {
  def to_code(t: Target) : String = {
    t match {
      case Python => "str"
      case TypeScript => "string"
    }
  }
}

case class TupleType(ts: SyntaxType*) extends SyntaxType {
  def to_code(t: Target) : String = {
    (t match {
      case Python => "tuple["
      case TypeScript => "["
    }) + ts.map(v => v.to_code(t)).mkString(", ") + "]"
  }
}

case class ClassType(c: Identifier) extends SyntaxType {
  def to_code(t: Target) : String = c.to_code(t)
}

case class Parameter(id: Identifier, T: SyntaxType) extends Syntax {
  def to_code(t: Target) : String = id.to_code(t) + ": " + T.to_code(t)
}

sealed abstract class SyntaxFunction(name: Identifier, arguments: Seq[Parameter], return_type: SyntaxType, body: Seq[Statement]) extends Syntax


def python_function(name: String, arguments: Seq[String], return_type: String, body: Seq[String]): String = {
  s"def ${name}(${arguments.mkString(", ")}) -> ${return_type}:" + "\n  " + body.mkString("\n  ")
}

case class Method(name: Identifier, arguments: Seq[Parameter], return_type: SyntaxType, body: Seq[Statement]) extends SyntaxFunction(name, arguments, return_type, body) {
  def to_code(t: Target) : String = {
    t match {
      case Python =>
        python_function(name.to_code(t), "self" +: arguments.map(v => v.to_code(t)), return_type.to_code(t), body.map(v => v.to_code(t)))
      case TypeScript =>
        ""
    }
  }
}

sealed abstract class Class(name: Identifier, fields: Seq[(Identifier, SyntaxType)]) extends Syntax

sealed abstract class Expr extends Syntax

case class FieldAccess(f: Identifier) extends Expr {
  def to_code(t: Target) : String = {
    t match {
      case Python => s"self.${f.to_code(t)}"
      case TypeScript => s"this.${f.to_code(t)}"
    }
  }
}


//sealed abstract class LiteralType extends Expr
//
//case object IntegerLiteral extends LiteralType {
//  def to_code(t: Target): String = {
//
//  }
////}
//case object StringLiteral extends LiteralType
//case object ListLiteral extends LiteralType
//case object FloatLiteral extends LiteralType



sealed abstract class Statement extends Syntax

case class Return(e: Option[Expr]) extends Statement {
  def to_code(t: Target) : String = s"return ${e match {
    case Some(expr) => expr.to_code(t)
    case None => ""
  }}" + (t match {
    case Python => ""
    case TypeScript => ";"
  })
}



@main def hello(): Unit = {
  println(ListType(FloatType).to_code(Python))
  println(TupleType(FloatType, TupleType(IntegerType, IntegerType)).to_code(Python))
  val mymethod = Method(Identifier("to_python"), Seq(), StringType, Seq(Return(Some(FieldAccess(Identifier("string"))))))
  println(mymethod)
  println(mymethod.to_code(Python))
}