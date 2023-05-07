from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json
import re

app = Flask(__name__)


# funkcja do odczytywania danych z plików
def load_data():
    with open('saldo.txt', 'r') as f:
        saldo = float(f.read())
    with open('magazyn.txt', 'r') as f:
        magazyn_lines = f.readlines()
        magazyn = {}
        for line in magazyn_lines:
            split_line = line.strip().split(';')
            if len(split_line) == 3:
                produkt, ilosc, cena = split_line
                magazyn[produkt] = {"ilosc": int(ilosc), "cena": float(cena)}
            else:
                print(f"Błąd wczytywania danych z pliku 'magazyn.txt': Nieprawidłowy format wiersza: {line}")
    with open('historia.txt', 'r') as f:
        historia = [line.strip() for line in f.readlines()]
    return saldo, magazyn, historia


# funkcja do zapisywania danych do plików
def save_data(saldo, magazyn, historia):
    with open('saldo.txt', 'w') as f:
        f.write(str(saldo))
    with open('magazyn.txt', 'w') as f:
        for produkt, dane in magazyn.items():
            f.write(f'{produkt};{dane["ilosc"]};{dane["cena"]}\n')
    with open('historia.txt', 'w') as f:
        for wpis in historia:
            f.write(f'{wpis}\n')

@app.route('/')
def index():
    saldo, magazyn, _ = load_data()
    return render_template('index.html', saldo=saldo, magazyn=magazyn)

@app.route('/zakup', methods=['GET', 'POST'])
def zakup():
    if request.method == 'POST':
        nazwa = request.form['nazwa']
        cena = float(request.form['cena'])
        ilosc = int(request.form['ilosc'])
        saldo, magazyn, historia = load_data()
        if saldo >= cena * ilosc:
            saldo -= cena * ilosc
            if nazwa in magazyn:
                magazyn[nazwa] = {"ilosc": magazyn.get(nazwa, {"ilosc": 0})["ilosc"] + ilosc, "cena": cena}
            else:
                magazyn[nazwa] = {"ilosc": ilosc, "cena": cena}
            current_date = datetime.now().strftime("%Y-%m-%d")
            historia.append(f'{current_date} Zakup: {nazwa}, cena: {cena}, ilość: {ilosc}\n')
            save_data(saldo, magazyn, historia)
            return redirect(url_for('index'))
        else:
            return render_template('zakup.html', error='Brak środków na koncie')
    else:
        return render_template('zakup.html')

@app.route('/sprzedaz', methods=['POST'])
def sprzedaz():
    nazwa = request.form['nazwa']
    ilosc = int(request.form['ilosc'])
    cena = float(request.form['cena'])

    saldo, magazyn, historia = load_data()

    if nazwa in magazyn and magazyn[nazwa]['ilosc'] >= ilosc:
        magazyn[nazwa]['ilosc'] -= ilosc
        saldo += cena * ilosc
        current_date = datetime.now().strftime("%Y-%m-%d")
        historia.append(f'{current_date} Sprzedaż: {nazwa}, cena: {cena}, ilość: {ilosc}\n')
        save_data(saldo, magazyn, historia)
        return redirect(url_for('index'))
    else:
        return render_template('index.html', error='Nie można sprzedać towaru')

@app.route('/saldo', methods=['POST'])
def update_saldo():
    zmiana = float(request.form['zmiana'])
    saldo, magazyn, historia = load_data()
    saldo += zmiana
    current_date = datetime.now().strftime("%Y-%m-%d")
    historia.append(f'{current_date} Zmiana salda: {zmiana}\n')
    save_data(saldo, magazyn, historia)
    return redirect(url_for('index'))

@app.route('/historia/', defaults={'start': None, 'end': None})
@app.route('/historia/<int:start>/<int:end>')
def historia(start, end):
    _, _, historia = load_data()
    if start is not None and end is not None:
        if 0 <= start < len(historia) and 0 <= end <= len(historia):
            historia = historia[start:end]
        else:
            error_msg = f"Nieprawidłowy zakres indeksów. Możliwy zakres to od 0 do {len(historia) - 1}."
            return render_template('historia.html', error=error_msg)

    parsed_history = []
    for entry in historia:
        entry_parts = entry.split(' ', 1)
        if len(entry_parts) < 2:
            continue
        date, operation = entry_parts
        parsed_history.append({
            'data': date,
            'typ': operation.split(':')[0].strip(),
            'produkt': re.findall(r'([a-zA-Z\s]+),', operation)[0].strip() if re.findall(r'([a-zA-Z\s]+),', operation) else '',
            'ilosc': int(re.findall(r'ilość:\s(\d+)', operation)[0]) if re.findall(r'ilość:\s(\d+)', operation) else 0,
            'cena': float(re.findall(r'cena:\s([0-9.]+)', operation)[0]) if re.findall(r'cena:\s([0-9.]+)', operation) else 0
        })
    return render_template('historia.html', historia=parsed_history)


if __name__ == '__main__':
    app.run(debug=True)