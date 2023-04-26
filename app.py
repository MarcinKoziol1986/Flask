from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# funkcja do odczytywania danych z plików
def load_data():
    with open('saldo.txt', 'r') as f:
        saldo = float(f.read())
    with open('magazyn.txt', 'r') as f:
        magazyn = json.load(f)
    with open('historia.txt', 'r') as f:
        historia = f.readlines()
    return saldo, magazyn, historia

# funkcja do zapisywania danych do plików
def save_data(saldo, magazyn, historia):
    with open('saldo.txt', 'w') as f:
        f.write(str(saldo))
    with open('magazyn.txt', 'w') as f:
        json.dump(magazyn, f)
    with open('historia.txt', 'w') as f:
        f.writelines(historia)

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
                magazyn[nazwa] += ilosc
            else:
                magazyn[nazwa] = ilosc
            historia.append(f'Zakup: {nazwa}, cena: {cena}, ilość: {ilosc}\n')
            save_data(saldo, magazyn, historia)
            return redirect(url_for('index'))
        else:
            return render_template('zakup.html', error='Brak środków na koncie')
    else:
        return render_template('zakup.html')

@app.route('/sprzedaz', methods=['GET', 'POST'])
def sprzedaz():
    if request.method == 'POST':
        nazwa = request.form['nazwa']
        ilosc = int(request.form['ilosc'])
        saldo, magazyn, historia = load_data()
        if nazwa in magazyn and magazyn[nazwa] >= ilosc:
            cena = magazyn[nazwa]['cena']
            saldo += cena * ilosc
            magazyn[nazwa] -= ilosc
            historia.append(f'Sprzedaż: {nazwa}, cena: {cena}, ilość: {ilosc}\n')
            save_data(saldo, magazyn, historia)
            return redirect(url_for('index'))
        else:
            return render_template('sprzedaz.html', error='Brak produkt')
