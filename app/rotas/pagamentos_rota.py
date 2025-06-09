from flask import Blueprint, request, jsonify, send_file
from app.models.pagamento import Pagamento
from app.banco.database import db
from app.pagamentos.pix import Pix
from app.models.comanda import Comanda
from datetime import  datetime, timedelta


pagamento_rt = Blueprint('pagamento',__name__,url_prefix='/pagamento')

#criando pagamentos
@pagamento_rt.route('/', methods=['POST'])
def create_pagamento_pix():
    dado = request.get_json()
    comanda_id = dado.get('comanda_id')
    valor = dado.get('valor')

    if not comanda_id or valor is None:
        return jsonify({"message": "Campo 'valor' e 'comanda' são obrigatórios"}), 400
    
    #expiração 30min após criação
    expiration_date = datetime.now() + timedelta(minutes=30)

    novo_pagamento = Pagamento(value=valor,
                               expiration_date=expiration_date,
                               comanda_id=comanda_id
                            )
    
    pix_obj = Pix()
    dado_pagamento_pix = pix_obj.create_pagamento(valor, comanda_id)

    novo_pagamento.bank_payment_id = dado_pagamento_pix["bank_payment_id"]
    novo_pagamento.qr_code =  dado_pagamento_pix["qr_code_path"]


    db.session.add(novo_pagamento)
    db.session.commit()
    return jsonify({"message": "Pagamento criado com sucesso", 
                    "pagamento":novo_pagamento.to_dict()})



#retornando imagem 
@pagamento_rt.route('/pix/qrcode/<file_name>', methods=['GET'])
def get_img(file_name):
    return send_file(f"static/img/{file_name}.png", mimetype='image/png')


#confirmação de pagamento
@pagamento_rt.route('/confirmacao', methods=['POST'])
def pix_confirmacao():
    dado = request.get_json()
    comanda_id = dado.get('comanda_id')
    valor = dado.get('valor')

    pagamento = Pagamento.query.filter_by(comanda_id=comanda_id, value=valor, paid=False).first()

    if not pagamento:
        return jsonify({"message": "Não existe nenhum pagamento para essa comanda"}), 404

    pagamento.paid= True
    comanda = pagamento.comanda
    
    total_comanda = comanda.calcula_total()
    total_pago = sum(p.value for p in comanda.pagamentos if p.paid)

    saldo = total_comanda - total_pago

    db.session.commit()
    return jsonify({
        "message": "Pagamento confirmado com sucesso",
        "total_comanda": total_comanda,
        "total_pago": total_pago,
        "saldo_restante": saldo
    })


