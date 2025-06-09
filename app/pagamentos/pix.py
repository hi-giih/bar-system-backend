import os
import uuid
import qrcode


class Pix:
    def __init__(self):
        pass


    def create_pagamento(self,valor, comanda_id):
        bank_payment_id =str(uuid.uuid4())

        hash_pagamento = f'hash_pagamento_{bank_payment_id}'

        #Caminho fixo
        base_dir = os.path.dirname(os.path.abspath(__file__)) 
        img_dir = os.path.join(base_dir, '..', 'static', 'img') 
        os.makedirs(img_dir, exist_ok=True) 

        # Caminho para salvar o QR code
        file_name = f'qr_code_pagamento_{bank_payment_id}.png'
        img_path = os.path.join(img_dir, file_name)

        img = qrcode.make(hash_pagamento)


        img = qrcode.make(hash_pagamento)
        img.save(img_path)

        return {"bank_payment_id":bank_payment_id,
                "qr_code_path":f"qr_code_pagamento_{bank_payment_id}"}
    
