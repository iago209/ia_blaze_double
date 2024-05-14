import requests
import time

# Função para obter os dados mais recentes da API
def get_recent_rolls():
    url = "https://blaze1.space/api/roulette_games/recent"
    response = requests.get(url)
    if response.status_code == 200:
        rolls_data = response.json()
        return rolls_data
    else:
        print("Falha ao obter os dados da API")
        return None

# Função para calcular as chances de cada cor no próximo roll
def calculate_color_chances(rolls_data):
    red_count = 0
    black_count = 0
    white_count = 0
    total_rolls = len(rolls_data)

    for roll in rolls_data:
        color = roll["color"]
        if color == 1:
            red_count += 1
        elif color == 2:
            black_count += 1
        else:
            white_count += 1

    red_chance = red_count / total_rolls
    black_chance = black_count / total_rolls
    white_chance = white_count / total_rolls

    return red_chance, black_chance, white_chance

# Função para calcular as chances de cair um número branco no próximo roll
def calculate_white_chance(rolls_data):
    white_chance = 0
    white_key_numbers = [12, 4, 11, 5]

    for i, roll in enumerate(rolls_data[:-1]):
        if roll["roll"] in white_key_numbers:
            if rolls_data[i+1]["color"] == 0:
                white_chance += 1

    if len(white_key_numbers) > 0:
        white_chance /= len(white_key_numbers)

    return white_chance

# Função principal para atualizar e mostrar palpites a cada 5 segundos
def main():
    recent_roll_id = ""
    while True:
        rolls_data = get_recent_rolls()
        if rolls_data:
            latest_roll = rolls_data[0]
            if latest_roll["id"] != recent_roll_id:
                recent_roll_id = latest_roll["id"]
                red_chance, black_chance, white_chance = calculate_color_chances(rolls_data)
                next_white_chance = calculate_white_chance(rolls_data)
                print(f"Chances de cor no próximo roll:")
                print(f"Vermelho: {red_chance * 100}%")
                print(f"Preto: {black_chance * 100}%")
                print(f"Branco: {white_chance * 100}% (considerando os números-chave)")
                print(f"Chances de branco após números-chave: {next_white_chance * 100}%")
                print("\n")
        time.sleep(5)

if __name__ == "__main__":
    main()
