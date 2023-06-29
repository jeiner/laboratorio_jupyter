"""
    Realizar la transformacion de un structura de datos de origen a una nueva, en cuanto a boletas  de venta OEA EDUCACION
"""
import json
import xmltodict
from time import time


class CountElapsedTime:
    def __init__(self):
        pass
        # self.param_foo = param_foo
        # self.param_bar = param_bar

    def __call__(self, func):
        def my_logic(*args, **kwargs):
            # whatever logic your decorator is supposed to implement goes in here
            start_time = time()
            # print(self.param_bar)
            # including the call to the decorated function (if you want to do that)
            result = func(*args, **kwargs)
            elapsed_time = time() - start_time
            print("Tiempo transcurrido: %0.10f segundos." % elapsed_time)
            return result

        return my_logic


def evaluate_data(data: list, tag_colum='bol_response') -> list:
    boletas_new = []
    for item in data:
        jsonload = json.loads(item[tag_colum])
        json_formate: dict = xml_to_json(jsonload['xml'])
        info: dict = build_dict(json_formate, jsonload)
        if info['estado'] is False:
            COMPANY_RUC='20545280605'
            COMPANY_RZSOCIAL='ORGANIZACION EDUCATIVA AMERICANA S.A.C.'
            COMAPANY_N_COMERCIAL='OEA Educación'
            COMAPANY_ADDRESS='Av. la Marina 4to Piso Nro. 2529, San Miguel, Lima - Perú'
            COD_TIP_NIF_EMIS='6'
            CURRENCY_MONEY='PEN',
            COMAPANY_UBIGEO=''
            token = '150101'
            request_body = {
                "TOKEN": token,
                "items": [
                    {
                        "COD_ITEM": info['codigo_producto'],
                        "MNT_BRUTO": info['gravado'],
                        "MNT_PV_ITEM": info['gravado'],
                        "MNT_IGV_ITEM": info['igv'],
                        "POR_IGV_ITEM": 18,
                        "VAL_VTA_ITEM": info['gravado'],
                        "COD_UNID_ITEM": "NIU",
                        "TXT_DESC_ITEM": info['descripcion_producto'],
                        "VAL_UNIT_ITEM": info['gravado'],
                        "CANT_UNID_ITEM": 1,
                        "COD_TIP_PRC_VTA": "01",
                        "COD_TRIB_IGV_ITEM": "1000",
                        "PRC_VTA_UNIT_ITEM": info['total'],
                        "COD_TIP_AFECT_IGV_ITEM": 10
                    }
                ],
                "COD_MND": CURRENCY_MONEY,
                "MNT_TOT": info['total'],
                "FEC_EMIS": info['fecha_emision'],
                "COD_TIP_CPE": "03",
                "RETORNA_PDF": "true",
                "COD_UBI_EMIS": COMAPANY_UBIGEO,
                "NUM_NIF_EMIS": COMPANY_RUC,
                "NUM_NIF_RECP": info['dni'],
                "TXT_VERS_UBL": "2.1",
                "COD_FORM_IMPR": "001",
                "NUM_CORRE_CPE":'',
                "NUM_SERIE_CPE":'',
                "COD_ANEXO_EMIS": "0000",
                "COD_PRCD_CARGA": "001",
                "ENVIAR_A_SUNAT": "true",
                "NOM_COMER_EMIS": COMAPANY_N_COMERCIAL,
                "MNT_TOT_GRAVADO": info['gravado'],
                "RETORNA_XML_CDR": "true",
                "COD_TIP_NIF_EMIS": COD_TIP_NIF_EMIS,
                "COD_TIP_NIF_RECP": info['tipo_doc'],
                "MNT_TOT_TRIB_IGV": info['igv'],
                "NOM_RZN_SOC_EMIS": COMPANY_RZSOCIAL,
                "NOM_RZN_SOC_RECP": info['nombres'],
                "COD_TIP_OPE_SUNAT": "0101",
                "RETORNA_XML_ENVIO": "true",
                "TXT_DMCL_FISC_EMIS": COMAPANY_ADDRESS,
                "TXT_DMCL_FISC_RECEP": 'sin descripcion',
                "TXT_VERS_ESTRUCT_UBL": "2.0"
            }
            boletas_new.append(request_body)

    return boletas_new

def build_dict(data:dict, json_formate:dict):
    total = str(data['Invoice']['cac:InvoiceLine']['cac:PricingReference']['cac:AlternativeConditionPrice']['cbc:PriceAmount']['#text'])
    neto = float(total)
    gravado = round(neto / (1 + 0.18), 2)
    igv = round(neto - gravado, 2)

    description_sunat = ''
    if json_formate.get('sunatResponse', None) is not None:
        if json_formate['sunatResponse'].get('cdrResponse', None) is not None:
            description_sunat = json_formate['sunatResponse']['cdrResponse']['description']
        elif json_formate['sunatResponse'].get('error'):
            description_sunat = json_formate['sunatResponse']['error']['message']

    status = False
    if description_sunat.find('ha sido aceptado') >=0:
        # "se encontro la frase"
        status = True
    detail = {
        "gravado": str(gravado),
        "igv": str(igv),
        "total": str(total),
        "estado": status,
        "num_correlativo" : '',
        "serie" :'',
        "dni" : data['Invoice']['cac:AccountingCustomerParty']['cac:Party']['cac:PartyIdentification']['cbc:ID']['#text'],
        "tipo_doc" : data['Invoice']['cac:AccountingCustomerParty']['cac:Party']['cac:PartyIdentification']['cbc:ID']['@schemeID'],
        "descripcion_producto" : data['Invoice']['cac:InvoiceLine']['cac:Item']['cbc:Description'],
        "codigo_producto" :  data['Invoice']['cac:InvoiceLine']['cac:Item']['cac:SellersItemIdentification']['cbc:ID'],
        "leyenda" : data['Invoice']['cbc:Note']['#text'],
        "nombres" : data['Invoice']['cac:AccountingCustomerParty']['cac:Party']['cac:PartyLegalEntity']['cbc:RegistrationName'],
        "fecha_emision" :  data['Invoice']['cbc:IssueDate'],
    }

    return detail


def xml_to_json(xml) -> dict:
    try:
        return xmltodict.parse(xml)
    except:
        raise ("No se pudo convertir el xml a Json")


def open_file_json(path) -> list:
    try:
        f = open(path , "rb")
        return json.load(f)
    except:
        raise ("No se pudo leer el archivo")


def save_json(path, data) -> None:
    # path_json_mifact = 'D:\\jeiner\\jeinercastro\\datascience\\laboratorio1\\data\\boletas_to_mifact.json'
    try:
        with open(path, 'w') as convert_file:
            convert_file.write(json.dumps(data))
    except:
        raise ("No se pudo guardar la data")

@CountElapsedTime()
def main() -> None:
    boletas_open = 'D:\\jeiner\\jeinercastro\\datascience\\laboratorio1\\data\\boletas_mayo_oficial.json'
    facturas_open = 'D:\\jeiner\\jeinercastro\\datascience\\laboratorio1\\data\\factura_mayo_2023_oficial.json'
    path_save = 'D:\\jeiner\\jeinercastro\\datascience\\laboratorio1\\data\\boletas_to_mifact.json'
    data_dict = open_file_json(facturas_open)
    list_request_body: list = evaluate_data(data=data_dict, tag_colum='fact_response')
    save_json(path_save, list_request_body)



if __name__ == '__main__':
    main()