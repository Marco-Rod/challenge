import sys
import json
import csv
import requests

""" Script para generar un archivo csv obteniendo los datos desde una url """


"""
Las variables JSON_FILE_URL y CSV_FILE_NAME son variables globales y podrian
contener informacion sensible, se recomienda utiliar un archivo de configuracion
para almacenar las variables.
"""
JSON_FILE_URL = 'https://storage.googleapis.com/resources-prod-shelftia/scrapers-prueba/product.json'
CSV_FILE_NAME = 'output-product.csv'


class Manager:
    def __init__(self):
        """
        Inicializamos los metodos para obtener los datos
        y generar el archivo csv con el formato correspondiente.
        Usamos el metodo get_data para hacer una peticion a la url usandp
        la libreria requests, validamos el codigo de estado y si es 200
        devolvemos el json, en caso de obtener un error por un codigo
        distinto de 200 devolvemos None.
        Luego usamos el metodo generate_csv para generar el archivo csv
        formateamos y hacemos las validaciones necesarias.
        """
        self.url = JSON_FILE_URL
        self.data = self.get_data()   
        self.properties = self.sanitized_info()
        self.attributes = self.generate_attributes()
        self.generate_csv()
        
    def get_data(self):
        """
        Metodo donde hacemos la peticion a la url usando la libreria
        requests, valaidamos con el metdo raise_for_status que nos
        devuelve un objeto de la clase Response y si el codigo de estado
        es 200 devolvemos el json, en caso contrario nos devuelve un
        mensaje de error y devolvemos None.
        aregamos una excepcion de tipo requests.exceptions.RequestException
        que nos devuelve un error de peticion.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            if response.status_code == 200:
                return response.json()
            else:
                print("Error: status code {}".format(response.status_code))
                return None
        except response.exceptions.RequestException as e:
            print("Error making request to {}: {}".format(self.url, e))
            return None
        
    def sanitized_info(self):
        """
        Generamos una nueva lista con los datos necesarios obtenidos
        desde el archivo json, accedemos al nodo "allVariants" y seleccionamos
        el primer elemento, luego accedemos al nodo "attributesRaw" y
        seleccionamos los atributos que necesitamos.
        creamos un diccionario llamado properties y almacenamos los
        datos procesados.
        validamos que es-CR este en el diccionario,
        si necesitaramos algun dato extra lo podriamos
        agredar al diccionario.
        Devolvemos el diccionario properties.
        """
        properties = dict()
        json_data = self.data["allVariants"][0]["attributesRaw"]
        for attribute in json_data:
            if attribute["name"] == "custom_attributes":
                custom_attributes = attribute["value"]
                if "es-CR" in custom_attributes:
                    es_data = json.loads(custom_attributes["es-CR"])
                    properties = es_data

        return properties
    
    def validate_keys(self, data, key):
        """
        Metodo que valida si la clave existe en el diccionario data y si es
        verdadero devuelve el valor de la clave "value" en caso contrario
        devuelve None.
        """
        result = data.get(key).get("value") if data.get(key) and "value" in data.get(key) else None
        return result


    def generate_attributes(self):
        """
        Validamos la longitud del diccionario properties y si es mayor de 0
        generamos las variables necesarias que seran procesadas en el archivo csv.
        utilizamos la funcion validate_keys para validar que la clave existe en el diccionario,
        estas variables son almacenadas en uan lista la cual devolveremos para ser manipulada
        en el metodo que genera el archivo csv.
        """
        attributes_list = list()
        if len(self.properties) > 0:
            es_allergens = [allergen["name"] for allergen in self.properties["allergens"]["value"]]
            attributes_list.append(es_allergens)
            sku = self.validate_keys(self.properties, "sku")
            attributes_list.append(sku)
            vegan = self.validate_keys(self.properties, "vegan")
            attributes_list.append(vegan)
            kosher = self.validate_keys(self.properties, "kosher")
            attributes_list.append(kosher)
            organic = self.validate_keys(self.properties, "organic")
            attributes_list.append(organic)            
            vegetarian = self.validate_keys(self.properties, "vegetarian")
            attributes_list.append(vegetarian)
            gluten_free = self.validate_keys(self.properties, "gluten_free")
            attributes_list.append(gluten_free)
            lactose_free = self.validate_keys(self.properties, "lactose_free")
            attributes_list.append(lactose_free)
            package_quantity = self.validate_keys(self.properties, "package_quantity")
            attributes_list.append(package_quantity)
            unit_size = self.validate_keys(self.properties, "unit_size")
            attributes_list.append(round(float(unit_size), 1) if unit_size else None)
            net_weight = self.validate_keys(self.properties, "net_weight")
            attributes_list.append(round(float(net_weight), 1) if net_weight else None)
            
        return attributes_list

    def generate_csv(self):
        """
        Metodo que genera el archivo csv con los datos procesados.
        agregamos los headers y los datos.
        """
        headers = [
            "allergens", "sku", "vegan", "kosher", "organic", "vegetarian",
            "gluten_free", "lactose_free", "package_quantity", "unit_size", "net_weight"
        ]

        with open (CSV_FILE_NAME, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerow(self.attributes)


if __name__ == '__main__':
    manager = Manager()
