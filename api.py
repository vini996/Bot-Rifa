from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)
CSV_FILE = "rifa.csv"

# Inicializa o arquivo CSV se não existir
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["numero", "status"])
            for i in range(1, 100):
                writer.writerow([str(i).zfill(2), "disponivel"])
            writer.writerow(["00", "disponivel"])  # 00 como 100

# Lê o CSV e retorna como lista de dicionários
def read_csv():
    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

# Escreve a lista de dicionários de volta para o arquivo CSV
def write_csv(data):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["numero", "status"])
        writer.writeheader()
        writer.writerows(data)

@app.route("/rifa", methods=["GET"])
def get_rifa():
    rifa_data = read_csv()
    return jsonify(rifa_data)

@app.route("/rifa/vender", methods=["POST"])
def vender_numero():
    data = request.json
    numero = data.get("numero")

    if not numero:
        return jsonify({"erro": "Número não fornecido"}), 400

    if numero == "100": # Converte 100 para 00
        numero = "00"

    rows = read_csv()
    numero_encontrado = False
    for row in rows:
        if row["numero"] == numero:
            numero_encontrado = True
            if row["status"] == "vendido":
                return jsonify({"erro": "Número já vendido"}), 400
            row["status"] = "vendido"
            break

    if not numero_encontrado:
        return jsonify({"erro": "Número inválido"}), 400

    write_csv(rows)
    return jsonify({"msg": f"Número {numero} marcado como vendido"})

@app.route("/rifa/help", methods=["GET"])
def help():
    comandos = {
        "lista": "Mostra todos os números e seus status.",
        "vendidos": "Mostra apenas os números vendidos.",
        "disponiveis": "Mostra apenas os números disponíveis.",
        "vender <numero>": "Marca o número como vendido.",
        "desmarcar <numero>": "Marca o número como disponível novamente.",
        "valor_total": "Mostra quanto já foi arrecadado.",
        "help": "Mostra esta lista de comandos."
    }
    return jsonify(comandos)

@app.route("/rifa/vendidos", methods=["GET"])
def vendidos():
    rows = read_csv()
    vendidos_list = [row["numero"] for row in rows if row["status"] == "vendido"]
    return jsonify(vendidos_list)

@app.route("/rifa/disponiveis", methods=["GET"])
def disponiveis():
    rows = read_csv()
    disponiveis_list = [row["numero"] for row in rows if row["status"] == "disponivel"]
    return jsonify(disponiveis_list)

@app.route("/rifa/valor_total", methods=["GET"])
def valor_total():
    preco = 10  # Defina o valor de cada número aqui
    rows = read_csv()
    vendidos_count = len([row for row in rows if row["status"] == "vendido"])
    total = vendidos_count * preco
    return jsonify({"valor_total": total, "quantidade_vendida": vendidos_count, "preco_por_numero": preco})

@app.route("/rifa/desvender", methods=["POST"])
def desvender_numero():
    data = request.json
    numero = data.get("numero")
    if not numero:
        return jsonify({"erro": "Número não fornecido"}), 400
    if numero == "100": # Converte 100 para 00
        numero = "00"
    rows = read_csv()
    numero_encontrado = False
    for row in rows:
        if row["numero"] == numero:
            numero_encontrado = True
            if row["status"] == "disponivel":
                return jsonify({"erro": "Número já está disponível"}), 400
            row["status"] = "disponivel"
            break

    if not numero_encontrado:
        return jsonify({"erro": "Número inválido"}), 400

    write_csv(rows)
    return jsonify({"msg": f"Número {numero} desmarcado como vendido"})

if __name__ == "__main__":
    init_csv()
    app.run(debug=True)