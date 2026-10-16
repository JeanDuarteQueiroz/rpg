import random 

def rolar_dados(expressao: str, retorno: str = "total"): 
    # Transforma "1D6" ou "1d6" no padrão correto
    tmp = expressao.lower().split("d")
    quantidade = int(tmp[0])
    lados = int(tmp[1])
    
    valores = []
    total = 0
    for _ in range(quantidade):
         resultado = random.randint(1, lados)
         valores.append(resultado)
         total += resultado
         
    if retorno == "total":
        return total
    elif retorno == "valores":
        return valores
    else:
        return total, valores

def rolar_dados_atributos() -> list:
    atributos = []
    for _ in range(6):
        resultados = rolar_dados("4d6", "valores")
        resultados.sort()
        resultados.pop(0) # Remove o menor dado (regra padrão D&D)
        atributos.append(sum(resultados))
    return atributos