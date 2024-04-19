import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from threading import Timer

# Variáveis globais para armazenar os últimos rolls e o modelo treinado
rolls_anteriores = []
modelo = None
encoder = None
ultimo_horario_processado = None

# Criação de uma sessão para reutilizar conexões HTTP
sessao = requests.Session()

## Função para obter todos os "rolls" disponíveis na API
def obter_rolls_disponiveis():
    url = 'https://blaze1.space/api/roulette_games/recent'
    response = sessao.get(url, timeout=10)  # Define um tempo limite de 10 segundos para a solicitação
    if response.status_code == 200:
        dados = response.json()
        return dados if dados else None  # Retorna os "rolls" se houver, senão None
    else:
        print("Erro ao obter os últimos rolls da API")
        return None
    
# Função para treinar o modelo com os dados fornecidos
def treinar_modelo(dados):
    global modelo, encoder
    encoder = LabelEncoder()
    categorias = [categorizar_numero(roll['roll']) for roll in dados]
    encoder.fit(categorias)
    categorias_encoded = encoder.transform(categorias)
    X = [[roll['roll']] for roll in dados]
    modelo = RandomForestClassifier()
    modelo.fit(X, categorias_encoded)

# Função para categorizar os números
def categorizar_numero(numero):
    if numero == 0:
        return 'Branco'
    elif 1 <= numero <= 7:
        return 'Vermelho'
    else:
        return 'Preto'

# Função para prever os próximos números/cor com base nos últimos "rolls"
def prever_proximos_numeros(ultimos_rolls):
    X = [[roll['roll']] for roll in ultimos_rolls]
    categorias_previstas_encoded = modelo.predict(X)
    categorias_previstas = encoder.inverse_transform(categorias_previstas_encoded)
    contagem = {categoria: list(categorias_previstas).count(categoria) for categoria in set(categorias_previstas)}
    total = sum(contagem.values())
    probabilidade = {categoria: contagem[categoria] / total for categoria in contagem}
    return probabilidade

# Função para salvar os rolls em um arquivo de texto
def salvar_rolls_em_txt(rolls):
    with open('rolls.txt', 'w') as file:
        for roll in rolls:
            file.write(f"{roll['roll']} {categorizar_numero(roll['roll'])}\n")

# Função principal para agendar a próxima atualização
def agendar_proxima_atualizacao():
    timer = Timer(1, main)
    timer.start()

# Função principal
def main():
    global rolls_anteriores, modelo, encoder, ultimo_horario_processado
    
    # Obtém o último "roll" da API
    todos_rolls = obter_rolls_disponiveis()
    if todos_rolls:
        # Verifica se houve mudança no último "roll"
        if not ultimo_horario_processado or todos_rolls[0]['created_at'] > ultimo_horario_processado:
            ultimo_horario_processado = todos_rolls[0]['created_at']  # Atualiza o último horário processado
            
            # Adiciona o último roll aos rolls anteriores
            rolls_anteriores.append(todos_rolls[0])
            
            # Salva os rolls em um arquivo de texto
            salvar_rolls_em_txt(rolls_anteriores)
            
            # Espera até ter um número suficiente de "rolls" antes de começar a previsão
            if len(rolls_anteriores) < 40:
                rolls_restantes = 40 - len(rolls_anteriores)
                print(f"Aguardando mais {rolls_restantes} rolls para iniciar as previsões...")
                agendar_proxima_atualizacao()
                return       
            
            # Treina o modelo com os dados obtidos
            treinar_modelo(rolls_anteriores)
            
            # Preve os próximos números/cor com base nos últimos "rolls" se o modelo estiver treinado
            if modelo is not None and encoder is not None:
                probabilidade = prever_proximos_numeros(rolls_anteriores)
                print("--------------------")
                print("Probabilidade de previsão:")
                for categoria, prob in probabilidade.items():
                    print(f"{categoria}: {prob:.2f}")
                
                # Mostra as informações do último roll
                ultimo = todos_rolls[0]
                cor_real = categorizar_numero(ultimo['roll'])
                print("\nÚltimo resultado em tempo real:")
                print(f"Número: {ultimo['roll']} - Cor: {cor_real}")
                print("--------------------")
    
    else:
        print("Não foi possível obter o último roll da API")
    
    # Agendar a próxima atualização
    agendar_proxima_atualizacao()

if __name__ == "__main__":
    main()
