import random 

def rolar_dados(expressao, retorno): 
    #1d6
    tmp = expressao.split("d");
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

def rolar_dados_atributos():
    atributos = []
    for _ in range(6):
        resultados = rolar_dados("4d6","valores")
        resultados.sort()
        resultados.pop(0)
        atributos.append(sum(resultados))
    return atributos