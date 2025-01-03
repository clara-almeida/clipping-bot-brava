import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from raspador import get_epbr
from raspador import get_infomoney
from raspador import get_investing
from raspador import get_petronoticias
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__) # Cria uma instância do Flask. 

@app.route("/")
def raspadores():
    run_epbr = get_epbr()
    run_infomoney = get_infomoney()
    #run_investing = get_investing()
    #run_petronoticias = get_petronoticias()
    return render_template('raspadores.html')


if __name__ == "__main__":
    app.run(debug=True)
