#pip install flask flask_sqlalchemy pyodbc smtplib

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pyodbc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Configuração do banco de dados WinThor
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://username:password@servername/databasename?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Preços (ajuste conforme a estrutura do WinThor)
class PriceChange(db.Model):
    __tablename__ = 'pcprodfilial'  # Ajuste conforme sua tabela
    id = db.Column('id', db.Integer, primary_key=True)
    codprod = db.Column('codprod', db.Integer)
    custorepant = db.Column('custorepant', db.Float)  # Preço antigo
    custorep = db.Column('custorep', db.Float)  # Preço novo
    dtultaltcom = db.Column('dtultaltcom', db.DateTime)  # Data de alteração

# Função para enviar e-mails
def send_email(to_email, subject, body):
    sender_email = "your_email@example.com"
    sender_password = "your_password"

    # Configuração do servidor de e-mail (Exemplo: Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        # Configurando o e-mail
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Enviando o e-mail
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())

        print(f"E-mail enviado para {to_email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# Endpoint para buscar alterações de preços
@app.route('/price_changes', methods=['GET'])
def get_price_changes():
    try:
        # Buscando alterações recentes no banco
        changes = PriceChange.query.filter(PriceChange.dtultaltcom >= '2024-01-01').all()
        result = []
        for change in changes:
            result.append({
                'codprod': change.codprod,
                'preco_antigo': change.custorepant,
                'preco_novo': change.custorep,
                'data_alteracao': change.dtultaltcom.strftime('%Y-%m-%d %H:%M:%S')
            })

        # Enviar e-mail se houver alterações
        if result:
            body = "Alterações recentes de preços:\n\n"
            for item in result:
                body += f"Produto {item['codprod']}: de {item['preco_antigo']} para {item['preco_novo']} em {item['data_alteracao']}\n"
            send_email("destinatario@example.com", "Alterações de Preço de Compra", body)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
