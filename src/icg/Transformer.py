import lark
from .horn import horn
from .TA import TA,Label
def ignore():
	raise lark.Discard()
@lark.v_args(tree=True)
class Transformer(lark.Transformer):
	def __init__(self,symtable,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.symtable=symtable
		self.max_level=0
	def programa(self,tree):
		ans=lark.Tree("tac",tree.children[0])
		ans.max_level=self.max_level
		return ans
	def lista_declaracoes(self,tree):
		if len(tree.children)==2:
			return tree.children[0]+tree.children[1]
		return tree.children[0]
	def declaracao(self,tree):
		return tree.children[0]
	def declaracao_variaveis(self,tree):
		ignore()
	def tipo(self,tree):
		ignore()
	def declaracao_funcoes(self,tree):
		var=tree.entry
		if var.type=="void":
			tree.children[-1].append(TA("ret"))
		return [Label(var.name,tree.children[-1])]
	def parametros(self,tree):
		ignore()
	def lista_parametros(self,tree):
		ignore()
	def param(self,tree):
		ignore()
	def declaracao_composta(self,tree):
		return tree.children[-2]
	def declaracao_locais(self,tree):
		ignore()
	def lista_comandos(self,tree):
		if len(tree.children)==2:
			return tree.children[0]+tree.children[1]
		return []
	def comando(self,tree):
		return tree.children[0]
	def declaracao_expressao(self,tree):
		if len(tree.children)==1:
			return [TA("nop")]
		return tree.children[0]
	def declaracao_selecao(self,tree):
		raise RuntimeError(NotImplemented)
	def declaracao_iteracao(self,tree):
		raise RuntimeError(NotImplemented)
	def declaracao_retorno(self,tree):
		if len(tree.children)==2:
			return [TA("ret")]
		l=tree.children[1]
		t=l[-1].arg1
		return l+[TA("ret_val",t),TA("ret")]

	def expressao(self,tree):
		if getattr(tree,"is_head",None)!=None:
			ans=horn(tree.expression)
			#----------------------------------------------------------------
			#search for call instructions, if the function is void, remove get_arg instruction
			#and decrement level
			call_ta=next((ta for ta in ans.list if ta.op=="call"),None)
			if call_ta:
				entry=self.symtable.get(tree,call_ta.arg1)
				if entry.type=="void":
					ans.level-=1
					ans.list.pop(-1)
			#----------------------------------------------------------------
			#search for pattern of attr style "x=y", if the 2 variables are vector, then join them all
			# in single set_vec instructions
			if  len(ans.list)>0 and ans.list[0].data=="attr":
				arg1,arg2=ans.list[0].arg1,ans.list[0].arg2
				#if both are variables
				if all((not a.isnumeric() for a in (arg1,arg2))):
					var1=self.symtable.get(tree,arg1)
					var2=self.symtable.get(tree,arg2)
					#if both are vectors
					if all((var.is_vector() for var in (var1,var2))):
						ans.list=[TA("set_vec",arg1,arg2)]
						ans.level=0

			self.max_level=max(self.max_level,ans.level)
			return ans.list
		return tree
	# def variavel(self,tree):

	# def expressao_simples(self,tree):

	# def op_relacional(self,tree):

	# def soma_expressao(self,tree):

	# def soma(self,tree):

	# def termo(self,tree):

	# def mult(self,tree):

	# def fator(self,tree):

	# def ativacao(self,tree):

	# def argumentos(self,tree):

	# def lista_argumentos(self,tree):
